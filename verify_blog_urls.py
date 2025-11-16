#!/usr/bin/env python3
"""
Blog Static URL Verification
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_blog_urls():
    try:
        from app_factory import create_app
        app = create_app()
        
        print("🌐 Testing Blog Static URLs...")
        
        with app.app_context():
            from flask import url_for
            
            # Test static file URLs
            css_url = url_for('blog.static', filename='blog.css')
            js_url = url_for('blog.static', filename='blog.js') 
            img_url = url_for('blog.static', filename='images/default-post.jpg')
            
            print(f"CSS URL: {css_url}")
            print(f"JS URL: {js_url}")
            print(f"Image URL: {img_url}")
            
            # Verify no double /blog/ in URLs
            if '/blog/blog/' in img_url:
                print("❌ Double /blog/ path detected!")
                return False
            else:
                print("✅ Static URLs are correctly configured")
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_blog_urls()
    exit(0 if success else 1)
