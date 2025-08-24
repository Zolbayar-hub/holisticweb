import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from requests_oauthlib import OAuth1Session

# Add the parent directory to the Python path to import our models
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask
from db import db
from db.models import GeneratedContent

class XPoster:
    def __init__(self, creds_file='creds.json'):
        """Initialize the X poster with credentials from JSON file."""
        self.creds_file = os.path.join(os.path.dirname(__file__), creds_file)
        self.credentials = self._load_credentials()

    def _load_credentials(self):
        """Load X API credentials from JSON file."""
        print(f"Looking for credentials file: {self.creds_file}")

        try:
            with open(self.creds_file, 'r') as f:
                creds = json.load(f)
                print(f"Credentials loaded successfully. Keys found: {list(creds.keys())}")
                return creds
        except FileNotFoundError:
            print(f"Error: Credentials file '{self.creds_file}' not found.")
            print("Please create creds.json with your X API credentials.")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in credentials file '{self.creds_file}'")
            return None

    def upload_media(self, media_path):
        """
        Upload an image or video to Twitter's media upload endpoint.

        Args:
            media_path (str): Local path to the media file (image or video)

        Returns:
            str: media_id if successful, None if failed
        """
        if not self.credentials:
            print("No credentials available for media upload.")
            return None

        # Check if it's a video file
        file_extension = os.path.splitext(media_path)[1].lower()
        is_video = file_extension in ['.mp4', '.mov', '.avi']

        # Create OAuth1Session
        oauth = OAuth1Session(
            self.credentials['consumer_key'],
            client_secret=self.credentials['consumer_secret'],
            resource_owner_key=self.credentials['access_token'],
            resource_owner_secret=self.credentials['access_token_secret'],
        )

        try:
            if is_video:
                # For videos, we need to use chunked upload
                return self._upload_video_chunked(oauth, media_path)
            else:
                # For images, use simple upload
                with open(media_path, 'rb') as media_file:
                    files = {'media': media_file}
                    response = oauth.post("https://upload.twitter.com/1.1/media/upload.json", files=files)

                    if response.status_code == 200:
                        media_data = response.json()
                        media_id = media_data.get('media_id_string')
                        print(f"✅ Media uploaded successfully. Media ID: {media_id}")
                        return media_id
                    else:
                        print(f"❌ Failed to upload media. Status: {response.status_code}")
                        print(f"Response: {response.text}")
                        return None

        except FileNotFoundError:
            print(f"❌ Media file not found: {media_path}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error uploading media: {e}")
            return None

    def _upload_video_chunked(self, oauth, video_path):
        """
        Upload a video using Twitter's chunked upload process.
        
        Args:
            oauth: OAuth1Session object
            video_path: Path to the video file
            
        Returns:
            str: media_id if successful, None if failed
        """
        try:
            # Get file size
            file_size = os.path.getsize(video_path)
            
            # Step 1: Initialize upload
            init_data = {
                'command': 'INIT',
                'media_type': 'video/mp4',
                'total_bytes': file_size
            }
            
            response = oauth.post("https://upload.twitter.com/1.1/media/upload.json", data=init_data)
            if response.status_code != 202:
                print(f"❌ Failed to initialize video upload. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
            media_id = response.json()['media_id_string']
            print(f"📹 Video upload initialized. Media ID: {media_id}")
            
            # Step 2: Upload chunks
            chunk_size = 1024 * 1024  # 1MB chunks
            segment_index = 0
            
            with open(video_path, 'rb') as video_file:
                while True:
                    chunk = video_file.read(chunk_size)
                    if not chunk:
                        break
                        
                    append_data = {
                        'command': 'APPEND',
                        'media_id': media_id,
                        'segment_index': segment_index
                    }
                    
                    files = {'media': chunk}
                    response = oauth.post("https://upload.twitter.com/1.1/media/upload.json", 
                                        data=append_data, files=files)
                    
                    if response.status_code != 204:
                        print(f"❌ Failed to upload chunk {segment_index}. Status: {response.status_code}")
                        print(f"Response: {response.text}")
                        return None
                    
                    segment_index += 1
                    print(f"📤 Uploaded chunk {segment_index}")
            
            # Step 3: Finalize upload
            finalize_data = {
                'command': 'FINALIZE',
                'media_id': media_id
            }
            
            response = oauth.post("https://upload.twitter.com/1.1/media/upload.json", data=finalize_data)
            if response.status_code not in [200, 201]:
                print(f"❌ Failed to finalize video upload. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None
            
            response_data = response.json()
            
            # Check if video is being processed
            if 'processing_info' in response_data:
                processing_info = response_data['processing_info']
                state = processing_info.get('state')
                
                if state == 'pending':
                    print(f"📹 Video is being processed by Twitter...")
                    # Wait for processing to complete
                    if self._wait_for_video_processing(oauth, media_id):
                        print(f"✅ Video processed successfully. Media ID: {media_id}")
                        return media_id
                    else:
                        print(f"❌ Video processing failed or timed out.")
                        return None
                elif state == 'succeeded':
                    print(f"✅ Video processed successfully. Media ID: {media_id}")
                    return media_id
                elif state == 'failed':
                    print(f"❌ Video processing failed.")
                    return None
            
            print(f"✅ Video uploaded successfully. Media ID: {media_id}")
            return media_id
            
        except Exception as e:
            print(f"❌ Error during chunked video upload: {e}")
            return None

    def _wait_for_video_processing(self, oauth, media_id, max_wait_time=300):
        """
        Wait for video processing to complete by checking status.
        
        Args:
            oauth: OAuth1Session object
            media_id: Media ID to check
            max_wait_time: Maximum time to wait in seconds (default 5 minutes)
            
        Returns:
            bool: True if processing succeeded, False if failed or timed out
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Check status
                status_data = {
                    'command': 'STATUS',
                    'media_id': media_id
                }
                
                response = oauth.get("https://upload.twitter.com/1.1/media/upload.json", params=status_data)
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if 'processing_info' in response_data:
                        processing_info = response_data['processing_info']
                        state = processing_info.get('state')
                        progress = processing_info.get('progress_percent', 0)
                        
                        print(f"📹 Processing status: {state} ({progress}%)")
                        
                        if state == 'succeeded':
                            return True
                        elif state == 'failed':
                            error = processing_info.get('error', {})
                            print(f"❌ Processing failed: {error}")
                            return False
                        elif state == 'pending' or state == 'in_progress':
                            # Wait before checking again
                            check_after = processing_info.get('check_after_secs', 5)
                            print(f"⏳ Waiting {check_after} seconds before next check...")
                            time.sleep(check_after)
                        else:
                            print(f"❓ Unknown processing state: {state}")
                            time.sleep(5)
                    else:
                        # No processing info, assume it's ready
                        return True
                else:
                    print(f"❌ Failed to check status. Status: {response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"❌ Error checking video status: {e}")
                time.sleep(5)
        
        print(f"⏰ Video processing timed out after {max_wait_time} seconds")
        return False

    def download_media_from_url(self, media_filename, local_path):
        """
        Copy a media file (image or video) from the static/images directory to a local temp file.

        Args:
            media_filename (str): Filename of the media (e.g., 'data_salary.jpg' or 'video.mp4')
            local_path (str): Local path where to save the media file

        Returns:
            bool: True if successful, False if failed
        """
        try:
            # Construct the full path to the media in static/images
            static_images_dir = os.path.join(os.path.dirname(__file__), "../static/images")
            source_media_path = os.path.join(static_images_dir, media_filename)

            print(f"Copying media from: {source_media_path}")

            # Check if source file exists
            if not os.path.exists(source_media_path):
                print(f"❌ Source media file not found: {source_media_path}")
                return False

            # Copy the file
            import shutil
            shutil.copy2(source_media_path, local_path)
            print(f"✅ Media copied to: {local_path}")
            return True

        except Exception as e:
            print(f"❌ Error copying media: {e}")
            return False

    def post_to_x(self, content, image_url=None):
        """
        Post content to X using the API with OAuth1Session authentication.

        Args:
            content (str): The text content to post
            image_url (str, optional): URL of image to include in post

        Returns:
            dict: API response or None if failed
        """
        if not self.credentials:
            print("No credentials available for posting.")
            return None

        # Create OAuth1Session
        oauth = OAuth1Session(
            self.credentials['consumer_key'],
            client_secret=self.credentials['consumer_secret'],
            resource_owner_key=self.credentials['access_token'],
            resource_owner_secret=self.credentials['access_token_secret'],
        )

        # Handle media upload if provided
        media_id = None
        if image_url:
            print(f"Processing media: {image_url}")

            # Create temp directory for downloaded media
            temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            # Get file extension to preserve it in temp file
            file_extension = os.path.splitext(image_url)[1]
            if not file_extension:
                # Default to .png if no extension
                file_extension = '.png'
            
            # Copy media locally first (image_url is now just the filename)
            temp_media_path = os.path.join(temp_dir, f'temp_media{file_extension}')

            if self.download_media_from_url(image_url, temp_media_path):
                # Upload media to Twitter
                media_id = self.upload_media(temp_media_path)

                # Clean up temp file
                try:
                    os.remove(temp_media_path)
                except:
                    pass

                if media_id:
                    print(f"✅ Media will be included in tweet")
                else:
                    print(f"⚠️ Will post without media due to upload failure")
            else:
                print(f"⚠️ Will post without media due to media copy failure")

        # Prepare tweet payload
        payload = {"text": content}  # Twitter character limit
        if media_id:
            payload["media"] = {"media_ids": [media_id]}

        print(f"Posting to X API: https://api.twitter.com/2/tweets")
        print(f"Tweet payload: {payload}")

        try:
            # Making the request to post the tweet
            response = oauth.post(
                "https://api.twitter.com/2/tweets",
                json=payload,
            )

            print(f"API Response Status: {response.status_code}")

            # Check if the request was successful
            if response.status_code == 201:
                print("✅ Successfully posted to X!")
                json_response = response.json()
                print(f"Tweet ID: {json_response.get('data', {}).get('id')}")
                return json_response
            else:
                print(f"❌ Failed to post to X. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error posting to X: {e}")
            return None

    def repost_tweet(self, tweet_id):
        """
        Repost (retweet) an existing tweet using the Twitter API.

        Args:
            tweet_id (str): The ID of the tweet to repost

        Returns:
            dict: API response or None if failed
        """
        if not self.credentials:
            print("No credentials available for reposting.")
            return None

        # Create OAuth1Session
        oauth = OAuth1Session(
            self.credentials['consumer_key'],
            client_secret=self.credentials['consumer_secret'],
            resource_owner_key=self.credentials['access_token'],
            resource_owner_secret=self.credentials['access_token_secret'],
        )

        print(f"Reposting tweet ID: {tweet_id}")

        try:
            # Get user ID first (needed for repost endpoint)
            user_response = oauth.get("https://api.twitter.com/2/users/me")
            if user_response.status_code != 200:
                print(f"❌ Failed to get user info. Status: {user_response.status_code}")
                return None
            
            user_id = user_response.json()['data']['id']
            
            # Repost the tweet
            response = oauth.post(
                f"https://api.twitter.com/2/users/{user_id}/retweets",
                json={"tweet_id": tweet_id}
            )

            print(f"Repost API Response Status: {response.status_code}")

            if response.status_code == 200:
                print("✅ Successfully reposted tweet!")
                json_response = response.json()
                return json_response
            else:
                print(f"❌ Failed to repost tweet. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error reposting tweet: {e}")
            return None

    def unrepost_tweet(self, tweet_id):
        """
        Remove repost (unretweet) of an existing tweet using the Twitter API.

        Args:
            tweet_id (str): The ID of the tweet to unrepost

        Returns:
            dict: API response or None if failed
        """
        if not self.credentials:
            print("No credentials available for unreposting.")
            return None

        # Create OAuth1Session
        oauth = OAuth1Session(
            self.credentials['consumer_key'],
            client_secret=self.credentials['consumer_secret'],
            resource_owner_key=self.credentials['access_token'],
            resource_owner_secret=self.credentials['access_token_secret'],
        )

        print(f"Removing repost for tweet ID: {tweet_id}")

        try:
            # Get user ID first (needed for unrepost endpoint)
            user_response = oauth.get("https://api.twitter.com/2/users/me")
            if user_response.status_code != 200:
                print(f"❌ Failed to get user info. Status: {user_response.status_code}")
                return None
            
            user_id = user_response.json()['data']['id']
            
            # Remove repost
            response = oauth.delete(
                f"https://api.twitter.com/2/users/{user_id}/retweets/{tweet_id}"
            )

            print(f"Unrepost API Response Status: {response.status_code}")

            if response.status_code == 200:
                print("✅ Successfully removed repost!")
                json_response = response.json()
                return json_response
            else:
                print(f"❌ Failed to remove repost. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error removing repost: {e}")
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

def get_latest_unposted_content():
    """Get the latest unposted content from the database."""
    try:
        content = db.session.query(GeneratedContent).filter_by(
            posted=False
        ).order_by(
            GeneratedContent.created_at.asc()
        ).first()

        return content
    except Exception as e:
        print(f"Error querying database: {e}")
        return None

def get_last_posted_content():
    """Get the most recently posted content that has a Twitter ID."""
    try:
        content = db.session.query(GeneratedContent).filter(
            GeneratedContent.posted == True,
            GeneratedContent.twitter_id.isnot(None)
        ).order_by(
            GeneratedContent.posted_at.desc()
        ).first()

        return content
    except Exception as e:
        print(f"Error querying last posted content: {e}")
        return None

def mark_as_posted(content_id, twitter_id=None):
    """Mark content as posted in the database."""
    try:
        content = db.session.get(GeneratedContent, content_id)
        if content:
            content.posted = True
            content.posted_at = datetime.utcnow()
            if twitter_id:
                content.twitter_id = twitter_id
            db.session.commit()
            print(f"Marked content ID {content_id} as posted with Twitter ID: {twitter_id}")
        else:
            print(f"Content ID {content_id} not found.")
    except Exception as e:
        print(f"Error updating database: {e}")
        db.session.rollback()

def mark_as_reposted(content_id):
    """Mark content as reposted in the database."""
    try:
        content = db.session.get(GeneratedContent, content_id)
        if content:
            content.is_reposted = True
            content.reposted_at = datetime.utcnow()
            db.session.commit()
            print(f"Marked content ID {content_id} as reposted.")
        else:
            print(f"Content ID {content_id} not found.")
    except Exception as e:
        print(f"Error updating repost status: {e}")
        db.session.rollback()

def mark_as_unreposted(content_id):
    """Mark content as unreposted in the database."""
    try:
        content = db.session.get(GeneratedContent, content_id)
        if content:
            content.is_reposted = False
            content.reposted_at = None
            db.session.commit()
            print(f"Marked content ID {content_id} as unreposted.")
        else:
            print(f"Content ID {content_id} not found.")
    except Exception as e:
        print(f"Error updating unrepost status: {e}")
        db.session.rollback()

def main():
    """Main function to run the posting process."""
    print(f"Starting X posting process at {datetime.now()}")

    # Setup Flask app context
    app = setup_app()

    with app.app_context():
        # Get latest unposted content
        content = get_latest_unposted_content()

        # Initialize X poster
        poster = XPoster()

        # Check if credentials were loaded successfully
        if not poster.credentials:
            print("❌ Failed to load credentials. Cannot proceed with posting.")
            return

        if content:
            # Found new content to post
            print(f"Found content to post: '{content.topic}' (ID: {content.id})")

            # Prepare content for posting
            post_text = f"{content.content}"

            print(f"Attempting to post content (length: {len(post_text)} chars)")
            print(f"Post preview: {post_text[:100]}...")

            # Try to post to X
            result = poster.post_to_x(post_text, content.image_url)

            if result:
                # Extract Twitter ID from response
                twitter_id = result.get('data', {}).get('id')
                # Mark as posted if successful
                mark_as_posted(content.id, twitter_id)
                print("✅ Content posted successfully!")
            else:
                print("❌ Failed to post content.")
        else:
            # No new content found, try repost logic
            print("No unposted content found. Checking for repost options...")
            
            last_posted = get_last_posted_content()
            
            if not last_posted:
                print("❌ No previously posted content found with Twitter ID.")
                return
            
            if not last_posted.twitter_id:
                print("❌ Last posted content has no Twitter ID.")
                return
            
            print(f"Last posted content: '{last_posted.topic}' (ID: {last_posted.id})")
            print(f"Twitter ID: {last_posted.twitter_id}")
            print(f"Currently reposted: {last_posted.is_reposted}")
            
            if not last_posted.is_reposted:
                # Repost the last tweet
                print("🔄 Reposting last tweet...")
                result = poster.repost_tweet(last_posted.twitter_id)
                
                if result:
                    mark_as_reposted(last_posted.id)
                    print("✅ Successfully reposted last tweet!")
                else:
                    print("❌ Failed to repost last tweet.")
            else:
                # Unrepost the last tweet
                print("↩️ Removing repost of last tweet...")
                result = poster.unrepost_tweet(last_posted.twitter_id)
                
                if result:
                    mark_as_unreposted(last_posted.id)
                    print("✅ Successfully removed repost of last tweet!")
                else:
                    print("❌ Failed to remove repost of last tweet.")

if __name__ == "__main__":
    main()
