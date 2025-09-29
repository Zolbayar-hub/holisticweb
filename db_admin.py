"""
Database Admin Interface
A separate Flask-Admin powered database administration interface
Accessible at /db-admin endpoint
"""

from flask import Flask, request, redirect, url_for, flash, session
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from flask_login import current_user
from wtforms import SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from flask_babel import Babel, gettext as _
from db import db
from db.models import (
    User, Role, Service, Booking, SiteSetting, 
    EmailTemplate, Testimonial, AboutImage, GeneratedContent
)


# Helper: check admin access
def is_admin():
    return (
        current_user.is_authenticated
        and current_user.role
        and current_user.role.name in ['admin', 'owner']
    )


# Custom Admin Home View
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not is_admin():
            flash(_('Access denied. Admin role required.'), 'error')
            return redirect(url_for('auth.login') if 'user_id' not in session else url_for('main.home'))
        return super().index()

    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash(_('Access denied. Admin role required.'), 'error')
        return redirect(url_for('auth.login') if 'user_id' not in session else url_for('main.home'))


# Base model view with auth
class SecureModelView(ModelView):
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash(_('Database admin access requires admin privileges.'), 'error')
        # Make sure we redirect to login, not web_admin
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.home'))


class UserModelView(SecureModelView):
    column_list = ['id', 'username', 'email', 'role', 'is_paid', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['role', 'is_paid', 'created_at']
    column_editable_list = ['is_paid']
    column_labels = {
        'is_paid': 'Paid Status',
        'role': 'Role',
        'created_at': 'Created'
    }
    form_excluded_columns = ['password', 'bookings', 'created_at', 'updated_at']

    form_extra_fields = {
        'role_id': SelectField(
            _('Role'),
            coerce=int,
            validators=[DataRequired()],
            widget=Select2Widget()
        ),
        'new_password': TextAreaField(_('New Password (leave blank to keep current)'))
    }

    def create_model(self, form):
        try:
            model = self.model()
            form.populate_obj(model)
            if form.new_password.data:
                model.set_password(form.new_password.data)
            self.session.add(model)
            self._on_model_change(form, model, True)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(_('Failed to create record. %(err)s', err=str(ex)), 'error')
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, True)
        return model

    def update_model(self, form, model):
        try:
            form.populate_obj(model)
            if form.new_password.data:
                model.set_password(form.new_password.data)
            self._on_model_change(form, model, False)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(_('Failed to update record. %(err)s', err=str(ex)), 'error')
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, False)
        return True


class UserPaidTestModelView(UserModelView):
    """Filtered view showing only paid users"""
    
    def get_query(self):
        return self.session.query(self.model).filter(self.model.is_paid == True)

    def get_count_query(self):
        return self.session.query(db.func.count('*')).filter(self.model.is_paid == True)


class ServiceModelView(SecureModelView):
    column_list = ['id', 'name', 'price', 'duration', 'language']
    column_searchable_list = ['name', 'description']
    column_filters = ['language']
    column_editable_list = ['price']
    form_excluded_columns = ['image_path', 'bookings']
    form_widget_args = {'description': {'rows': 4}}


class BookingModelView(SecureModelView):
    column_list = ['id', 'user_name', 'email', 'service', 'start_time', 'status', 'created_at']
    column_searchable_list = ['user_name', 'email', 'phone_number']
    column_filters = ['status', 'start_time', 'created_at']
    column_editable_list = ['status']
    column_labels = {
        'user_name': _('Client Name'),
        'start_time': _('Appointment Start'),
        'end_time': _('Appointment End'),
        'phone_number': _('Phone'),
        'admin_notes': _('Admin Notes')
    }


class TestimonialModelView(SecureModelView):
    column_list = ['id', 'client_name', 'rating', 'is_approved', 'is_featured', 'created_at']
    column_searchable_list = ['client_name', 'testimonial_text', 'client_title']
    column_filters = ['rating', 'is_approved', 'is_featured', 'created_at']
    column_editable_list = ['is_approved', 'is_featured']
    form_widget_args = {'testimonial_text': {'rows': 4}}


class SiteSettingModelView(SecureModelView):
    column_list = ['id', 'key', 'value', 'language', 'description', 'updated_at']
    column_searchable_list = ['key', 'value', 'description']
    column_filters = ['language', 'key']
    column_editable_list = ['value']
    column_labels = {
        'key': 'Key',
        'value': 'Value',
        'description': 'Description',
        'language': 'Language'
    }
    form_widget_args = {
        'value': {'rows': 4, 'style': 'font-family: monospace;'},
        'description': {'rows': 2}
    }
    column_formatters = {
        'value': lambda view, context, model, name: (
            model.value[:50] + '...' if model.value and len(model.value) > 50 
            else model.value or ''
        )
    }
    
    # Make the form more user-friendly
    form_excluded_columns = ['created_at', 'updated_at']


class EmailTemplateModelView(SecureModelView):
    column_list = ['id', 'name', 'subject', 'updated_at']
    column_searchable_list = ['name', 'subject', 'body']
    column_filters = ['name']
    form_widget_args = {'body': {'rows': 10}}


class AboutImageModelView(SecureModelView):
    column_list = ['id', 'title', 'sort_order', 'is_active', 'created_at']
    column_searchable_list = ['title', 'caption']
    column_filters = ['is_active', 'created_at']
    column_editable_list = ['is_active', 'sort_order']
    form_excluded_columns = ['image_path']


class GeneratedContentModelView(SecureModelView):
    column_list = ['id', 'topic', 'posted', 'created_at', 'posted_at']
    column_searchable_list = ['topic', 'content', 'user_name']
    column_filters = ['posted', 'is_reposted', 'created_at']
    column_editable_list = ['posted']
    form_widget_args = {
        'content': {'rows': 8},
        'input_data': {'rows': 4},
        'output_data': {'rows': 4}
    }


class RoleModelView(SecureModelView):
    column_list = ['id', 'name', 'created_at']
    column_searchable_list = ['name']
    can_delete = False  # Prevent deletion of system roles


# Add more ModelViews as needed for other tables
def init_db_admin(app):
    """Initialize the Database Admin Panel with Flask-Admin"""
    try:
        print("🗄️ Initializing Database Admin Panel...")
        
        # Create admin with specific configuration to avoid conflicts
        db_admin = Admin(
            app,
            name='Database Admin',
            template_mode='bootstrap4',
            index_view=MyAdminIndexView(endpoint='db_admin', url='/db_admin'),
            static_url_path='/admin/static'
        )

        print("📊 Adding model views to Database Admin...")
        
        # Add model views to match the navigation structure
        # Core User Management
        db_admin.add_view(UserPaidTestModelView(User, db.session, name='User Paid', endpoint='db_admin_user_paid_test'))
        db_admin.add_view(UserModelView(User, db.session, name='User', endpoint='db_admin_users'))
        db_admin.add_view(RoleModelView(Role, db.session, name='Role', endpoint='db_admin_roles'))
        
        # Configuration and Settings
        db_admin.add_view(SiteSettingModelView(SiteSetting, db.session, name='Config', endpoint='db_admin_config'))
        
        # Business Operations
        db_admin.add_view(ServiceModelView(Service, db.session, name='Service', endpoint='db_admin_services'))
        db_admin.add_view(BookingModelView(Booking, db.session, name='Booking', endpoint='db_admin_bookings'))
        
        # Content Management
        db_admin.add_view(TestimonialModelView(Testimonial, db.session, name='Testimonial', endpoint='db_admin_testimonials'))
        db_admin.add_view(AboutImageModelView(AboutImage, db.session, name='About Image', endpoint='db_admin_images'))
        db_admin.add_view(EmailTemplateModelView(EmailTemplate, db.session, name='Email Template', endpoint='db_admin_emails'))
        db_admin.add_view(GeneratedContentModelView(GeneratedContent, db.session, name='Generated Content', endpoint='db_admin_content'))

        print("✅ Database Admin Panel initialized with all model views")
        return db_admin
        
    except Exception as e:
        print(f"❌ Error initializing Database Admin Panel: {e}")
        import traceback
        traceback.print_exc()
        return None

