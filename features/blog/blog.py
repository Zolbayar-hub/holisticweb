"""
Standalone Blog Feature
Professional AI blog system with human-focused design
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from datetime import datetime, timedelta
import os
import json
from werkzeug.utils import secure_filename

# Create blueprint with custom template and static folders
blog_bp = Blueprint(
    'blog', 
    __name__, 
    url_prefix='/blog',
    template_folder='templates',
    static_folder='static',
    static_url_path='/blog/static'
)

# Mock data storage (replace with database in production)
BLOG_DATA_FILE = 'blog_data.json'

# Blog categories with descriptions
BLOG_CATEGORIES = {
    'therapeutic-sessions': {
        'name': 'Therapeutic Sessions',
        'description': 'Explore various therapeutic approaches including sound healing, meditation, and breathwork to restore balance and promote deep healing.',
        'icon': '🎭',
        'color': '#8B5E3C',
        'services': [
            'Sound Healing Therapy',
            'Private Meditation Session', 
            'Guided Breathwork Therapy',
            'Deep Relaxation Session'
        ]
    },
    'energy-work': {
        'name': 'Energy Work',
        'description': 'Discover the power of energy healing through chakra balancing, stress release practices, and nervous system restoration.',
        'icon': '⚡',
        'color': '#2c3e50',
        'services': [
            'Chakra Balancing',
            'Stress Release Practice',
            'Nervous System Reset',
            'Sleep Support Session'
        ]
    },
    'group-experiences': {
        'name': 'Group Experiences',
        'description': 'Join community healing through group sound baths, workshops, classes, and transformative events and retreats.',
        'icon': '👥',
        'color': '#27ae60',
        'services': [
            'Group Sound Bath',
            'Workshops & Classes',
            'Events & Retreats'
        ]
    },
    'wellness-benefits': {
        'name': 'Wellness Benefits',
        'description': 'Learn about the profound benefits of holistic practices for stress relief, emotional wellness, better sleep, and energy balance.',
        'icon': '✨',
        'color': '#e67e22',
        'services': [
            'Stress Relief',
            'Emotional Wellness',
            'Better Sleep',
            'Energy Balance'
        ]
    },
    'soundbath': {
        'name': 'Sound Bath',
        'description': 'Immerse yourself in healing vibrations through sound baths, singing bowls, and vibrational therapy for deep relaxation and restoration.',
        'icon': '🎵',
        'color': '#667eea',
        'services': [
            'Sound Healing Therapy',
            'Tibetan Singing Bowls',
            'Crystal Bowl Sessions',
            'Vibrational Therapy'
        ]
    },
    'science': {
        'name': 'Science',
        'description': 'Explore the scientific research and evidence behind holistic wellness practices, from neuroscience to frequency healing.',
        'icon': '🔬',
        'color': '#3498db',
        'services': [
            'Research-Based Therapy',
            'Neuroscience Studies',
            'Evidence-Based Wellness',
            'Scientific Validation'
        ]
    },
    'wellness': {
        'name': 'Wellness',
        'description': 'Comprehensive wellness approaches that integrate mind, body, and spirit for optimal health and well-being.',
        'icon': '🌿',
        'color': '#27ae60',
        'services': [
            'Holistic Wellness',
            'Mind-Body Integration',
            'Lifestyle Wellness',
            'Complete Health Solutions'
        ]
    },
    'ai': {
        'name': 'AI & Technology',
        'description': 'Explore how artificial intelligence and modern technology enhance traditional wellness practices and meditation.',
        'icon': '🤖',
        'color': '#667eea',
        'services': [
            'AI-Enhanced Meditation',
            'Smart Wellness Tools',
            'Biometric Tracking',
            'Personalized Therapy'
        ]
    },
    'energy-healing': {
        'name': 'Energy Healing',
        'description': 'Understand and release energy blockages through various healing modalities including chakra work, breathwork, and energy clearing techniques.',
        'icon': '🌟',
        'color': '#764ba2',
        'services': [
            'Energy Blockage Clearing',
            'Chakra Balancing',
            'Reiki Healing',
            'Breathwork Therapy'
        ]
    }
}

def load_blog_data():
    """Load blog posts from JSON file"""
    if os.path.exists(BLOG_DATA_FILE):
        with open(BLOG_DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "posts": [
            {
                "id": 1,
                "title": "How AI Is Transforming Wellness and Mindfulness in 2025",
                "slug": "ai-transforming-wellness-2025",
                "category": "wellness-benefits",
                "excerpt": "Discover how artificial intelligence is revolutionizing personal wellness, meditation apps, and holistic health approaches.",
                "content": """
                <p>The intersection of artificial intelligence and wellness is creating unprecedented opportunities for personal growth and healing. As we navigate 2025, AI-powered wellness tools are becoming more sophisticated, personalized, and accessible than ever before.</p>
                
                <h3>The Rise of AI-Powered Meditation</h3>
                <p>Modern meditation apps now use AI to adapt to your emotional state, stress levels, and personal preferences. These systems analyze your voice patterns, heart rate variability, and usage patterns to create truly personalized mindfulness experiences.</p>
                
                <h3>Personalized Wellness Recommendations</h3>
                <p>AI algorithms can now process vast amounts of health data to provide tailored wellness recommendations. From sleep optimization to nutrition guidance, these systems learn from your daily habits and provide actionable insights.</p>
                
                <h3>The Future of Holistic Health</h3>
                <p>We're seeing AI integration in traditional healing practices, creating bridges between ancient wisdom and modern technology. This fusion is making holistic health more accessible and effective for millions of people worldwide.</p>
                """,
                "author": "Serenity Wellness Team",
                "published_date": "2025-11-10",
                "tags": ["AI", "Wellness", "Mindfulness", "Technology"],
                "featured_image": "ai-wellness-hero.jpg",
                "read_time": 5,
                "published": True
            },
            {
                "id": 2,
                "title": "5 Science-Backed Benefits of Regular Meditation Practice",
                "slug": "science-backed-meditation-benefits",
                "category": "therapeutic-sessions",
                "excerpt": "Explore the latest research on how consistent meditation practice can improve your mental health, cognitive function, and overall well-being.",
                "content": """
                <p>Recent neuroscience research has provided compelling evidence for the transformative power of regular meditation practice. Here are five scientifically-proven benefits that will inspire you to start or deepen your practice.</p>
                
                <h3>1. Enhanced Emotional Regulation</h3>
                <p>Studies show that regular meditation increases activity in the prefrontal cortex while reducing amygdala reactivity, leading to better emotional balance and reduced anxiety.</p>
                
                <h3>2. Improved Focus and Attention</h3>
                <p>Research indicates that just 8 weeks of mindfulness practice can increase cortical thickness in areas associated with attention and sensory processing.</p>
                
                <h3>3. Stress Reduction at the Cellular Level</h3>
                <p>Meditation has been shown to reduce cortisol levels and inflammatory markers, promoting healing and resilience at the cellular level.</p>
                
                <h3>4. Better Sleep Quality</h3>
                <p>Studies demonstrate that meditation practices can improve sleep onset, duration, and quality by calming the nervous system and reducing racing thoughts.</p>
                
                <h3>5. Increased Self-Awareness and Compassion</h3>
                <p>Neuroimaging studies show that meditation increases gray matter density in areas associated with self-awareness, empathy, and compassion.</p>
                """,
                "author": "Dr. Sarah Chen",
                "published_date": "2025-11-08",
                "tags": ["Meditation", "Science", "Mental Health", "Research"],
                "featured_image": "meditation-science.jpg",
                "read_time": 7,
                "published": True
            },
            {
                "id": 3,
                "title": "Creating Sacred Space: The Power of Group Sound Healing",
                "slug": "group-sound-healing-sacred-space",
                "category": "group-experiences",
                "excerpt": "Discover how group sound baths create a powerful collective healing experience that amplifies individual transformation and builds community connection.",
                "content": """
                <p>There's something magical that happens when people come together with shared intention for healing. In our group sound healing sessions, this magic becomes palpable, creating a sacred space where individual transformation is amplified by collective energy.</p>
                
                <h3>The Science of Group Healing</h3>
                <p>Research in fields ranging from neuroscience to quantum physics suggests that when groups meditate or engage in healing practices together, their brainwaves begin to synchronize. This phenomenon, called entrainment, creates a powerful field of coherence that can deepen each person's individual experience.</p>
                
                <h3>What Makes Our Group Sessions Special</h3>
                <p>Our monthly group sound baths are carefully crafted to honor both individual needs and collective healing. Using crystal singing bowls, gongs, and other therapeutic instruments, we create a sonic journey that guides the group through layers of relaxation and transformation.</p>
                
                <h3>The Ripple Effect of Community Healing</h3>
                <p>When we heal in community, the benefits extend far beyond the session itself. Participants often report feeling more connected, supported, and empowered in their daily lives. The bonds formed in these sacred spaces become sources of ongoing strength and inspiration.</p>
                """,
                "author": "Serenity Wellness Team",
                "published_date": "2025-11-05",
                "tags": ["GroupHealing", "SoundBath", "Community", "Transformation"],
                "featured_image": "blogg.png",
                "read_time": 6,
                "published": True
            },
            {
                "id": 4,
                "title": "Chakra Balancing: Your Complete Guide to Energy Alignment",
                "slug": "chakra-balancing-energy-alignment-guide",
                "category": "energy-work",
                "excerpt": "Learn how chakra balancing can restore your natural energy flow, improve physical health, and enhance emotional well-being through this comprehensive guide.",
                "content": """
                <p>Your body's energy centers, known as chakras, are constantly responding to your thoughts, emotions, and experiences. When these energy centers become blocked or imbalanced, you may experience physical symptoms, emotional instability, or a sense of being disconnected from your true self.</p>
                
                <h3>Understanding the Seven Main Chakras</h3>
                <p>Each chakra governs specific aspects of your physical, emotional, and spiritual well-being. From the root chakra's connection to safety and grounding, to the crown chakra's link to spiritual connection, understanding these energy centers is the first step toward healing.</p>
                
                <h3>Signs Your Chakras Need Attention</h3>
                <p>Chakra imbalances often manifest as recurring physical symptoms, persistent emotional patterns, or feelings of being stuck in certain areas of life. Learning to recognize these signs empowers you to address imbalances before they become chronic issues.</p>
                
                <h3>The Chakra Balancing Process</h3>
                <p>During a chakra balancing session, we use a combination of sound healing, energy work, and guided visualization to clear blockages and restore natural energy flow. Many clients report immediate feelings of lightness, clarity, and renewed vitality.</p>
                """,
                "author": "Dr. Sarah Chen",
                "published_date": "2025-11-03",
                "tags": ["ChakraHealing", "EnergyWork", "Balance", "Wellness"],
                "featured_image": "chakra-balancing.jpg",
                "read_time": 8,
                "published": True
            },
            {
                "id": 5,
                "title": "The Sleep Solution: How Sound Therapy Transforms Your Rest",
                "slug": "sound-therapy-sleep-solution",
                "category": "wellness-benefits",
                "excerpt": "Discover how sound therapy can revolutionize your sleep quality, helping you fall asleep faster, sleep deeper, and wake up more refreshed and energized.",
                "content": """
                <p>Quality sleep is the foundation of good health, yet millions of people struggle with insomnia, restless nights, and waking up exhausted. Sound therapy offers a natural, effective solution that works with your body's own healing mechanisms to restore healthy sleep patterns.</p>
                
                <h3>The Science of Sound and Sleep</h3>
                <p>Research shows that specific frequencies can trigger the release of sleep-promoting hormones like melatonin while reducing stress hormones like cortisol. These therapeutic sounds essentially guide your nervous system from a state of activation into deep relaxation and restorative sleep.</p>
                
                <h3>How Sound Therapy Addresses Sleep Issues</h3>
                <p>Unlike sleep medications that can create dependency and side effects, sound therapy works by addressing the root causes of sleep disturbance: an overactive nervous system, racing thoughts, and accumulated stress in the body.</p>
                
                <h3>Creating Your Sleep Sanctuary</h3>
                <p>Beyond our specialized sleep support sessions, we'll teach you simple sound techniques you can use at home to maintain healthy sleep patterns. From specific breathing sounds to using singing bowls before bed, these tools become part of your nightly ritual.</p>
                """,
                "author": "Serenity Wellness Team",
                "published_date": "2025-11-01",
                "tags": ["Sleep", "SoundTherapy", "Wellness", "Health"],
                "featured_image": "sound-therapy-sleep.jpg",
                "read_time": 6,
                "published": True
            }
        ]
    }

def save_blog_data(data):
    """Save blog posts to JSON file"""
    with open(BLOG_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@blog_bp.route('/')
def index():
    """Main blog page with all published posts"""
    data = load_blog_data()
    published_posts = [post for post in data['posts'] if post.get('published', False)]
    
    # Sort by published date (newest first)
    published_posts.sort(key=lambda x: x['published_date'], reverse=True)
    
    return render_template('blog.html', posts=published_posts, categories=BLOG_CATEGORIES)

@blog_bp.route('/post/<slug>')
def post_detail(slug):
    """Individual blog post page"""
    data = load_blog_data()
    post = next((p for p in data['posts'] if p['slug'] == slug and p.get('published', False)), None)
    
    if not post:
        flash("Blog post not found.", "error")
        return redirect(url_for('blog.index'))
    
    # Get related posts (same tags, excluding current post)
    related_posts = []
    for p in data['posts']:
        if p['id'] != post['id'] and p.get('published', False):
            common_tags = set(p['tags']) & set(post['tags'])
            if common_tags:
                related_posts.append(p)
    
    # Limit to 3 related posts
    related_posts = related_posts[:3]
    
    return render_template('blog_post.html', post=post, related_posts=related_posts, categories=BLOG_CATEGORIES)

@blog_bp.route('/category/<category>')
def posts_by_category(category):
    """Posts filtered by category"""
    data = load_blog_data()
    
    # Get category info
    category_info = BLOG_CATEGORIES.get(category)
    if not category_info:
        flash("Category not found.", "error")
        return redirect(url_for('blog.index'))
    
    # Filter posts by category
    category_posts = [
        post for post in data['posts'] 
        if post.get('category') == category and post.get('published', False)
    ]
    
    category_posts.sort(key=lambda x: x['published_date'], reverse=True)
    
    return render_template('blog_category.html', 
                         posts=category_posts, 
                         category=category,
                         category_info=category_info,
                         categories=BLOG_CATEGORIES)

@blog_bp.route('/tag/<tag>')
def posts_by_tag(tag):
    """Posts filtered by tag"""
    data = load_blog_data()
    tagged_posts = [
        post for post in data['posts'] 
        if tag.lower() in [t.lower() for t in post['tags']] and post.get('published', False)
    ]
    
    tagged_posts.sort(key=lambda x: x['published_date'], reverse=True)
    
    return render_template('blog_tag.html', posts=tagged_posts, tag=tag, categories=BLOG_CATEGORIES)

@blog_bp.route('/search')
def search():
    """Search blog posts"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('blog.index'))
    
    data = load_blog_data()
    results = []
    
    for post in data['posts']:
        if post.get('published', False):
            # Search in title, excerpt, and content
            searchable_text = f"{post['title']} {post['excerpt']} {post['content']}".lower()
            if query.lower() in searchable_text:
                results.append(post)
    
    results.sort(key=lambda x: x['published_date'], reverse=True)
    
    return render_template('blog_search.html', posts=results, query=query, categories=BLOG_CATEGORIES)

@blog_bp.route('/api/posts')
def api_posts():
    """API endpoint for blog posts"""
    data = load_blog_data()
    published_posts = [post for post in data['posts'] if post.get('published', False)]
    
    # Remove content for API response (just metadata)
    api_posts = []
    for post in published_posts:
        api_post = {
            'id': post['id'],
            'title': post['title'],
            'slug': post['slug'],
            'excerpt': post['excerpt'],
            'author': post['author'],
            'published_date': post['published_date'],
            'tags': post['tags'],
            'read_time': post['read_time']
        }
        api_posts.append(api_post)
    
    return jsonify({'posts': api_posts})

def get_feature_info():
    """Return information about this feature"""
    return {
        "name": "Professional Blog System",
        "version": "1.0.0",
        "description": "Complete AI-focused blog with human-centered design, SEO optimization, and responsive layout",
        "dependencies": ["Flask"],
        "routes": [
            "/blog/",
            "/blog/post/<slug>",
            "/blog/tag/<tag>",
            "/blog/search",
            "/blog/api/posts"
        ],
        "templates": [
            "blog.html",
            "blog_post.html", 
            "blog_tag.html",
            "blog_search.html"
        ],
        "static_files": [
            "blog.css",
            "blog.js"
        ]
    }
