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
            return redirect(url_for('home'))
        
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
            return redirect(url_for('home'))
            
        except Exception as e:
            flash('Error submitting testimonial. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('testimonial_form.html')

# Admin testimonial management routes
@testimony_bp.route('/admin')
@admin_required
def admin_testimonials():
    """Admin testimonials management"""
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('admin/testimonials.html', testimonials=testimonials)

@testimony_bp.route('/admin/approve/<int:testimonial_id>', methods=['POST'])
@admin_required
def approve_testimonial(testimonial_id):
    """Approve a testimonial"""
    try:
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        testimonial.is_approved = True
        testimonial.approved_at = db.func.now()
        testimonial.approved_by = current_user.id
        
        db.session.commit()
        flash('Testimonial approved successfully!', 'success')
        
    except Exception as e:
        flash(f'Error approving testimonial: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('testimony.admin_testimonials'))

@testimony_bp.route('/admin/disapprove/<int:testimonial_id>', methods=['POST'])
@admin_required
def disapprove_testimonial(testimonial_id):
    """Disapprove a testimonial"""
    try:
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        testimonial.is_approved = False
        testimonial.approved_at = None
        testimonial.approved_by = None
        
        db.session.commit()
        flash('Testimonial disapproved successfully!', 'success')
        
    except Exception as e:
        flash(f'Error disapproving testimonial: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('testimony.admin_testimonials'))

@testimony_bp.route('/admin/feature/<int:testimonial_id>', methods=['POST'])
@admin_required
def toggle_feature_testimonial(testimonial_id):
    """Toggle featured status of a testimonial"""
    try:
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        testimonial.is_featured = not testimonial.is_featured
        
        db.session.commit()
        status = "featured" if testimonial.is_featured else "unfeatured"
        flash(f'Testimonial {status} successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating testimonial: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('testimony.admin_testimonials'))

@testimony_bp.route('/admin/edit/<int:testimonial_id>', methods=['GET', 'POST'])
@admin_required
def edit_testimonial(testimonial_id):
    """Edit a testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    
    if request.method == 'POST':
        try:
            testimonial.client_name = request.form.get('client_name')
            testimonial.client_title = request.form.get('client_title')
            testimonial.testimonial_text = request.form.get('testimonial_text')
            testimonial.rating = int(request.form.get('rating', 5))
            testimonial.email = request.form.get('email')
            
            db.session.commit()
            flash('Testimonial updated successfully!', 'success')
            return redirect(url_for('testimony.admin_testimonials'))
            
        except Exception as e:
            flash(f'Error updating testimonial: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_testimonial.html', testimonial=testimonial)

@testimony_bp.route('/admin/create', methods=['GET', 'POST'])
@admin_required
def create_testimonial():
    """Create a new testimonial"""
    if request.method == 'POST':
        try:
            testimonial = Testimonial(
                client_name=request.form.get('client_name'),
                client_title=request.form.get('client_title'),
                testimonial_text=request.form.get('testimonial_text'),
                rating=int(request.form.get('rating', 5)),
                email=request.form.get('email'),
                is_approved=True,  # Admin-created testimonials are auto-approved
                approved_by=current_user.id,
                approved_at=db.func.now()
            )
            
            db.session.add(testimonial)
            db.session.commit()
            flash('Testimonial created successfully!', 'success')
            return redirect(url_for('testimony.admin_testimonials'))
            
        except Exception as e:
            flash(f'Error creating testimonial: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_testimonial.html')

@testimony_bp.route('/admin/delete/<int:testimonial_id>', methods=['POST'])
@admin_required
def delete_testimonial(testimonial_id):
    """Delete a testimonial"""
    try:
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        db.session.delete(testimonial)
        db.session.commit()
        flash('Testimonial deleted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error deleting testimonial: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('testimony.admin_testimonials'))

# Helper function to get approved testimonials for home page
def get_approved_testimonials():
    """Get approved testimonials for display on home page"""
    return Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
