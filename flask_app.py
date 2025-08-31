from dotenv import load_dotenv
# Load .flaskenv file specifically
load_dotenv('.flaskenv')
# Also load .env if it exists (for overrides)
load_dotenv()

from flask import Flask, render_template, redirect, url_for, flash, request, session, send_from_directory
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import markdown as md
from db import db
from flask_migrate import Migrate
from datetime import datetime
import os
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from db.models import User, Role, GeneratedContent, Booking, Service, SiteSetting, EmailTemplate
from werkzeug.security import generate_password_hash
from flask_babel import Babel
from flask_login import LoginManager, current_user
from routes.booking import booking_bp


# Optional: CORS for local development
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("Flask-CORS not installed. Skipping...")

# ---- Flask Setup ----
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ---- Mail Config ----
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@holisticweb.com')
app.config['MAIL_TIMEOUT'] = 10  # Add 10 second timeout

# Debug email configuration
print("📧 Email Configuration:")
print(f"   Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
print(f"   TLS: {app.config['MAIL_USE_TLS']}, SSL: {app.config['MAIL_USE_SSL']}")
print(f"   Username: {'✅ Set' if app.config['MAIL_USERNAME'] else '❌ Not set'}")
print(f"   Password: {'✅ Set' if app.config['MAIL_PASSWORD'] else '❌ Not set'}")

mail = Mail(app)

# Make mail available globally for blueprints
app.mail = mail

# ---- Test Mail Route ----
@app.route("/send-email")
def send_email():
    try:
        msg = Message("Test Email", recipients=["dambazolbayar@gmail.com"])
        msg.body = "This is a test email from Flask."
        mail.send(msg)
        return "Email sent!"
    except Exception as e:
        return f"Email failed: {e}"

# ---- Enable CORS ----
if CORS_AVAILABLE:
    CORS(app, supports_credentials=True)

# ---- Init DB + Migrate + Babel ----
db.init_app(app)
migrate = Migrate(app, db)
babel = Babel(app)

# ---- Login Manager ----
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---- Register Blueprints ----
from routes.auth import auth_bp
from routes.admin import admin_bp
app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp)

# ---- Error Handlers ----
@app.errorhandler(500)
def internal_error(error):
    print(f"Internal server error: {error}")
    return f"Internal Server Error: {error}", 500

@app.errorhandler(404)
def not_found_error(error):
    print(f"404 error: {error}")
    return f"Not Found: {error}", 404

# ---- Health Check ----
@app.route('/')
def home():
    services = Service.query.all()
    
    # Get site settings
    site_settings = SiteSetting.query.all()
    settings = {setting.key: setting.value for setting in site_settings}
    
    return render_template('home.html', services=services, settings=settings)

@app.route('/book')
def book_redirect():
    """Redirect to the booking page for easy access"""
    return redirect(url_for('booking_bp.booking_page'))

@app.route('/bookings/new')
def old_booking_redirect():
    """Redirect old booking URL to new booking page"""
    return redirect(url_for('booking_bp.create_booking'))

@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'Server is running'}, 200

# ---- Markdown filter ----
@app.template_filter('markdown')
def markdown_filter(text):
    return md.markdown(text or "", extensions=['fenced_code', 'codehilite', 'tables'])

# ---- Static Images ----
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(app.static_folder, 'images'), filename)

# ---- DB Init ----
with app.app_context():
    try:
        # Try to create all tables
        db.create_all()
        
        # Test if booking table has service_id column
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'booking' in inspector.get_table_names():
            columns = inspector.get_columns('booking')
            column_names = [col['name'] for col in columns]
            
            if 'service_id' not in column_names:
                print("Missing service_id column. Recreating database...")
                db.drop_all()
                db.create_all()
                print("Database recreated with service_id column.")
                
    except Exception as e:
        print(f"Database initialization error: {e}")
        print("Recreating database...")
        try:
            db.drop_all()
            db.create_all()
            print("Database recreated successfully.")
        except Exception as e2:
            print(f"Failed to recreate database: {e2}")

# ---- Helpers ----
def is_admin():
    return current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role.name == 'admin'

# ---- Flask-Admin ----
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login') if 'user_id' not in session else '/')

admin = Admin(app, name='Admin Panel', template_mode='bootstrap4', index_view=MyAdminIndexView())

class RoleModelView(ModelView):
    column_list = ('id', 'name')
    form_columns = ('name',)
    def is_accessible(self): return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))

class UserModelView(ModelView):
    column_list = ('id', 'username', 'email', 'role_id')
    column_exclude_list = ['password']
    form_excluded_columns = ['password']
    def is_accessible(self): return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))
    def on_model_change(self, form, model, is_created):
        if is_created and hasattr(form, 'password') and form.password.data:
            model.set_password(form.password.data)

class GeneratedContentModelView(ModelView):
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

    def is_accessible(self): return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))
    def on_model_change(self, form, model, is_created):
        if model.posted and not model.posted_at:
            model.posted_at = datetime.utcnow()
        elif not model.posted:
            model.posted_at = None

class BookingAdminView(ModelView):
    column_list = ('id', 'user_name', 'email', 'service', 'start_time', 'end_time', 'status', 'admin_notes', 'created_at')
    column_filters = ['status', 'service', 'start_time', 'created_at']
    form_columns = ('user_name', 'email', 'service', 'start_time', 'end_time', 'status', 'admin_notes')
    def is_accessible(self): return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))
    
class ServiceAdminView(ModelView):
    column_list = ('id', 'name', 'price', 'description')
    column_searchable_list = ['name']
    column_filters = ['price']
    form_columns = ('name', 'description', 'price', 'duration')

    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))



# ✅ Only keep these three
admin.add_view(UserModelView(User, db.session))
admin.add_view(RoleModelView(Role, db.session))
admin.add_view(GeneratedContentModelView(GeneratedContent, db.session))
admin.add_view(BookingAdminView(Booking, db.session))
admin.add_view(ServiceAdminView(Service, db.session))


# ---- Run ----
if __name__ == '__main__':
    with app.app_context():
        try:
            # Try to create all tables
            db.create_all()
            
            # Test if booking table has service_id column
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'booking' in inspector.get_table_names():
                columns = inspector.get_columns('booking')
                column_names = [col['name'] for col in columns]
                
                if 'service_id' not in column_names:
                    print("Missing service_id column. Recreating database...")
                    db.drop_all()
                    db.create_all()
                    print("Database recreated with service_id column.")
                    
        except Exception as e:
            print(f"Database initialization error: {e}")
            print("Recreating database...")
            try:
                db.drop_all()
                db.create_all()
                print("Database recreated successfully.")
            except Exception as e2:
                print(f"Failed to recreate database: {e2}")

        # Insert roles if missing
        if not Role.query.first():
            roles = [
                Role(id=1, name='viewer'),
                Role(id=2, name='editor'),
                Role(id=3, name='admin')
            ]
            db.session.bulk_save_objects(roles)
            db.session.commit()

        # Insert admin user if missing
        if not User.query.filter_by(email='admin@example.com').first():
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role_id=3
            )
            db.session.add(admin_user)
            db.session.commit()

        # Insert default site settings if missing
        default_settings = [
            ('hero_title', 'Holistic Therapy', 'Main hero section title'),
            ('hero_subtitle', 'Discover the power of integrated healing for your mind, body, and spirit. Our comprehensive approach combines traditional wisdom with modern techniques to help you achieve optimal wellness.', 'Hero section subtitle'),
            ('about_title', 'Our Holistic Approach', 'About section title'),
            ('about_text_1', 'At Holistic Therapy, we believe that true healing encompasses all aspects of the human experience. Our integrated approach addresses the interconnected nature of mind, body, and spirit.', 'About section paragraph 1'),
            ('about_text_2', 'Our experienced practitioners work with you to create personalized treatment plans that honor your unique journey and support your natural healing processes.', 'About section paragraph 2'),
            ('about_text_3', 'Whether you\'re seeking relief from stress, looking to improve your overall wellness, or embarking on a journey of personal growth, we\'re here to support you every step of the way.', 'About section paragraph 3'),
            ('contact_title', 'Begin Your Healing Journey', 'Contact section title'),
            ('contact_text', 'Ready to take the first step? Contact us to schedule a consultation and discover how our holistic approach can support your wellness goals.', 'Contact section text'),
            ('footer_text', 'Holistic Therapy. All rights reserved. | Healing Mind, Body & Spirit', 'Footer text'),
        ]
        
        for key, value, description in default_settings:
            if not SiteSetting.query.filter_by(key=key).first():
                setting = SiteSetting(key=key, value=value, description=description)
                db.session.add(setting)
        
        # Insert default email template if missing
        if not EmailTemplate.query.filter_by(name='booking_confirmation').first():
            template = EmailTemplate(
                name='booking_confirmation',
                subject='🌟 Booking Confirmation - {service_name}',
                body="""Hello {user_name},

Thank you for booking with HolisticWeb! ✨

📌 Service: {service_name}
💰 Price: ${service_price}
🕒 Start: {start_time}
🕒 End: {end_time}

We look forward to seeing you!

Best regards,
- The HolisticWeb Team

If you need to reschedule or have any questions, please contact us.""",
                description='Default booking confirmation email sent to customers'
            )
            db.session.add(template)
        
        # Insert default services if missing
        if not Service.query.first():
            default_services = [
                Service(name='Holistic Therapy Session', description='A comprehensive therapy session addressing mind, body, and spirit wellness through integrated healing techniques.', price=120.00, duration=90),
                Service(name='Stress Relief Therapy', description='Specialized therapy focused on reducing stress and promoting relaxation through holistic approaches.', price=90.00, duration=60),
                Service(name='Energy Healing Session', description='Therapeutic session designed to balance and restore your natural energy flow for optimal wellness.', price=100.00, duration=75),
            ]
            
            for service in default_services:
                db.session.add(service)
        
        db.session.commit()


    app.run(
        host='127.0.0.1',
        port=5000,
        debug=app.config['DEBUG'],
        threaded=True
    )

