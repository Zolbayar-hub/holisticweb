"""
Feature Manager
Manages all standalone features and provides easy registration/removal
"""

class FeatureManager:
    def __init__(self, app=None):
        self.app = app
        self.features = {}
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
    
    def register_feature(self, feature_name, blueprint, dependencies=None):
        """Register a feature with its blueprint and dependencies"""
        self.features[feature_name] = {
            'blueprint': blueprint,
            'dependencies': dependencies or [],
            'registered': False
        }
        
        # Register the blueprint
        self.app.register_blueprint(blueprint)
        self.features[feature_name]['registered'] = True
        
        print(f"✅ Feature '{feature_name}' registered successfully")
    
    def unregister_feature(self, feature_name):
        """Unregister a feature (removes from registry, but Flask doesn't support blueprint removal)"""
        if feature_name in self.features:
            self.features[feature_name]['registered'] = False
            print(f"⚠️ Feature '{feature_name}' marked as unregistered (restart required)")
        else:
            print(f"❌ Feature '{feature_name}' not found")
    
    def list_features(self):
        """List all registered features"""
        return self.features
    
    def get_feature_info(self, feature_name):
        """Get information about a specific feature"""
        return self.features.get(feature_name)

# Global feature manager instance
feature_manager = FeatureManager()

def register_all_features(app):
    """Register all available features"""
    feature_manager.init_app(app)
    
    # Register Booking Feature
    try:
        from features.booking.booking import booking_bp
        feature_manager.register_feature('booking', booking_bp, ['Flask-Mail', 'pytz', 'twilio'])
    except ImportError as e:
        print(f"⚠️ Booking feature not available: {e}")
        # Fallback to original booking
        try:
            from routes.booking import booking_bp as original_booking_bp
            feature_manager.register_feature('booking_original', original_booking_bp, ['Flask-Mail', 'pytz', 'twilio'])
        except ImportError:
            print(f"⚠️ Original booking also not available")
    
    # Register Testimonials Feature
    try:
        from features.testimonials.testimonials import testimony_bp
        feature_manager.register_feature('testimonials', testimony_bp, ['Flask-Mail', 'Flask-Login'])
    except ImportError as e:
        print(f"⚠️ Testimonials feature not available: {e}")
        # Fallback to original testimonials
        try:
            from routes.testimony import testimony_bp as original_testimony_bp
            feature_manager.register_feature('testimonials_original', original_testimony_bp, ['Flask-Mail', 'Flask-Login'])
        except ImportError:
            print(f"⚠️ Original testimonials also not available")
    
    # Register Admin Feature
    try:
        from routes.web_admin import web_admin_bp
        feature_manager.register_feature('admin', web_admin_bp, ['Flask-Login'])
    except ImportError as e:
        print(f"⚠️ Admin feature not available: {e}")
    
    # Register Auth Feature
    try:
        from routes.auth import auth_bp
        feature_manager.register_feature('auth', auth_bp, ['Flask-Login'])
    except ImportError as e:
        print(f"⚠️ Auth feature not available: {e}")

    # Register Blog Feature
    try:
        from features.blog.blog import blog_bp
        feature_manager.register_feature('blog', blog_bp, [])
    except ImportError as e:
        print(f"⚠️ Blog feature not available: {e}")
    
    return feature_manager
