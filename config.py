"""
Application configuration module
Centralized configuration for the Flask application
"""

import os
import json


def load_facebook_credentials():
    """Load Facebook credentials from creds.json file"""
    creds_file = "creds.json"
    if os.path.exists(creds_file):
        try:
            with open(creds_file, 'r') as f:
                creds = json.load(f)
                return {
                    'app_id': creds.get('app_id'),
                    'app_secret': creds.get('app_secret'), 
                    'page_id': creds.get('page_id'),
                    'page_access_token': creds.get('page_access_token')
                }
        except Exception as e:
            print(f"⚠️ Error loading Facebook credentials: {e}")
    return {}


class Config:
    """Base configuration class"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-very-secret-key')
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@holisticweb.com')
    MAIL_TIMEOUT = 10
    
    # Facebook Configuration - Load from environment variables or creds.json
    @property
    def facebook_config(self):
        fb_creds = load_facebook_credentials()
        return {
            'FACEBOOK_APP_ID': os.environ.get('FACEBOOK_APP_ID') or fb_creds.get('app_id'),
            'FACEBOOK_APP_SECRET': os.environ.get('FACEBOOK_APP_SECRET') or fb_creds.get('app_secret'),
            'FACEBOOK_DEFAULT_PAGE_ID': os.environ.get('FACEBOOK_DEFAULT_PAGE_ID') or fb_creds.get('page_id'),
            'FACEBOOK_REDIRECT_URI': os.environ.get('FACEBOOK_REDIRECT_URI', 'http://localhost:5000/auth/facebook/callback')
        }
    
    # Set Facebook config as class attributes
    @classmethod
    def _load_facebook_config(cls):
        """Load Facebook configuration from environment or file"""
        fb_creds = load_facebook_credentials()
        cls.FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID') or fb_creds.get('app_id')
        cls.FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET') or fb_creds.get('app_secret')
        cls.FACEBOOK_DEFAULT_PAGE_ID = os.environ.get('FACEBOOK_DEFAULT_PAGE_ID') or fb_creds.get('page_id')
        cls.FACEBOOK_REDIRECT_URI = os.environ.get('FACEBOOK_REDIRECT_URI', 'http://localhost:5000/auth/facebook/callback')
    
    @staticmethod
    def init_app(app):
        """Initialize app-specific configuration"""
        # Load Facebook configuration into app config
        fb_creds = load_facebook_credentials()
        app.config['FACEBOOK_APP_ID'] = os.environ.get('FACEBOOK_APP_ID') or fb_creds.get('app_id')
        app.config['FACEBOOK_APP_SECRET'] = os.environ.get('FACEBOOK_APP_SECRET') or fb_creds.get('app_secret')
        app.config['FACEBOOK_DEFAULT_PAGE_ID'] = os.environ.get('FACEBOOK_DEFAULT_PAGE_ID') or fb_creds.get('page_id')
        app.config['FACEBOOK_REDIRECT_URI'] = os.environ.get('FACEBOOK_REDIRECT_URI', 'http://localhost:5000/auth/facebook/callback')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Set up database path for development
        os.makedirs(app.instance_path, exist_ok=True)
        db_path = os.path.join(app.instance_path, 'data.sqlite')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Set up database path for production
        os.makedirs(app.instance_path, exist_ok=True)
        db_path = os.path.join(app.instance_path, 'data.sqlite')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    return config[os.getenv('FLASK_ENV', 'default')]


def print_config_status(app):
    """Print configuration status for debugging"""
    print("\n" + "="*60)
    print("📁 APPLICATION CONFIGURATION")
    print("="*60)
    print(f"📁 Database path: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    print(f"📁 Instance path: {app.instance_path}")
    print(f"🔧 Debug mode: {app.config.get('DEBUG', False)}")
    print(f"🔒 Secret key: {'✅ Set' if app.config.get('SECRET_KEY') != 'your-very-secret-key' else '⚠️ Default'}")
    
    print("\n📧 EMAIL CONFIGURATION:")
    print(f"   Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
    print(f"   TLS: {app.config['MAIL_USE_TLS']}, SSL: {app.config['MAIL_USE_SSL']}")
    print(f"   Username: {'✅ Set' if app.config['MAIL_USERNAME'] else '❌ Not set'}")
    print(f"   Password: {'✅ Set' if app.config['MAIL_PASSWORD'] else '❌ Not set'}")
    
    print("\n📘 FACEBOOK CONFIGURATION:")
    print(f"   App ID: {'✅ Set' if app.config['FACEBOOK_APP_ID'] else '❌ Not set'}")
    print(f"   App Secret: {'✅ Set' if app.config['FACEBOOK_APP_SECRET'] else '❌ Not set'}")
    print(f"   Redirect URI: {app.config['FACEBOOK_REDIRECT_URI']}")
    print(f"   Default Page ID: {'✅ Set' if app.config['FACEBOOK_DEFAULT_PAGE_ID'] else '❌ Not set'}")
    print("="*60 + "\n")
