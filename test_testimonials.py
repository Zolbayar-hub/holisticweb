from flask_app import app
from db.models import Testimonial

# Test the testimonials system
with app.app_context():
    print("=== Testimonials System Test ===")
    
    # Test testimonials query (same as used in home route)
    approved_testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
    print(f"✅ Approved testimonials for homepage: {len(approved_testimonials)}")
    
    # Test admin route exists
    with app.test_client() as client:
        # Test that admin routes are registered
        print("✅ Testing admin routes...")
        
        # Test admin testimonials route (should redirect to login)
        response = client.get('/admin/testimonials')
        print(f"✅ /admin/testimonials route responds: {response.status_code}")
        
        # Test home page with testimonials
        response = client.get('/')
        print(f"✅ Home page responds: {response.status_code}")
        
        # Test testimonial submission form
        response = client.get('/submit-testimonial')
        print(f"✅ Testimonial form responds: {response.status_code}")
        
    print("\n=== Database Content ===")
    all_testimonials = Testimonial.query.all()
    for t in all_testimonials:
        status = "✅ Approved" if t.is_approved else "⏳ Pending"
        featured = "⭐ Featured" if t.is_featured else ""
        print(f"{status} {featured} - {t.client_name}: '{t.testimonial_text[:50]}...'")
    
    print(f"\n=== Summary ===")
    print(f"Total testimonials: {len(all_testimonials)}")
    print(f"Approved testimonials: {len(approved_testimonials)}")
    print(f"Pending testimonials: {len(all_testimonials) - len(approved_testimonials)}")
    
    print(f"\n=== Admin Access ===")
    print(f"Admin Panel: http://127.0.0.1:5000/admin/")
    print(f"Username: admin")
    print(f"Password: admin123")
    print(f"Direct Testimonials Admin: http://127.0.0.1:5000/admin/testimonials")
    
    print(f"\n=== User Features ===")
    print(f"Homepage with testimonials: http://127.0.0.1:5000/")
    print(f"Submit testimonial: http://127.0.0.1:5000/submit-testimonial")
