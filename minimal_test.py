#!/usr/bin/env python3
"""
Minimal Flask Blog Test
"""
from flask import Flask, Blueprint

# Create a minimal test blueprint with the same configuration
test_bp = Blueprint(
    'blog', 
    __name__, 
    url_prefix='/blog',
    template_folder='features/blog/templates',
    static_folder='features/blog/static',
    static_url_path='/blog/static'
)

app = Flask(__name__)
app.register_blueprint(test_bp)

with app.app_context():
    from flask import url_for
    
    # Test URL generation
    img_url = url_for('blog.static', filename='images/default-post.jpg')
    print(f"Generated URL: {img_url}")
    
    if '/blog/blog/' in img_url:
        print("❌ Double /blog/ detected - configuration issue")
    else:
        print("✅ URL correctly configured")
