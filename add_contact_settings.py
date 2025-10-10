#!/usr/bin/env python3
"""
Script to add missing contact settings to the database
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_factory import create_app
from db import db
from db.models import SiteSetting

def add_contact_settings():
    """Add contact settings if they don't exist"""
    
    contact_settings = [
        ('business_phone', '8014720284', 'Business phone number'),
        ('business_email', 'bayarba27@gmail.com', 'Business email address'),
        ('business_address', '123 Wellness Street, Healing City, HC 12345', 'Business address'),
    ]
    
    settings_added = False
    
    for key, value, description in contact_settings:
        # Check if setting exists for English language
        setting = SiteSetting.query.filter_by(key=key, language='ENG').first()
        if not setting:
            setting = SiteSetting(key=key, language='ENG', value=value, description=description)
            db.session.add(setting)
            settings_added = True
            print(f"✅ Added {key} setting for English: {value}")
        else:
            print(f"ℹ️  {key} already exists for English: {setting.value}")
        
        # Add Mongolian version
        setting_mon = SiteSetting.query.filter_by(key=key, language='MON').first()
        if not setting_mon:
            setting_mon = SiteSetting(key=key, language='MON', value=value, description=f"{description} (Mongolian)")
            db.session.add(setting_mon)
            settings_added = True
            print(f"✅ Added {key} setting for Mongolian: {value}")
        else:
            print(f"ℹ️  {key} already exists for Mongolian: {setting_mon.value}")
    
    if settings_added:
        db.session.commit()
        print("✅ Contact settings committed to database!")
    else:
        print("ℹ️  All contact settings already exist.")

if __name__ == '__main__':
    try:
        app = create_app()
        
        with app.app_context():
            add_contact_settings()
    except Exception as e:
        print(f"❌ Error adding contact settings: {e}")
        import traceback
        traceback.print_exc()
