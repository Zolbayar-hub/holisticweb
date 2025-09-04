from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from db import db
from db.models import Testimonial
from functools import wraps

# Create testimonial blueprint
testimony_bp = Blueprint('testimony', __name__, url_prefix='/testimonials')

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
                is_approved=False,  # Requires admin approval
                is_featured=False
            )
            
            db.session.add(testimonial)
            db.session.commit()
            
            flash('Thank you for your testimonial! It will be reviewed and published soon.', 'success')
            return redirect(url_for('main.home'))
            
        except Exception as e:
            flash('Error submitting testimonial. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('testimony.html')

# Helper function to get approved testimonials for home page
def get_approved_testimonials():
    """Get approved testimonials for display on home page"""
    return Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
