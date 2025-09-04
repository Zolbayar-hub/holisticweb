"""
Application configuration module
Centralized configuration for the Flask application
"""

import os


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
    
    @staticmethod
    def init_app(app):
        """Initialize app-specific configuration"""
        pass


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
    print("="*60 + "\n")
