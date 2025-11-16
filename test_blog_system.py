#!/usr/bin/env python3
"""
Quick test to validate blog system functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from features.blog.blog import load_blog_data, BLOG_CATEGORIES

def test_blog_system():
    print("🧪 Testing Blog System...")
    
    # Test JSON loading
    try:
        data = load_blog_data()
        posts = data.get('posts', [])
        print(f"✅ JSON loaded successfully! Found {len(posts)} posts:")
        
        for post in posts:
            title = post.get('title', 'Unknown')
            category = post.get('category', 'unknown')
            slug = post.get('slug', 'no-slug')
            print(f"   📝 {title}")
            print(f"      Category: {category}")
            print(f"      Slug: {slug}")
            print(f"      Published: {post.get('published', False)}")
            print()
            
        # Test categories
        print("🗂️ Available Categories:")
        for key, info in BLOG_CATEGORIES.items():
            print(f"   {info['icon']} {info['name']} ({key})")
            
        # Validate post categories
        print("🔍 Category Validation:")
        for post in posts:
            category = post.get('category')
            if category in BLOG_CATEGORIES:
                print(f"   ✅ {post['title']} -> {category} (valid)")
            else:
                print(f"   ❌ {post['title']} -> {category} (invalid category!)")
                
        print("\n🎉 Blog system test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_blog_system()
