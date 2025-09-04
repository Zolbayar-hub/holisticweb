"""
Admin panel setup utilities
"""

from flask import flash, redirect, url_for, session
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from datetime import datetime

from db import db
from db.models import User, Role, GeneratedContent, Booking, Service


def is_admin():
    """Check if current user is admin"""
    return current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role.name == 'admin'


class MyAdminIndexView(AdminIndexView):
    """Custom admin index view with authentication"""
    
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login') if 'user_id' not in session else '/')


class BaseAdminModelView(ModelView):
    """Base admin model view with authentication"""
    
    def is_accessible(self):
        return is_admin()
    
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))


class RoleModelView(BaseAdminModelView):
    """Admin view for Role model"""
    column_list = ('id', 'name')
    form_columns = ('name',)


class UserModelView(BaseAdminModelView):
    """Admin view for User model"""
    column_list = ('id', 'username', 'email', 'role_id')
    column_exclude_list = ['password']
    form_excluded_columns = ['password']
    
    def on_model_change(self, form, model, is_created):
        if is_created and hasattr(form, 'password') and form.password.data:
            model.set_password(form.password.data)


class GeneratedContentModelView(BaseAdminModelView):
    """Admin view for GeneratedContent model"""
    column_list = ('id', 'topic', 'content_preview', 'image_url', 'posted', 'posted_at')
    column_labels = {'content_preview': 'Content Preview'}
    form_columns = ('topic', 'content', 'image_url', 'image_prompt', 'user_name', 'when_post', 'code', 'input_data', 'posted', 'output_data', 'is_reposted')
    column_searchable_list = ['topic', 'content']
    column_filters = ['posted', 'created_at', 'posted_at']
    column_default_sort = ('created_at', True)

    def _format_datetime(self, context, model, name):
        value = getattr(model, name)
        return value.strftime('%Y-%m-%d %H:%M:%S') if value else '-'

    def _format_boolean(self, context, model, name):
        return '✓' if getattr(model, name) else '✗'

    def _format_content_preview(self, context, model, name):
        return (model.content[:100] + '...') if model.content and len(model.content) > 100 else (model.content or '-')

    column_formatters = {
        'created_at': _format_datetime,
        'posted_at': _format_datetime,
        'posted': _format_boolean,
        'content_preview': _format_content_preview
    }
    
    def on_model_change(self, form, model, is_created):
        if model.posted and not model.posted_at:
            model.posted_at = datetime.utcnow()
        elif not model.posted:
            model.posted_at = None


class BookingAdminView(BaseAdminModelView):
    """Admin view for Booking model"""
    column_list = ('id', 'user_name', 'email', 'phone_number', 'service', 'start_time', 'end_time', 'status', 'admin_notes', 'created_at')
    column_filters = ['status', 'service', 'start_time', 'created_at']
    form_columns = ('user_name', 'email', 'phone_number', 'service', 'start_time', 'end_time', 'status', 'admin_notes')


class ServiceAdminView(BaseAdminModelView):
    """Admin view for Service model"""
    column_list = ('id', 'name', 'price', 'description')
    column_searchable_list = ['name']
    column_filters = ['price']
    form_columns = ('name', 'description', 'price', 'duration')


def setup_admin(app):
    """Set up Flask-Admin with all model views"""
    
    admin = Admin(
        app, 
        name='Admin Panel', 
        template_mode='bootstrap4', 
        index_view=MyAdminIndexView()
    )
    
    # Add model views
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(RoleModelView(Role, db.session))
    admin.add_view(GeneratedContentModelView(GeneratedContent, db.session))
    admin.add_view(BookingAdminView(Booking, db.session))
    admin.add_view(ServiceAdminView(Service, db.session))
    
    print("✅ Flask-Admin setup complete")
    
    return admin
