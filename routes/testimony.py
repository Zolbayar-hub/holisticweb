from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from flask_login import current_user
from db import db
from db.models import Testimonial
from functools import wraps
from datetime import datetime

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
                mail = current_app.mail
                admin_subject = f"New Testimonial Submitted by {testimonial.client_name}"
                admin_body = f"""
A new testimonial was just submitted and published immediately on the site.

Name: {testimonial.client_name}
Title: {testimonial.client_title}
Rating: {testimonial.rating}
Email: {testimonial.email}

Testimonial:
{testimonial.testimonial_text}

--
This notification was sent automatically.
"""
                admin_msg = Message(
                    subject=admin_subject,
                    recipients=[current_app.config.get('MAIL_USERNAME', 'admin@example.com')],
                    body=admin_body
                )
                mail.send(admin_msg)
            except Exception as e:
                # Log but don't block the user from seeing their testimonial
                current_app.logger.error(f"Failed to send testimonial notification: {e}")

            flash('Thank you — your testimonial has been published and will appear on the homepage.', 'success')
            return redirect(url_for('main.home'))
            
        except Exception as e:
            flash('Error submitting testimonial. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('testimony.html')

# Helper function to get approved testimonials for home page
def get_approved_testimonials():
    """Get approved testimonials for display on home page"""
    return Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
