from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from db import db
from db.models import Service, SiteSetting, EmailTemplate, User, Testimonial, AboutImage
from werkzeug.utils import secure_filename
from utils.site_settings import get_settings_by_language
import os
from functools import wraps
from datetime import datetime

web_admin_bp = Blueprint('web_admin_panel', __name__, url_prefix='/web_admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@web_admin_bp.route('/')
@admin_required
def web_admin_panel():
    """Main admin panel dashboard"""
    return render_template('admin/dashboard.html')

@web_admin_bp.route('/services')
@admin_required
def admin_services():
    """Admin services management"""
    services = Service.query.all()
    return render_template('admin/services.html', services=services)

@web_admin_bp.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@admin_required
def edit_service(service_id):
    """Edit a service"""
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        try:
            service.name = request.form.get('name')
            service.description = request.form.get('description')
            service.price = float(request.form.get('price'))
            service.duration = int(request.form.get('duration'))
            service.language = request.form.get('language', 'ENG')  # Add language support
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # Create uploads directory if it doesn't exist
                    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'services')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save file
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    service.image_path = f"uploads/services/{filename}"
            
            db.session.commit()
            flash('Service updated successfully!', 'success')
            return redirect(url_for('web_admin_panel.admin_services'))
            
        except Exception as e:
            flash(f'Error updating service: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_service.html', service=service)

@web_admin_bp.route('/services/create', methods=['GET', 'POST'])
@admin_required
def create_service():
    """Create a new service"""
    if request.method == 'POST':
        try:
            service = Service(
                name=request.form.get('name'),
                description=request.form.get('description'),
                price=float(request.form.get('price')),
                duration=int(request.form.get('duration')),
                language=request.form.get('language', 'ENG')  # Add language support
            )
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'services')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    service.image_path = f"uploads/services/{filename}"
            
            db.session.add(service)
            db.session.commit()
            flash('Service created successfully!', 'success')
            return redirect(url_for('web_admin_panel.admin_services'))
            
        except Exception as e:
            flash(f'Error creating service: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_service.html')

@web_admin_bp.route('/services/delete/<int:service_id>', methods=['POST'])
@admin_required
def delete_service(service_id):
    """Delete a service"""
    try:
        service = Service.query.get_or_404(service_id)
        
        # Delete image file if exists
        if service.image_path:
            image_full_path = os.path.join(current_app.static_folder, service.image_path)
            if os.path.exists(image_full_path):
                os.remove(image_full_path)
        
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error deleting service: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('web_admin_panel.admin_services'))

@web_admin_bp.route('/emails')
@admin_required
def admin_emails():
    """Admin email templates management"""
    templates = EmailTemplate.query.all()
    return render_template('admin/emails.html', templates=templates)

@web_admin_bp.route('/emails/edit/<int:template_id>', methods=['GET', 'POST'])
@admin_required
def edit_email_template(template_id):
    """Edit an email template"""
    template = EmailTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        try:
            template.name = request.form.get('name')
            template.subject = request.form.get('subject')
            template.body = request.form.get('body')
            template.description = request.form.get('description')
            
            db.session.commit()
            flash('Email template updated successfully!', 'success')
            return redirect(url_for('web_admin_panel.admin_emails'))
            
        except Exception as e:
            flash(f'Error updating email template: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_email.html', template=template)

@web_admin_bp.route('/emails/create', methods=['GET', 'POST'])
@admin_required
def create_email_template():
    """Create a new email template"""
    if request.method == 'POST':
        try:
            template = EmailTemplate(
                name=request.form.get('name'),
                subject=request.form.get('subject'),
                body=request.form.get('body'),
                description=request.form.get('description')
            )
            
            db.session.add(template)
            db.session.commit()
            flash('Email template created successfully!', 'success')
            return redirect(url_for('web_admin_panel.admin_emails'))
            
        except Exception as e:
            flash(f'Error creating email template: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_email.html')

@web_admin_bp.route('/emails/delete/<int:template_id>', methods=['POST'])
@admin_required
def delete_email_template(template_id):
    """Delete an email template"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        db.session.delete(template)
        db.session.commit()
        flash('Email template deleted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error deleting email template: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('web_admin_panel.admin_emails'))

@web_admin_bp.route('/settings')
@admin_required
def admin_settings():
    """Admin site settings management"""
    settings = SiteSetting.query.all()
    
    # Convert to dictionary for easier access, grouped by language
    settings_dict = {}
    settings_by_language = get_settings_by_language()
    
    # Create a flat settings dict for backward compatibility
    for lang_settings in settings_by_language.values():
        settings_dict.update(lang_settings)
    
    return render_template('admin/settings.html', 
                         settings=settings, 
                         settings_dict=settings_dict,
                         settings_by_language=settings_by_language)

@web_admin_bp.route('/settings/update', methods=['POST'])
@admin_required
def update_settings():
    """Update site settings"""
    try:
        # Get the selected language from form, default to 'ENG'
        selected_language = request.form.get('language', 'ENG')
        
        # Validate language
        if selected_language not in ['ENG', 'MON']:
            selected_language = 'ENG'
        
        # Get all form data
        for key, value in request.form.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                
                # Find or create setting for the selected language
                setting = SiteSetting.query.filter_by(key=setting_key, language=selected_language).first()
                if not setting:
                    setting = SiteSetting(key=setting_key, language=selected_language)
                    db.session.add(setting)
                
                setting.value = value
        
        # Handle home page image upload
        if 'home_image' in request.files:
            file = request.files['home_image']
            if file and file.filename:
                try:
                    # Generate a unique filename to avoid conflicts
                    import time
                    timestamp = str(int(time.time()))
                    original_filename = secure_filename(file.filename)
                    name, ext = os.path.splitext(original_filename)
                    filename = f"{name}_{timestamp}{ext}"
                    
                    # Ensure upload directory exists with proper permissions
                    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'home')
                    try:
                        os.makedirs(upload_dir, mode=0o755, exist_ok=True)
                        current_app.logger.info(f"Created/verified upload directory: {upload_dir}")
                    except OSError as e:
                        current_app.logger.error(f"Failed to create upload directory: {e}")
                        raise Exception(f"Failed to create upload directory: {e}")
                    
                    # Save file with error handling
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    
                    # Verify file was saved successfully
                    if not os.path.exists(file_path):
                        raise Exception("File was not saved successfully")
                    
                    # Set file permissions (important for PythonAnywhere)
                    try:
                        os.chmod(file_path, 0o644)
                        current_app.logger.info(f"Set file permissions for: {file_path}")
                    except OSError as e:
                        current_app.logger.warning(f"Could not set file permissions: {e}")
                    
                    # Update or create home_image setting for the selected language
                    setting = SiteSetting.query.filter_by(key='home_image', language=selected_language).first()
                    if not setting:
                        setting = SiteSetting(key='home_image', language=selected_language)
                        db.session.add(setting)
                    
                    # Store relative path for Flask's url_for function
                    relative_path = f"uploads/home/{filename}"
                    setting.value = relative_path
                    
                    current_app.logger.info(f"Successfully uploaded home image: {relative_path} for language: {selected_language}")
                    
                except Exception as upload_error:
                    current_app.logger.error(f"Home image upload failed: {upload_error}")
                    flash(f'Failed to upload home image: {str(upload_error)}', 'error')
                    db.session.rollback()
                    return redirect(url_for('web_admin_panel.admin_settings'))
        
        db.session.commit()
        flash(f'Settings updated successfully for {selected_language}!', 'success')
        
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('web_admin_panel.admin_settings'))

@web_admin_bp.route('/upload-image', methods=['POST'])
@admin_required
def upload_image():
    """Generic image upload endpoint"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            upload_type = request.form.get('type', 'general')
            
            upload_dir = os.path.join(current_app.static_folder, 'uploads', upload_type)
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            image_url = f"uploads/{upload_type}/{filename}"
            
            return jsonify({
                'success': True,
                'image_url': image_url,
                'message': 'Image uploaded successfully'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_admin_bp.route('/testimonials')
@admin_required
def admin_testimonials():
    """Admin testimonials management"""
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('admin/testimonials.html', testimonials=testimonials)

@web_admin_bp.route('/testimonials/edit/<int:testimonial_id>', methods=['GET', 'POST'])
@admin_required
def edit_testimonial(testimonial_id):
    """Edit a testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    
    if request.method == 'POST':
        try:
            testimonial.client_name = request.form.get('client_name')
            testimonial.client_title = request.form.get('client_title', '')
            testimonial.testimonial_text = request.form.get('testimonial_text')
            testimonial.rating = int(request.form.get('rating', 5))
            testimonial.email = request.form.get('email', '')
            
            # Handle approval status
            was_approved = testimonial.is_approved
            testimonial.is_approved = 'is_approved' in request.form
            testimonial.is_featured = 'is_featured' in request.form
            
            # Set approval details if newly approved
            if not was_approved and testimonial.is_approved:
                testimonial.approved_at = datetime.utcnow()
                testimonial.approved_by = current_user.id
            elif not testimonial.is_approved:
                testimonial.approved_at = None
                testimonial.approved_by = None
            
            db.session.commit()
            flash('Testimonial updated successfully!', 'success')
            return redirect(url_for('web_admin_panel.admin_testimonials'))
            
        except Exception as e:
            flash(f'Error updating testimonial: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_testimonial.html', testimonial=testimonial)

@web_admin_bp.route('/testimonials/create', methods=['GET', 'POST'])
@admin_required
def create_testimonial():
    """Create a new testimonial"""
    if request.method == 'POST':
        try:
            testimonial = Testimonial(
                client_name=request.form.get('client_name'),
                client_title=request.form.get('client_title', ''),
                testimonial_text=request.form.get('testimonial_text'),
                rating=int(request.form.get('rating', 5)),
                email=request.form.get('email', ''),
                is_approved='is_approved' in request.form,
                is_featured='is_featured' in request.form
            )
            
            # Set approval details if approved
            if testimonial.is_approved:
                testimonial.approved_at = datetime.utcnow()
                testimonial.approved_by = current_user.id
            
            db.session.add(testimonial)
            db.session.commit()
            flash('Testimonial created successfully!', 'success')
            return redirect(url_for('web_admin_panel.admin_testimonials'))
            
        except Exception as e:
            flash(f'Error creating testimonial: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_testimonial.html', testimonial=None)

@web_admin_bp.route('/testimonials/delete/<int:testimonial_id>', methods=['POST'])
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
    
    return redirect(url_for('web_admin_panel.admin_testimonials'))

@web_admin_bp.route('/testimonials/approve/<int:testimonial_id>', methods=['POST'])
@admin_required
def approve_testimonial(testimonial_id):
    """Quick approve a testimonial (disabled: testimonials are published immediately)."""
    flash('Operation not allowed. Testimonials are published immediately — only deletion is permitted by admin.', 'warning')
    return redirect(url_for('web_admin_panel.admin_testimonials'))

@web_admin_bp.route('/testimonials/disapprove/<int:testimonial_id>', methods=['POST'])
@admin_required
def disapprove_testimonial(testimonial_id):
    """Disapprove a testimonial (disabled: testimonials are published immediately)."""
    flash('Operation not allowed. Testimonials are published immediately — only deletion is permitted by admin.', 'warning')
    return redirect(url_for('web_admin_panel.admin_testimonials'))

@web_admin_bp.route('/testimonials/toggle_feature/<int:testimonial_id>', methods=['POST'])
@admin_required
def toggle_feature_testimonial(testimonial_id):
    """Toggle featured status of a testimonial (disabled in this mode)."""
    flash('Operation not allowed. Featuring is disabled when testimonials are auto-published.', 'warning')
    return redirect(url_for('web_admin_panel.admin_testimonials'))


# About Images Management Routes
@web_admin_bp.route('/about-images')
@admin_required
def admin_about_images():
    """Admin about images management"""
    images = AboutImage.query.order_by(AboutImage.sort_order, AboutImage.created_at).all()
    return render_template('admin/about_images.html', images=images)

@web_admin_bp.route('/about-images/create', methods=['GET', 'POST'])
@admin_required
def create_about_image():
    """Create a new about image"""
    if request.method == 'POST':
        try:
            # Get the highest sort order and add 1
            max_order = db.session.query(db.func.max(AboutImage.sort_order)).scalar() or 0
            
            media_type = request.form.get('media_type', 'image')
            
            image = AboutImage(
                title=request.form.get('title'),
                caption=request.form.get('caption'),
                media_type=media_type,
                sort_order=max_order + 1,
                is_active=request.form.get('is_active') == 'on'
            )
            
            # Handle media upload (image or video)
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'about_images')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    image.image_path = f"uploads/about_images/{filename}"
                else:
                    flash('Media file is required.', 'error')
                    return render_template('admin/edit_about_image.html')
            else:
                flash('Media file is required.', 'error')
                return render_template('admin/edit_about_image.html')
            
            db.session.add(image)
            db.session.commit()
            flash('About image created successfully!', 'success')
            return redirect(url_for('web_admin_panel.admin_about_images'))
            
        except Exception as e:
            flash(f'Error creating about image: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_about_image.html')

@web_admin_bp.route('/about-images/edit/<int:image_id>', methods=['GET', 'POST'])
@admin_required
def edit_about_image(image_id):
    """Edit an about image"""
    image = AboutImage.query.get_or_404(image_id)
    
    if request.method == 'POST':
        try:
            image.title = request.form.get('title')
            image.caption = request.form.get('caption')
            image.media_type = request.form.get('media_type', 'image')
            image.is_active = request.form.get('is_active') == 'on'
            
            # Handle media upload (image or video)
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    # Delete old file if exists
                    if image.image_path:
                        old_file_path = os.path.join(current_app.static_folder, image.image_path)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'about_images')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    image.image_path = f"uploads/about_images/{filename}"
            
            db.session.commit()
            flash('About image updated successfully!', 'success')
            return redirect(url_for('web_admin_panel.admin_about_images'))
            
        except Exception as e:
            flash(f'Error updating about image: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_about_image.html', image=image)

@web_admin_bp.route('/about-images/delete/<int:image_id>', methods=['POST'])
@admin_required
def delete_about_image(image_id):
    """Delete an about image"""
    try:
        image = AboutImage.query.get_or_404(image_id)
        
        # Delete image file if exists
        if image.image_path:
            image_full_path = os.path.join(current_app.static_folder, image.image_path)
            if os.path.exists(image_full_path):
                os.remove(image_full_path)
        
        db.session.delete(image)
        db.session.commit()
        flash('About image deleted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error deleting about image: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('web_admin_panel.admin_about_images'))

@web_admin_bp.route('/about-images/reorder', methods=['POST'])
@admin_required
def reorder_about_images():
    """Reorder about images"""
    try:
        image_ids = request.json.get('image_ids', [])
        
        for index, image_id in enumerate(image_ids):
            image = AboutImage.query.get(image_id)
            if image:
                image.sort_order = index + 1
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Images reordered successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error reordering images: {str(e)}'})

@web_admin_bp.route('/about-images/toggle-active/<int:image_id>', methods=['POST'])
@admin_required
def toggle_about_image_active(image_id):
    """Toggle active status of an about image"""
    try:
        image = AboutImage.query.get_or_404(image_id)
        image.is_active = not image.is_active
        
        db.session.commit()
        status = 'activated' if image.is_active else 'deactivated'
        flash(f'About image {status} successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating about image: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('web_admin_panel.admin_about_images'))

@web_admin_bp.route('/bookings')
@admin_required
def admin_bookings():
    """Admin bookings management"""
    from db.models import Booking, Service
    bookings = Booking.query.order_by(Booking.start_time.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@web_admin_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@admin_required
def admin_cancel_booking(booking_id):
    """Cancel a booking from admin panel"""
    try:
        from db.models import Booking
        booking = Booking.query.get_or_404(booking_id)
        
        if booking.status == 'cancelled':
            flash('Booking is already cancelled.', 'warning')
        else:
            booking.status = 'cancelled'
            db.session.commit()
            flash(f'Booking for {booking.user_name} has been cancelled successfully.', 'success')
        
        return redirect(url_for('web_admin_panel.admin_bookings'))
        
    except Exception as e:
        flash(f'Error cancelling booking: {str(e)}', 'error')
        return redirect(url_for('web_admin_panel.admin_bookings'))

@web_admin_bp.route('/debug/file-system')
@admin_required
def debug_file_system():
    """Debug route to check file system permissions and paths"""
    debug_info = {
        'static_folder': current_app.static_folder,
        'uploads_dir': os.path.join(current_app.static_folder, 'uploads'),
        'home_uploads_dir': os.path.join(current_app.static_folder, 'uploads', 'home'),
        'directories_exist': {},
        'permissions': {},
        'current_home_images': {},
        'file_listings': {}
    }
    
    # Check directory existence
    dirs_to_check = [
        debug_info['static_folder'],
        debug_info['uploads_dir'],
        debug_info['home_uploads_dir']
    ]
    
    for dir_path in dirs_to_check:
        debug_info['directories_exist'][dir_path] = os.path.exists(dir_path)
        if os.path.exists(dir_path):
            try:
                debug_info['permissions'][dir_path] = oct(os.stat(dir_path).st_mode)[-3:]
                debug_info['file_listings'][dir_path] = os.listdir(dir_path) if os.path.isdir(dir_path) else 'Not a directory'
            except Exception as e:
                debug_info['permissions'][dir_path] = f"Error: {e}"
                debug_info['file_listings'][dir_path] = f"Error: {e}"
    
    # Check current home_image settings
    try:
        home_image_settings = SiteSetting.query.filter_by(key='home_image').all()
        for setting in home_image_settings:
            debug_info['current_home_images'][setting.language] = {
                'value': setting.value,
                'file_exists': os.path.exists(os.path.join(current_app.static_folder, setting.value)) if setting.value else False
            }
    except Exception as e:
        debug_info['current_home_images']['error'] = str(e)
    
    return jsonify(debug_info)

@web_admin_bp.route('/upload-home-image', methods=['POST'])
@admin_required
def upload_home_image():
    """Dedicated endpoint for home image upload with enhanced error handling"""
    try:
        current_app.logger.info("Starting home image upload process")
        
        if 'home_image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['home_image']
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Get language from form
        language = request.form.get('language', 'ENG')
        if language not in ['ENG', 'MON']:
            language = 'ENG'
        
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False, 
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }), 400
        
        # Generate unique filename
        import time
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        unique_filename = f"hero_{language.lower()}_{timestamp}{ext}"
        
        # Prepare upload directory
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'home')
        
        # Create directory with proper permissions
        try:
            os.makedirs(upload_dir, mode=0o755, exist_ok=True)
            current_app.logger.info(f"Verified upload directory: {upload_dir}")
        except OSError as e:
            current_app.logger.error(f"Failed to create upload directory: {e}")
            return jsonify({'success': False, 'error': 'Server configuration error'}), 500
        
        # Check if directory is writable
        if not os.access(upload_dir, os.W_OK):
            current_app.logger.error(f"Upload directory not writable: {upload_dir}")
            return jsonify({'success': False, 'error': 'Upload directory not writable'}), 500
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        try:
            file.save(file_path)
            current_app.logger.info(f"File saved to: {file_path}")
        except Exception as e:
            current_app.logger.error(f"File save failed: {e}")
            return jsonify({'success': False, 'error': 'Failed to save file'}), 500
        
        # Verify file was saved
        if not os.path.exists(file_path):
            current_app.logger.error(f"File verification failed: {file_path}")
            return jsonify({'success': False, 'error': 'File verification failed'}), 500
        
        # Set file permissions
        try:
            os.chmod(file_path, 0o644)
            current_app.logger.info(f"Set file permissions for: {file_path}")
        except OSError as e:
            current_app.logger.warning(f"Could not set file permissions: {e}")
        
        # Update database
        try:
            setting = SiteSetting.query.filter_by(key='home_image', language=language).first()
            if not setting:
                setting = SiteSetting(key='home_image', language=language)
                db.session.add(setting)
            
            # Store relative path
            relative_path = f"uploads/home/{unique_filename}"
            setting.value = relative_path
            
            db.session.commit()
            current_app.logger.info(f"Database updated with home image: {relative_path} for {language}")
            
            return jsonify({
                'success': True,
                'message': f'Home image updated successfully for {language}',
                'image_path': relative_path,
                'image_url': url_for('static', filename=relative_path)
            })
            
        except Exception as e:
            current_app.logger.error(f"Database update failed: {e}")
            db.session.rollback()
            # Clean up uploaded file on database error
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({'success': False, 'error': 'Database update failed'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Home image upload error: {e}")
        return jsonify({'success': False, 'error': 'Upload failed'}), 500

@web_admin_bp.route('/test/home-image')
@admin_required  
def test_home_image():
    """Test route to verify home image functionality"""
    try:
        # Get all home image settings
        home_settings = SiteSetting.query.filter_by(key='home_image').all()
        
        results = {
            'settings_found': len(home_settings),
            'settings': {},
            'file_checks': {},
            'static_folder': current_app.static_folder
        }
        
        for setting in home_settings:
            results['settings'][setting.language] = setting.value
            
            if setting.value:
                # Check if file exists
                file_path = os.path.join(current_app.static_folder, setting.value)
                file_exists = os.path.exists(file_path)
                
                results['file_checks'][setting.language] = {
                    'relative_path': setting.value,
                    'absolute_path': file_path,
                    'exists': file_exists,
                    'url': url_for('static', filename=setting.value) if file_exists else None
                }
                
                if file_exists:
                    try:
                        stat_info = os.stat(file_path)
                        results['file_checks'][setting.language].update({
                            'size': stat_info.st_size,
                            'permissions': oct(stat_info.st_mode)[-3:],
                            'last_modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                        })
                    except Exception as e:
                        results['file_checks'][setting.language]['stat_error'] = str(e)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500