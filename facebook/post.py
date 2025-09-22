import json
import requests
import os
from datetime import datetime

class FacebookPoster:
    def __init__(self, creds_file_path="creds.json"):
        """Initialize Facebook poster with credentials from JSON file"""
        self.creds_file_path = creds_file_path
        self.credentials = self._load_credentials()
        self.page_id = self.credentials.get("page_id")
        self.page_access_token = self.credentials.get("page_access_token")
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def _load_credentials(self):
        """Load Facebook credentials from JSON file"""
        try:
            with open(self.creds_file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Credentials file {self.creds_file_path} not found")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.creds_file_path}")
            return {}
    
    def post_text(self, message):
        """Post a text message to Facebook page"""
        if not self.page_id or not self.page_access_token:
            print("Error: Missing page_id or page_access_token")
            return False
        
        url = f"{self.base_url}/{self.page_id}/feed"
        
        payload = {
            "message": message,
            "access_token": self.page_access_token
        }
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            if "id" in result:
                print(f"Successfully posted to Facebook! Post ID: {result['id']}")
                return True
            else:
                print(f"Error posting to Facebook: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            # Try to get more details about the error
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    print(f"Error details: {error_details}")
                except:
                    print(f"Response text: {e.response.text}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return False
    
    def post_with_image(self, message, image_path):
        """Post a message with an image to Facebook page"""
        if not self.page_id or not self.page_access_token:
            print("Error: Missing page_id or page_access_token")
            return False
        
        if not os.path.exists(image_path):
            print(f"Error: Image file {image_path} not found")
            return False
        
        url = f"{self.base_url}/{self.page_id}/photos"
        
        payload = {
            "message": message,
            "access_token": self.page_access_token
        }
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'source': image_file}
                response = requests.post(url, data=payload, files=files)
                response.raise_for_status()
                
                result = response.json()
                if "id" in result:
                    print(f"Successfully posted image to Facebook! Post ID: {result['id']}")
                    return True
                else:
                    print(f"Error posting image to Facebook: {result}")
                    return False
                    
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return False
        except FileNotFoundError as e:
            print(f"File error: {e}")
            return False
    
    def check_token_permissions(self):
        """Check what permissions the current access token has"""
        url = "https://graph.facebook.com/me/permissions"
        params = {
            "access_token": self.page_access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            print("Current token permissions:")
            for permission in result.get('data', []):
                status = permission.get('status', 'unknown')
                perm_name = permission.get('permission', 'unknown')
                print(f"  {perm_name}: {status}")
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"Error checking permissions: {e}")
            return None

    def get_page_info(self):
        """Get basic information about the Facebook page"""
        if not self.page_id or not self.page_access_token:
            print("Error: Missing page_id or page_access_token")
            return None
        
        url = f"{self.base_url}/{self.page_id}"
        params = {
            "fields": "name,about,fan_count,followers_count",
            "access_token": self.page_access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting page info: {e}")
            return None

def main():
    """Example usage of FacebookPoster class"""
    poster = FacebookPoster()
    
    # Check token permissions first
    print("Checking access token permissions...")
    poster.check_token_permissions()
    print()
    
    # Example 1: Post a simple text message
    message = f"Hello from web! 🧘‍♀️ Today is {datetime.now().strftime('%B %d, %Y')}. We're here to help you on your journey to holistic health and well-being. #wellness #meditation #holistichealth"
    
    print("Posting text message to Facebook...")
    success = poster.post_text(message)
    
    if success:
        print("✅ Text post successful!")
    else:
        print("❌ Text post failed!")
    
    # Example 2: Post with an image (if available)
    # Commenting out image posting for now due to missing image file
    print("\nSkipping image post example (no image file configured).")
    
    # Example 3: Get page information
    print("\nGetting page information...")
    page_info = poster.get_page_info()
    if page_info:
        print(f"Page Name: {page_info.get('name', 'N/A')}")
        print(f"About: {page_info.get('about', 'N/A')}")
        print(f"Fans: {page_info.get('fan_count', 'N/A')}")
        print(f"Followers: {page_info.get('followers_count', 'N/A')}")
    
    # Example 4: Check token permissions
    print("\nChecking token permissions...")
    permissions = poster.check_token_permissions()
    if permissions:
        print("Permissions checked successfully.")
    else:
        print("Failed to check permissions.")

if __name__ == "__main__":
    main()
