#!/usr/bin/env python3
"""
Blog Management Utility
Easily add, edit, and manage blog posts for the Serenity Wellness Studio blog
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

BLOG_DATA_FILE = 'blog_data.json'

def load_blog_data() -> Dict:
    """Load blog posts from JSON file"""
    if os.path.exists(BLOG_DATA_FILE):
        with open(BLOG_DATA_FILE, 'r') as f:
            return json.load(f)
    return {"posts": []}

def save_blog_data(data: Dict) -> None:
    """Save blog posts to JSON file"""
    with open(BLOG_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_post_id(data: Dict) -> int:
    """Get the next available post ID"""
    if not data.get('posts'):
        return 1
    return max(post['id'] for post in data['posts']) + 1

def create_slug(title: str) -> str:
    """Create a URL-friendly slug from title"""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug.strip('-')

def add_blog_post(
    title: str,
    content: str,
    category: str,
    excerpt: str,
    author: str = "Serenity Wellness Team",
    tags: List[str] = None,
    featured_image: str = "default-post.jpg",
    read_time: int = 5,
    published: bool = True
) -> Dict:
    """Add a new blog post"""
    
    data = load_blog_data()
    
    new_post = {
        "id": get_next_post_id(data),
        "title": title,
        "slug": create_slug(title),
        "category": category,
        "excerpt": excerpt,
        "content": content,
        "author": author,
        "published_date": datetime.now().strftime("%Y-%m-%d"),
        "tags": tags or [],
        "featured_image": featured_image,
        "read_time": read_time,
        "published": published
    }
    
    data['posts'].append(new_post)
    save_blog_data(data)
    
    print(f"✅ Blog post '{title}' added successfully!")
    print(f"   Slug: {new_post['slug']}")
    print(f"   URL: /blog/post/{new_post['slug']}")
    
    return new_post

def list_blog_posts() -> None:
    """List all blog posts"""
    data = load_blog_data()
    
    if not data.get('posts'):
        print("No blog posts found.")
        return
    
    print("\n📚 Blog Posts:")
    print("=" * 60)
    
    for post in data['posts']:
        status = "✅ Published" if post.get('published', False) else "❌ Draft"
        print(f"ID: {post['id']}")
        print(f"Title: {post['title']}")
        print(f"Slug: {post['slug']}")
        print(f"Category: {post['category']}")
        print(f"Author: {post['author']}")
        print(f"Date: {post['published_date']}")
        print(f"Status: {status}")
        print(f"Tags: {', '.join(post['tags'])}")
        print("-" * 60)

def delete_blog_post(post_id: int) -> None:
    """Delete a blog post by ID"""
    data = load_blog_data()
    
    original_count = len(data['posts'])
    data['posts'] = [post for post in data['posts'] if post['id'] != post_id]
    
    if len(data['posts']) < original_count:
        save_blog_data(data)
        print(f"✅ Blog post with ID {post_id} deleted successfully!")
    else:
        print(f"❌ Blog post with ID {post_id} not found.")

def update_blog_post(post_id: int, **updates) -> None:
    """Update a blog post by ID"""
    data = load_blog_data()
    
    for post in data['posts']:
        if post['id'] == post_id:
            post.update(updates)
            save_blog_data(data)
            print(f"✅ Blog post with ID {post_id} updated successfully!")
            return
    
    print(f"❌ Blog post with ID {post_id} not found.")

def main():
    """Main menu for blog management"""
    while True:
        print("\n🌟 Serenity Wellness Studio - Blog Manager")
        print("=" * 50)
        print("1. List all blog posts")
        print("2. Add new blog post")
        print("3. Delete blog post")
        print("4. Update blog post")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            list_blog_posts()
        
        elif choice == '2':
            print("\n📝 Add New Blog Post")
            print("-" * 30)
            
            title = input("Title: ").strip()
            if not title:
                print("❌ Title is required!")
                continue
            
            excerpt = input("Excerpt (brief description): ").strip()
            if not excerpt:
                print("❌ Excerpt is required!")
                continue
            
            category = input("Category (soundbath/science/wellness/therapeutic-sessions/etc.): ").strip()
            if not category:
                category = "wellness"
            
            content = input("Content (HTML format): ").strip()
            if not content:
                print("❌ Content is required!")
                continue
            
            author = input("Author (press Enter for 'Serenity Wellness Team'): ").strip()
            if not author:
                author = "Serenity Wellness Team"
            
            tags_input = input("Tags (comma-separated): ").strip()
            tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else []
            
            featured_image = input("Featured image filename (press Enter for 'default-post.jpg'): ").strip()
            if not featured_image:
                featured_image = "default-post.jpg"
            
            try:
                read_time = int(input("Read time in minutes (press Enter for 5): ").strip() or "5")
            except ValueError:
                read_time = 5
            
            published_input = input("Publish immediately? (y/n, default: y): ").strip().lower()
            published = published_input != 'n'
            
            add_blog_post(
                title=title,
                content=content,
                category=category,
                excerpt=excerpt,
                author=author,
                tags=tags,
                featured_image=featured_image,
                read_time=read_time,
                published=published
            )
        
        elif choice == '3':
            list_blog_posts()
            try:
                post_id = int(input("\nEnter post ID to delete: ").strip())
                confirm = input(f"Are you sure you want to delete post ID {post_id}? (y/n): ").strip().lower()
                if confirm == 'y':
                    delete_blog_post(post_id)
            except ValueError:
                print("❌ Invalid post ID!")
        
        elif choice == '4':
            list_blog_posts()
            try:
                post_id = int(input("\nEnter post ID to update: ").strip())
                print("Leave empty to keep current value...")
                
                updates = {}
                title = input("New title: ").strip()
                if title:
                    updates['title'] = title
                    updates['slug'] = create_slug(title)
                
                excerpt = input("New excerpt: ").strip()
                if excerpt:
                    updates['excerpt'] = excerpt
                
                category = input("New category: ").strip()
                if category:
                    updates['category'] = category
                
                published_input = input("Published? (y/n): ").strip().lower()
                if published_input in ['y', 'n']:
                    updates['published'] = published_input == 'y'
                
                if updates:
                    update_blog_post(post_id, **updates)
                else:
                    print("No updates provided.")
                    
            except ValueError:
                print("❌ Invalid post ID!")
        
        elif choice == '5':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice! Please select 1-5.")

if __name__ == "__main__":
    main()
