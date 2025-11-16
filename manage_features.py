#!/usr/bin/env python3
"""
Feature Management CLI
Easy command-line interface to manage modular features
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

def list_features():
    """List all available features"""
    features_dir = Path("features")
    if not features_dir.exists():
        print("❌ Features directory not found")
        return
    
    print("📋 Available Features:")
    print("=" * 50)
    
    for feature_dir in features_dir.iterdir():
        if feature_dir.is_dir() and feature_dir.name != "__pycache__":
            readme_path = feature_dir / "README.md"
            if readme_path.exists():
                # Try to extract description from README
                try:
                    with open(readme_path, 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            if line.startswith("**") and "standalone" in line.lower():
                                description = line.strip("*").strip()
                                break
                        else:
                            description = "Feature available"
                except:
                    description = "Feature available"
            else:
                description = "No documentation"
            
            status = "✅ Active" if is_feature_active(feature_dir.name) else "⚠️ Inactive"
            print(f"  {feature_dir.name:<15} {status:<12} {description}")

def is_feature_active(feature_name):
    """Check if a feature is currently active"""
    try:
        with open("features/feature_manager.py", 'r') as f:
            content = f.read()
            return f"register_feature('{feature_name}'" in content and not f"# feature_manager.register_feature('{feature_name}'" in content
    except:
        return False

def disable_feature(feature_name):
    """Disable a feature by commenting out its registration"""
    feature_manager_path = "features/feature_manager.py"
    
    if not os.path.exists(feature_manager_path):
        print("❌ Feature manager not found")
        return
    
    try:
        with open(feature_manager_path, 'r') as f:
            content = f.read()
        
        # Comment out the registration line
        old_line = f"feature_manager.register_feature('{feature_name}'"
        new_line = f"# feature_manager.register_feature('{feature_name}'"
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            with open(feature_manager_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Feature '{feature_name}' disabled")
            print("⚠️ Restart the application for changes to take effect")
        else:
            print(f"❌ Feature '{feature_name}' not found in registration")
    
    except Exception as e:
        print(f"❌ Error disabling feature: {e}")

def enable_feature(feature_name):
    """Enable a feature by uncommenting its registration"""
    feature_manager_path = "features/feature_manager.py"
    
    if not os.path.exists(feature_manager_path):
        print("❌ Feature manager not found")
        return
    
    try:
        with open(feature_manager_path, 'r') as f:
            content = f.read()
        
        # Uncomment the registration line
        old_line = f"# feature_manager.register_feature('{feature_name}'"
        new_line = f"feature_manager.register_feature('{feature_name}'"
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            with open(feature_manager_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Feature '{feature_name}' enabled")
            print("⚠️ Restart the application for changes to take effect")
        else:
            print(f"❌ Feature '{feature_name}' not found or already enabled")
    
    except Exception as e:
        print(f"❌ Error enabling feature: {e}")

def remove_feature(feature_name, confirm=False):
    """Completely remove a feature"""
    feature_path = Path(f"features/{feature_name}")
    
    if not feature_path.exists():
        print(f"❌ Feature '{feature_name}' not found")
        return
    
    if not confirm:
        response = input(f"⚠️ This will permanently delete the '{feature_name}' feature. Continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled")
            return
    
    try:
        # First disable the feature
        disable_feature(feature_name)
        
        # Then remove the directory
        shutil.rmtree(feature_path)
        
        print(f"✅ Feature '{feature_name}' completely removed")
        print("⚠️ Restart the application and remove any remaining imports")
    
    except Exception as e:
        print(f"❌ Error removing feature: {e}")

def create_feature_template(feature_name):
    """Create a new feature template"""
    feature_path = Path(f"features/{feature_name}")
    
    if feature_path.exists():
        print(f"❌ Feature '{feature_name}' already exists")
        return
    
    try:
        # Create directories
        feature_path.mkdir(parents=True)
        (feature_path / "templates").mkdir()
        (feature_path / "static").mkdir()
        
        # Create main feature file
        feature_file = feature_path / f"{feature_name}.py"
        with open(feature_file, 'w') as f:
            f.write(f'''"""
Standalone {feature_name.title()} Feature
"""

from flask import Blueprint, render_template, request, jsonify

# Create blueprint with custom template and static folders
{feature_name}_bp = Blueprint(
    '{feature_name}', 
    __name__, 
    url_prefix='/{feature_name}',
    template_folder='templates',
    static_folder='static',
    static_url_path='/{feature_name}/static'
)

@{feature_name}_bp.route('/')
def index():
    """Main {feature_name} page"""
    return render_template('{feature_name}.html')

def get_feature_info():
    """Return information about this feature"""
    return {{
        "name": "{feature_name.title()} Feature",
        "version": "1.0.0",
        "description": "Description of {feature_name} functionality",
        "dependencies": [],
        "routes": ["/{feature_name}/"],
        "templates": ["{feature_name}.html"],
        "static_files": ["{feature_name}.css", "{feature_name}.js"]
    }}
''')
        
        # Create template file
        template_file = feature_path / "templates" / f"{feature_name}.html"
        with open(template_file, 'w') as f:
            f.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{feature_name.title()} - Serenity Wellness Studio</title>
    <link rel="stylesheet" href="{{{{ url_for('{feature_name}.static', filename='{feature_name}.css') }}}}">
</head>
<body>
    <div class="container">
        <h1>{feature_name.title()} Feature</h1>
        <p>Welcome to the {feature_name} feature!</p>
        
        <div class="actions">
            <a href="/" class="btn">Back to Home</a>
        </div>
    </div>
    
    <script src="{{{{ url_for('{feature_name}.static', filename='{feature_name}.js') }}}}"></script>
</body>
</html>''')
        
        # Create CSS file
        css_file = feature_path / "static" / f"{feature_name}.css"
        with open(css_file, 'w') as f:
            f.write(f'''/* {feature_name.title()} Feature Styles */
.container {{
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    font-family: Arial, sans-serif;
}}

.btn {{
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: #8B5E3C;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    transition: background 0.3s;
}}

.btn:hover {{
    background: #6d4a2f;
}}
''')
        
        # Create JS file
        js_file = feature_path / "static" / f"{feature_name}.js"
        with open(js_file, 'w') as f:
            f.write(f'''// {feature_name.title()} Feature JavaScript
document.addEventListener('DOMContentLoaded', function() {{
    console.log('{feature_name.title()} feature loaded');
    
    // Add your JavaScript functionality here
}});
''')
        
        # Create README
        readme_file = feature_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(f'''# {feature_name.title()} Feature

**Complete standalone {feature_name} system**

## Files in this feature:
- `{feature_name}.py` - All routes and logic
- `templates/` - All HTML templates
- `static/` - All CSS and JavaScript files

## Installation:
1. Copy this entire folder to your Flask app
2. Import the blueprint: `from features.{feature_name}.{feature_name} import {feature_name}_bp`
3. Register it: `app.register_blueprint({feature_name}_bp)`

## Dependencies:
- Flask (add specific dependencies here)

## Routes:
- `/{feature_name}/` - Main {feature_name} page

## To Remove:
Simply delete this entire `features/{feature_name}/` folder and remove the blueprint registration from your app.

## Features:
- ✅ Basic {feature_name} functionality
- ✅ Responsive design
- ✅ Self-contained templates and assets
''')
        
        print(f"✅ Feature template '{feature_name}' created successfully!")
        print(f"📁 Location: features/{feature_name}/")
        print(f"📝 Next steps:")
        print(f"   1. Edit features/{feature_name}/{feature_name}.py to add your functionality")
        print(f"   2. Customize the template and styles")
        print(f"   3. Add registration to features/feature_manager.py")
        print(f"   4. Restart the application")
    
    except Exception as e:
        print(f"❌ Error creating feature template: {e}")

def main():
    parser = argparse.ArgumentParser(description='Manage modular Flask features')
    parser.add_argument('action', choices=['list', 'disable', 'enable', 'remove', 'create'], 
                       help='Action to perform')
    parser.add_argument('feature', nargs='?', help='Feature name')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_features()
    elif args.action in ['disable', 'enable', 'remove', 'create'] and not args.feature:
        print(f"❌ Feature name required for '{args.action}' action")
        sys.exit(1)
    elif args.action == 'disable':
        disable_feature(args.feature)
    elif args.action == 'enable':
        enable_feature(args.feature)
    elif args.action == 'remove':
        remove_feature(args.feature, args.confirm)
    elif args.action == 'create':
        create_feature_template(args.feature)

if __name__ == '__main__':
    main()
