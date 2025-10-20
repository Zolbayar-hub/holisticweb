#!/usr/bin/env python3
"""
Script to fix file upload permissions and directory structure for PythonAnywhere deployment
Run this script on PythonAnywhere after deployment to ensure proper permissions.
"""

import os
import stat
from app_factory import create_app
from db.models import SiteSetting

def fix_upload_permissions():
    """Fix upload directory permissions and structure"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing upload permissions and directory structure...")
        
        # Get static folder path
        static_folder = app.static_folder
        print(f"📁 Static folder: {static_folder}")
        
        # Directories to create/fix
        directories = [
            os.path.join(static_folder, 'uploads'),
            os.path.join(static_folder, 'uploads', 'home'),
            os.path.join(static_folder, 'uploads', 'services'),
            os.path.join(static_folder, 'uploads', 'about_images')
        ]
        
        for directory in directories:
            try:
                # Create directory if it doesn't exist
                os.makedirs(directory, mode=0o755, exist_ok=True)
                print(f"✅ Created/verified directory: {directory}")
                
                # Set proper permissions
                os.chmod(directory, 0o755)
                print(f"🔒 Set permissions 755 for: {directory}")
                
                # List files in directory and fix their permissions
                if os.path.exists(directory):
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            try:
                                os.chmod(file_path, 0o644)
                                print(f"🔒 Set file permissions 644 for: {file_path}")
                            except Exception as e:
                                print(f"⚠️  Could not set permissions for {file_path}: {e}")
                
            except Exception as e:
                print(f"❌ Error with directory {directory}: {e}")
        
        # Check current home_image settings and verify files exist
        print("\n📋 Checking current home_image settings...")
        try:
            home_settings = SiteSetting.query.filter_by(key='home_image').all()
            for setting in home_settings:
                print(f"🌐 Language: {setting.language}")
                print(f"   Value: {setting.value}")
                
                if setting.value:
                    file_path = os.path.join(static_folder, setting.value)
                    exists = os.path.exists(file_path)
                    print(f"   File exists: {exists}")
                    
                    if exists:
                        try:
                            permissions = oct(os.stat(file_path).st_mode)[-3:]
                            print(f"   Permissions: {permissions}")
                        except Exception as e:
                            print(f"   Permission check error: {e}")
                    else:
                        print(f"   ⚠️  File not found: {file_path}")
        except Exception as e:
            print(f"❌ Error checking home_image settings: {e}")
        
        print("\n✨ Permission fix complete!")
        print("\n💡 Additional PythonAnywhere setup tips:")
        print("1. Make sure your static files are being served correctly")
        print("2. Check that STATIC_URL_PATH is configured properly in your Flask app")
        print("3. Verify that your web app's static files mapping is correct")
        print("4. Test the debug route: /web_admin/debug/file-system")

if __name__ == '__main__':
    fix_upload_permissions()
