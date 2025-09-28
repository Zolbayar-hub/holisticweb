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
        return redirect(url_for('auth.login'))


class UserModelView(SecureModelView):
    column_list = ['id', 'username', 'email', 'role', 'is_paid', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['role', 'is_paid', 'created_at']
    column_editable_list = ['is_paid']
    form_excluded_columns = ['password', 'bookings']

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
    column_list = ['id', 'key', 'language', 'updated_at']
    column_searchable_list = ['key', 'value']
    column_filters = ['language', 'key']
    form_widget_args = {'value': {'rows': 6}}


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
    db_admin = Admin(
        app,
        name=_('Database Admin'),
        template_mode='bootstrap4',
        index_view=MyAdminIndexView(endpoint='db_admin', url='/db_admin')
    )

    # Add model views - Database Administration Only
    db_admin.add_view(UserModelView(User, db.session, name=_('Users'), category=_('User Management')))
    db_admin.add_view(RoleModelView(Role, db.session, name=_('Roles'), category=_('User Management')))
    db_admin.add_view(BookingModelView(Booking, db.session, name=_('Bookings'), category=_('Data Management')))
    db_admin.add_view(GeneratedContentModelView(GeneratedContent, db.session, name=_('Generated Content'), category=_('AI Content')))
    
    # Raw database views for troubleshooting (read-only recommended)
    db_admin.add_view(SiteSettingModelView(SiteSetting, db.session, name=_('Site Settings (Raw)'), category=_('Raw Data')))
    db_admin.add_view(ServiceModelView(Service, db.session, name=_('Services (Raw)'), category=_('Raw Data')))
    db_admin.add_view(TestimonialModelView(Testimonial, db.session, name=_('Testimonials (Raw)'), category=_('Raw Data')))
    db_admin.add_view(AboutImageModelView(AboutImage, db.session, name=_('About Images (Raw)'), category=_('Raw Data')))
    db_admin.add_view(EmailTemplateModelView(EmailTemplate, db.session, name=_('Email Templates (Raw)'), category=_('Raw Data')))

    return db_admin

