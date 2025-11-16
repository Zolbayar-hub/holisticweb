"""
Standalone Testimonials Feature
Complete testimonials system with submission, approval, and display
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_mail import Message
from flask_login import current_user
from db import db
from db.models import Testimonial
from functools import wraps
from datetime import datetime

# Create testimonial blueprint with custom template and static folders
testimony_bp = Blueprint(
    'testimonials', 
    __name__, 
    url_prefix='/testimonials',
    template_folder='templates',
    static_folder='static',
    static_url_path='/testimonials/static'
)

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not hasattr(current_user, 'role') or current_user.role.name != 'admin':
            flash('Access denied. Admin role required.', 'error')
            return redirect(url_for('main.home'))
        
        return f(*args, **kwargs)
    return decorated_function

# Public testimonial submission route
@testimony_bp.route('/submit', methods=['GET', 'POST'])
def submit_testimonial():
    """Public testimonial submission form"""
    if request.method == 'POST':
        try:
            testimonial = Testimonial(
                client_name=request.form.get('client_name'),
                client_title=request.form.get('client_title'),
                testimonial_text=request.form.get('testimonial_text'),
                rating=int(request.form.get('rating', 5)),
                email=request.form.get('email'),
                is_approved=True,  # Publish immediately
                is_featured=False
            )

            # Set approval metadata for immediate publish
            testimonial.approved_at = datetime.utcnow()
            testimonial.approved_by = None
            
            db.session.add(testimonial)
            db.session.commit()

            # Notify admin by email (best-effort)
            try:
                notify_admin_new_testimonial(testimonial)
            except Exception as e:
                current_app.logger.warning(f"Failed to send admin notification: {e}")

            flash('Thank you for your testimonial! It has been published.', 'success')
            return redirect(url_for('testimonials.submit_testimonial'))

        except Exception as e:
            current_app.logger.error(f"Error saving testimonial: {e}")
            flash('Sorry, there was an error submitting your testimonial. Please try again.', 'error')

    return render_template('testimony.html')

# API: Get approved testimonials
@testimony_bp.route('/api/approved')
def get_approved_testimonials():
    """API endpoint to get approved testimonials"""
    testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
    
    testimonials_data = []
    for t in testimonials:
        testimonials_data.append({
            'id': t.id,
            'client_name': t.client_name,
            'client_title': t.client_title or '',
            'testimonial_text': t.testimonial_text,
            'rating': t.rating,
            'is_featured': t.is_featured,
            'created_at': t.created_at.strftime('%Y-%m-%d')
        })
    
    return jsonify(testimonials_data)

# API: Get featured testimonials
@testimony_bp.route('/api/featured')
def get_featured_testimonials():
    """API endpoint to get featured testimonials only"""
    testimonials = Testimonial.query.filter_by(is_approved=True, is_featured=True).order_by(Testimonial.created_at.desc()).all()
    
    testimonials_data = []
    for t in testimonials:
        testimonials_data.append({
            'id': t.id,
            'client_name': t.client_name,
            'client_title': t.client_title or '',
            'testimonial_text': t.testimonial_text,
            'rating': t.rating,
            'created_at': t.created_at.strftime('%Y-%m-%d')
        })
    
    return jsonify(testimonials_data)

# Admin: List all testimonials
@testimony_bp.route('/admin')
@admin_required
def admin_testimonials():
    """Admin page to manage testimonials"""
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('admin_testimonials.html', testimonials=testimonials)

# Admin: Approve testimonial
@testimony_bp.route('/admin/<int:testimonial_id>/approve', methods=['POST'])
@admin_required
def approve_testimonial(testimonial_id):
    """Approve a testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    testimonial.is_approved = True
    testimonial.approved_at = datetime.utcnow()
    testimonial.approved_by = current_user.id
    
    db.session.commit()
    flash('Testimonial approved successfully!', 'success')
    return redirect(url_for('testimonials.admin_testimonials'))

# Admin: Feature testimonial
@testimony_bp.route('/admin/<int:testimonial_id>/feature', methods=['POST'])
@admin_required
def feature_testimonial(testimonial_id):
    """Toggle featured status of testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    testimonial.is_featured = not testimonial.is_featured
    
    db.session.commit()
    status = 'featured' if testimonial.is_featured else 'unfeatured'
    flash(f'Testimonial {status} successfully!', 'success')
    return redirect(url_for('testimonials.admin_testimonials'))

# Admin: Delete testimonial
@testimony_bp.route('/admin/<int:testimonial_id>/delete', methods=['POST'])
@admin_required
def delete_testimonial(testimonial_id):
    """Delete a testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    db.session.delete(testimonial)
    db.session.commit()
    
    flash('Testimonial deleted successfully!', 'success')
    return redirect(url_for('testimonials.admin_testimonials'))

def notify_admin_new_testimonial(testimonial):
    """Notify admin of new testimonial submission"""
    try:
        mail = current_app.mail
        
        subject = f"New Testimonial from {testimonial.client_name}"
        body = f"""
A new testimonial has been submitted:

Name: {testimonial.client_name}
Title: {testimonial.client_title or 'Not provided'}
Rating: {testimonial.rating}/5 stars
Email: {testimonial.email or 'Not provided'}

Testimonial:
{testimonial.testimonial_text}

---
Submitted at: {testimonial.created_at}
Status: {'Approved' if testimonial.is_approved else 'Pending Approval'}
"""
        
        msg = Message(
            subject=subject,
            recipients=[current_app.config.get('MAIL_USERNAME', 'admin@example.com')],
            body=body
        )
        mail.send(msg)
        
    except Exception as e:
        current_app.logger.error(f"Failed to send admin notification: {e}")

def get_approved_testimonials():
    """Helper function to get approved testimonials for other parts of the app"""
    return Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()

def get_featured_testimonials():
    """Helper function to get featured testimonials for other parts of the app"""
    return Testimonial.query.filter_by(is_approved=True, is_featured=True).order_by(Testimonial.created_at.desc()).all()

def get_feature_info():
    """Return information about this feature"""
    return {
        "name": "Testimonials System",
        "version": "1.0.0",
        "description": "Complete testimonials system with submission, approval, and display",
        "dependencies": ["Flask-Mail", "Flask-Login"],
        "routes": [
            "/testimonials/submit",
            "/testimonials/api/approved",
            "/testimonials/api/featured",
            "/testimonials/admin",
            "/testimonials/admin/<id>/approve",
            "/testimonials/admin/<id>/feature",
            "/testimonials/admin/<id>/delete"
        ],
        "templates": ["testimony.html", "admin_testimonials.html"],
        "static_files": ["testimonials.css", "testimonials.js"]
    }
