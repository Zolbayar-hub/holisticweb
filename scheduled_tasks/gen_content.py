#!/usr/bin/env python3
"""
Scheduled task to generate content and images for social media posting.
This script generates text content first, then creates matching images.
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Add the parent directory to the Python path to import our models
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask
from db import db
from db.models import GeneratedContent
from openai import OpenAI

class ContentGenerator:
    def __init__(self):
        """Initialize the content generator with OpenAI credentials."""
        # Load API credentials
        self.api_key_file = os.path.join(os.path.dirname(__file__), "api_key.json")
        self.api_key = self._load_api_key()
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key["api_key"])
        else:
            self.client = None
    
    def _load_api_key(self):
        """Load OpenAI API key from JSON file."""
        try:
            with open(self.api_key_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: API key file not found: {self.api_key_file}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in API key file: {self.api_key_file}")
            return None
    
    def get_response(self, prompt):
        """
        Get response from OpenAI API.
        
        Args:
            prompt (str): The prompt to send to OpenAI
            
        Returns:
            str: Generated response text
        """
        if not self.client:
            print("OpenAI client not initialized.")
            return None
            
        try:
            response = self.client.responses.create(
                model="gpt-4.1",
                input=f"{prompt}"
            )
            return response.output_text
        except Exception as e:
            print(f"Error getting OpenAI response: {e}")
            return None
    
    def gen_text(self, topic, custom_prompt=None):
        """
        Generate text content for a given topic.
        
        Args:
            topic (str): The topic to generate content about
            custom_prompt (str, optional): Custom prompt, otherwise uses default
            
        Returns:
            int: ID of the created GeneratedContent record, or None if failed
        """
        if not self.client:
            print("Cannot generate text - OpenAI client not available.")
            return None
        
        # Use custom prompt or default
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = f"""
            Create an engaging, educational social media post about {topic}.
            
            Requirements:
            - Keep it under 250 characters for social media
            - Make it informative and practical
            - Include key insights or tips
            - Use a professional yet accessible tone
            - Don't use hashtags (we'll add them separately)
            
            Topic: {topic}
            """
        
        print(f"Generating text content for topic: {topic}")
        content = self.get_response(prompt)
        
        if not content:
            print(f"Failed to generate content for topic: {topic}")
            return None
        
        # Create new GeneratedContent record
        try:
            gen_content = GeneratedContent(
                topic=topic,
                content=content.strip(),
                image_url=None,  # Will be updated in step 2
                posted=False,
                posted_at=None
            )
            
            db.session.add(gen_content)
            db.session.commit()
            
            print(f"✅ Text content generated and saved (ID: {gen_content.id})")
            print(f"Content preview: {content[:100]}...")
            
            return gen_content.id
            
        except Exception as e:
            print(f"Error saving generated content: {e}")
            db.session.rollback()
            return None
    
    def gen_image(self, content_id):
        """
        Generate an image for existing content and update the record.
        
        Args:
            content_id (int): ID of the GeneratedContent record to update
            
        Returns:
            bool: True if successful, False if failed
        """
        if not self.client:
            print("Cannot generate image - OpenAI client not available.")
            return False
        
        # Get the content record
        try:
            content_record = GeneratedContent.query.get(content_id)
            if not content_record:
                print(f"Content record not found: {content_id}")
                return False
        except Exception as e:
            print(f"Error retrieving content record: {e}")
            return False
        
        topic = content_record.topic
        content_text = content_record.content
        
        # Create image generation prompt
        image_prompt = f"""
        Create a professional, educational image for a social media post about {topic}.
        
        The post content is: "{content_text}"
        
        Requirements:
        - Professional, clean design suitable for LinkedIn/Twitter
        - Educational/informative style
        - Include relevant icons or visual elements
        - Readable text if any
        - Modern, tech-focused aesthetic
        - High contrast and clarity
        - Suitable for social media sharing
        
        Topic focus: {topic}
        """
        
        print(f"Generating image for content ID: {content_id}, topic: {topic}")
        
        try:
            # Generate image using DALL-E
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                n=1,
                size="1024x1024",
                quality="standard"
            )
            
            image_url = response.data[0].url
            print(f"✅ Image generated: {image_url}")
            
            # Download and save the image locally
            image_filename = f"{topic.replace(' ', '_').replace('/', '_')}.png"
            local_image_path = self._download_and_save_image(image_url, image_filename)
            
            if local_image_path:
                # Update the content record with the local image path
                content_record.image_url = local_image_path
                db.session.commit()
                
                print(f"✅ Image saved and content updated: {local_image_path}")
                return True
            else:
                print("Failed to save image locally")
                return False
                
        except Exception as e:
            print(f"Error generating image: {e}")
            return False
    
    def _download_and_save_image(self, image_url, filename):
        """
        Download image from URL and save locally.
        
        Args:
            image_url (str): URL of the image to download
            filename (str): Filename to save as
            
        Returns:
            str: Local path of saved image, or None if failed
        """
        try:
            # Create static/images directory if it doesn't exist
            images_dir = os.path.join(os.path.dirname(__file__), "../static/images")
            os.makedirs(images_dir, exist_ok=True)
            
            # Download the image
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                image_path = os.path.join(images_dir, filename)
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                # Return just the filename for database storage
                return filename
            else:
                print(f"Failed to download image. Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error downloading/saving image: {e}")
            return None

def setup_app():
    """Setup Flask app context for database access."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
        os.path.dirname(__file__), '..', 'instance', 'data.sqlite'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def main():
    """Main function to demonstrate content generation."""
    print(f"Starting content generation process at {datetime.now()}")
    
    # Setup Flask app context
    app = setup_app()
    
    with app.app_context():
        generator = ContentGenerator()
        
        # Example: Generate content for a topic
        topic = "SQL Inner Join"
        
        # Step 1: Generate text content
        content_id = generator.gen_text(topic)
        
        if content_id:
            # Step 2: Generate image for the content
            success = generator.gen_image(content_id)
            
            if success:
                print(f"🎉 Complete content generated for '{topic}' (ID: {content_id})")
            else:
                print(f"⚠️ Text generated but image failed for '{topic}' (ID: {content_id})")
        else:
            print(f"❌ Failed to generate content for '{topic}'")

if __name__ == "__main__":
    main()
