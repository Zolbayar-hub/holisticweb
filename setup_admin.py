from flask_app import app, db
from db.models import User, Role
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if admin role exists
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        print("Creating admin role...")
        admin_role = Role(name='admin')
        db.session.add(admin_role)
        db.session.commit()
        print("Admin role created!")
    
    # Check if admin user exists
    admin_user = User.query.filter_by(role_id=admin_role.id).first()
    if not admin_user:
        print("Creating admin user...")
        admin_user = User(
            username='admin',
            email='admin@holistictherapy.com',
            password=generate_password_hash('admin123'),
            role_id=admin_role.id
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Admin user already exists:")
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
    
    # List all testimonials
    from db.models import Testimonial
    testimonials = Testimonial.query.all()
    print(f"\nTestimonials in database: {len(testimonials)}")
    for t in testimonials:
        status = "Approved" if t.is_approved else "Pending"
        featured = "Featured" if t.is_featured else "Not Featured"
        print(f"  - {t.client_name}: {status}, {featured}")
