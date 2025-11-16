# Modular Flask Architecture

This Flask application uses a **modular feature-based architecture** where each feature is completely standalone and can be easily added or removed without affecting other features.

## Architecture Overview

```
features/
├── feature_manager.py          # Central feature management
├── booking/                    # Booking system feature
│   ├── booking.py             # All booking routes & logic
│   ├── templates/             # Booking HTML templates
│   ├── static/                # Booking CSS & JS files
│   └── README.md              # Feature documentation
├── testimonials/              # Testimonials feature
│   ├── testimonials.py        # All testimonial routes & logic
│   ├── templates/             # Testimonial HTML templates  
│   ├── static/                # Testimonial CSS & JS files
│   └── README.md              # Feature documentation
└── [other features...]
```

## Benefits

✅ **Easy to Remove**: Delete a feature folder = remove entire feature  
✅ **No Dependencies**: Features don't depend on each other  
✅ **Self-Contained**: Each feature has its own routes, templates, and static files  
✅ **Easy to Add**: Drop in a new feature folder and register it  
✅ **Clean Separation**: No mixing of feature code  
✅ **Maintainable**: Each feature can be developed and tested independently  

## How to Use Features

### 1. Adding a New Feature

1. Create a new folder in `features/`
2. Create the feature file with blueprint
3. Add templates and static files
4. Register in `feature_manager.py`

Example structure:
```
features/new_feature/
├── new_feature.py      # Blueprint with routes
├── templates/          # HTML templates
├── static/            # CSS/JS files
└── README.md          # Documentation
```

### 2. Removing a Feature

**Method 1: Complete Removal**
```bash
# Remove the entire feature
rm -rf features/booking/

# Remove from feature_manager.py registration
# Remove any imports in app_factory.py
```

**Method 2: Disable Feature**
```python
# In feature_manager.py, comment out the registration:
# feature_manager.register_feature('booking', booking_bp)
```

### 3. Feature Template

Each feature should follow this template:

```python
# features/my_feature/my_feature.py
from flask import Blueprint

# Create blueprint with custom folders
my_feature_bp = Blueprint(
    'my_feature', 
    __name__, 
    url_prefix='/my-feature',
    template_folder='templates',
    static_folder='static',
    static_url_path='/my-feature/static'
)

@my_feature_bp.route('/')
def index():
    return render_template('my_feature.html')

def get_feature_info():
    return {
        "name": "My Feature",
        "version": "1.0.0",
        "description": "Description of what this feature does",
        "dependencies": ["Flask-Extension1"],
        "routes": ["/my-feature/"],
        "templates": ["my_feature.html"],
        "static_files": ["my_feature.css", "my_feature.js"]
    }
```

## Current Features

| Feature | Status | Description | Dependencies |
|---------|--------|-------------|--------------|
| **Booking** | ✅ Active | Complete booking system with calendar, notifications | Flask-Mail, pytz, twilio |
| **Testimonials** | ✅ Active | Testimonial submission and management | Flask-Mail, Flask-Login |
| **Admin** | ✅ Active | Administrative dashboard and management | Flask-Login |
| **Auth** | ✅ Active | User authentication and registration | Flask-Login |

## Feature Manager

The `feature_manager.py` provides centralized feature management:

```python
from features.feature_manager import feature_manager

# List all features
features = feature_manager.list_features()

# Get feature info
info = feature_manager.get_feature_info('booking')

# Register new feature
feature_manager.register_feature('my_feature', my_bp)
```

## Migration Guide

### From Old Structure to Modular

1. **Identify Features**: Look at your current routes and group related functionality
2. **Create Feature Folders**: Move routes, templates, and static files
3. **Update Imports**: Change imports to use feature paths
4. **Update Registration**: Use feature manager instead of direct blueprint registration
5. **Test**: Ensure each feature works independently

### Example Migration

**Before** (Monolithic):
```
routes/booking.py
templates/book.html
static/book.css
```

**After** (Modular):
```
features/booking/
├── booking.py         # From routes/booking.py
├── templates/
│   └── book.html      # From templates/book.html
└── static/
    └── book.css       # From static/book.css
```

## Best Practices

1. **Self-Contained**: Each feature should work independently
2. **Clear Dependencies**: Document what each feature needs
3. **Consistent Structure**: Follow the template structure
4. **Good Documentation**: Include README.md for each feature
5. **Version Control**: Each feature can have its own versioning
6. **Testing**: Test features in isolation

## Troubleshooting

**Q: Feature not loading?**
- Check if it's registered in `feature_manager.py`
- Verify all dependencies are installed
- Check for import errors

**Q: Templates not found?**
- Ensure `template_folder='templates'` in blueprint
- Check template file paths are correct

**Q: Static files not serving?**
- Ensure `static_folder='static'` in blueprint
- Check `static_url_path` is set correctly

**Q: Want to disable a feature temporarily?**
- Comment out the registration in `feature_manager.py`
- Restart the application
