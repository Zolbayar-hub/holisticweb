#!/usr/bin/env python3
"""
Quick test script to check blog feature static URLs
"""

import sys
import os
sys.path.append('/Users/zoloo/project_v2/website/holisticweb_new')

try:
    from flask_app import app
    
    print("✅ Flask app imported successfully")
    
    with app.app_context():
        # Test URL generation for blog static files
        from flask import url_for
        
        print("\n📁 Testing Blog Static URLs:")
        
        try:
            css_url = url_for('blog.static', filename='blog.css')
            print(f"   CSS: {css_url}")
            
            js_url = url_for('blog.static', filename='blog.js')
            print(f"   JS: {js_url}")
            
            img_url = url_for('blog.static', filename='images/default-post.jpg')
            print(f"   Default Image: {img_url}")
            
            print("\n✅ All static URLs generated successfully!")
            
        except Exception as e:
            print(f"❌ Error generating static URLs: {e}")
            
        # Test blog routes
        print("\n🌐 Testing Blog Routes:")
        try:
            blog_url = url_for('blog.index')
            print(f"   Blog Index: {blog_url}")
            
            post_url = url_for('blog.post', slug='ai-transforming-wellness-2025')
            print(f"   Blog Post: {post_url}")
            
            print("\n✅ All blog routes generated successfully!")
            
        except Exception as e:
            print(f"❌ Error generating blog routes: {e}")
            
        # List registered blueprints
        print(f"\n📋 Registered Blueprints: {list(app.blueprints.keys())}")
        
        # Check if blog blueprint is registered
        if 'blog' in app.blueprints:
            blog_bp = app.blueprints['blog']
            print(f"\n📝 Blog Blueprint Details:")
            print(f"   URL Prefix: {blog_bp.url_prefix}")
            print(f"   Static Folder: {blog_bp.static_folder}")
            print(f"   Static URL Path: {blog_bp.static_url_path}")
            print(f"   Template Folder: {blog_bp.template_folder}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
