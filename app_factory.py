"""
Application factory module
Creates and configures the Flask application
"""

import os
from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_babel import Babel
from flask_login import LoginManager
from flask_admin import Admin

from config import get_config, print_config_status
from db import db
from db.models import User
from routes.send_sms import test_sms_connection


def create_app(config_name=None):
    """Application factory function"""
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv('.flaskenv')
        load_dotenv()
    except ImportError:
        print("python-dotenv not available. Using system environment variables.")
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    config_class = get_config()
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Print configuration status
    print_config_status(app)
    
    # Test SMS service on startup
    print("📱 SMS SERVICE CHECK:")
    test_sms_connection()
    print()
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Initialize database
    initialize_database(app)
    
    return app


def initialize_extensions(app):
    """Initialize Flask extensions"""
    
    # Database
    db.init_app(app)
    
    # Migration
    migrate = Migrate(app, db)
    
    # Babel for internationalization
    babel = Babel(app)
    
    # Mail
    mail = Mail(app)
    app.mail = mail  # Make mail available globally for blueprints
    
    # Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # CORS (if available)
    try:
        from flask_cors import CORS
        CORS(app, supports_credentials=True)
        print("✅ CORS enabled")
    except ImportError:
        print("⚠️ Flask-CORS not installed. Skipping...")
    
    # Flask-Admin
    from utils.admin_setup import setup_admin
    setup_admin(app)


def register_blueprints(app):
    """Register application blueprints"""
    
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.booking import booking_bp
    from routes.testimony import testimony_bp
    from routes.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(testimony_bp)
    app.register_blueprint(admin_bp)
    
    print("✅ Blueprints registered")


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        print(f"404 error: {error}")
        return f"Not Found: {error}", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        print(f"Internal server error: {error}")
        return f"Internal Server Error: {error}", 500


def register_template_filters(app):
    """Register custom template filters"""
    
    import markdown as md
    
    @app.template_filter('markdown')
    def markdown_filter(text):
        return md.markdown(text or "", extensions=['fenced_code', 'codehilite', 'tables'])


def initialize_database(app):
    """Initialize database and default data"""
    
    with app.app_context():
        try:
            # Ensure the instance directory exists
            os.makedirs(app.instance_path, exist_ok=True)
            
            # Try to create all tables
            db.create_all()
            
            # Check and fix database schema if needed
            check_database_schema()
            
            # Insert default data
            insert_default_data()
            
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            print("🔄 Recreating database...")
            try:
                os.makedirs(app.instance_path, exist_ok=True)
                db.drop_all()
                db.create_all()
                insert_default_data()
                print("✅ Database recreated successfully")
            except Exception as e2:
                print(f"❌ Failed to recreate database: {e2}")


def check_database_schema():
    """Check and fix database schema issues"""
    
    from sqlalchemy import inspect
    from db.models import Booking
    
    inspector = inspect(db.engine)
    if 'booking' in inspector.get_table_names():
        columns = inspector.get_columns('booking')
        column_names = [col['name'] for col in columns]
        
        if 'service_id' not in column_names:
            print("⚠️ Missing service_id column. Recreating database...")
            db.drop_all()
            db.create_all()
            print("✅ Database recreated with service_id column")


def insert_default_data():
    """Insert default data if missing"""
    
    from db.models import Role, User, SiteSetting, EmailTemplate, Service
    from werkzeug.security import generate_password_hash
    
    # Insert roles if missing
    if not Role.query.first():
        roles = [
            Role(id=1, name='viewer'),
            Role(id=2, name='editor'),
            Role(id=3, name='admin')
        ]
        db.session.bulk_save_objects(roles)
        db.session.commit()
        print("✅ Default roles created")
    
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
        print("✅ Default admin user created")
    
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
    
    settings_added = False
    for key, value, description in default_settings:
        if not SiteSetting.query.filter_by(key=key).first():
            setting = SiteSetting(key=key, value=value, description=description)
            db.session.add(setting)
            settings_added = True
    
    if settings_added:
        db.session.commit()
        print("✅ Default site settings created")
    
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
        db.session.commit()
        print("✅ Default email template created")
    
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
        print("✅ Default services created")
