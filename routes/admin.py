from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from db import db
from db.models import Service, SiteSetting, EmailTemplate
from werkzeug.utils import secure_filename
import os
from functools import wraps

admin_bp = Blueprint('admin_panel', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def admin_panel():
    """Main admin panel dashboard"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/services')
@admin_required
def admin_services():
    """Admin services management"""
    services = Service.query.all()
    return render_template('admin/services.html', services=services)

@admin_bp.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
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
            return redirect(url_for('admin_panel.admin_services'))
            
        except Exception as e:
            flash(f'Error updating service: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_service.html', service=service)

@admin_bp.route('/services/create', methods=['GET', 'POST'])
@admin_required
def create_service():
    """Create a new service"""
    if request.method == 'POST':
        try:
            service = Service(
                name=request.form.get('name'),
                description=request.form.get('description'),
                price=float(request.form.get('price')),
                duration=int(request.form.get('duration'))
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
            return redirect(url_for('admin_panel.admin_services'))
            
        except Exception as e:
            flash(f'Error creating service: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_service.html')

@admin_bp.route('/services/delete/<int:service_id>', methods=['POST'])
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
    
    return redirect(url_for('admin_panel.admin_services'))

@admin_bp.route('/emails')
@admin_required
def admin_emails():
    """Admin email templates management"""
    templates = EmailTemplate.query.all()
    return render_template('admin/emails.html', templates=templates)

@admin_bp.route('/emails/edit/<int:template_id>', methods=['GET', 'POST'])
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
            return redirect(url_for('admin_panel.admin_emails'))
            
        except Exception as e:
            flash(f'Error updating email template: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_email.html', template=template)

@admin_bp.route('/emails/create', methods=['GET', 'POST'])
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
            return redirect(url_for('admin_panel.admin_emails'))
            
        except Exception as e:
            flash(f'Error creating email template: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/edit_email.html')

@admin_bp.route('/emails/delete/<int:template_id>', methods=['POST'])
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
    
    return redirect(url_for('admin_panel.admin_emails'))

@admin_bp.route('/settings')
@admin_required
def admin_settings():
    """Admin site settings management"""
    settings = SiteSetting.query.all()
    
    # Convert to dictionary for easier access
    settings_dict = {setting.key: setting.value for setting in settings}
    
    return render_template('admin/settings.html', settings=settings, settings_dict=settings_dict)

@admin_bp.route('/settings/update', methods=['POST'])
@admin_required
def update_settings():
    """Update site settings"""
    try:
        # Get all form data
        for key, value in request.form.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                
                # Find or create setting
                setting = SiteSetting.query.filter_by(key=setting_key).first()
                if not setting:
                    setting = SiteSetting(key=setting_key)
                    db.session.add(setting)
                
                setting.value = value
        
        # Handle home page image upload
        if 'home_image' in request.files:
            file = request.files['home_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'home')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # Update or create home_image setting
                setting = SiteSetting.query.filter_by(key='home_image').first()
                if not setting:
                    setting = SiteSetting(key='home_image')
                    db.session.add(setting)
                setting.value = f"uploads/home/{filename}"
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_panel.admin_settings'))

@admin_bp.route('/upload-image', methods=['POST'])
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
