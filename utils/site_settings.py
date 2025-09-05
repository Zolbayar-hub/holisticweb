"""
Utility functions for site settings with language support
"""

from db.models import SiteSetting


def get_site_settings(language='ENG'):
    """
    Get site settings for a specific language with fallback to English
    
    Args:
        language (str): Language code ('ENG' or 'MON')
    
    Returns:
        dict: Dictionary of setting key-value pairs
    """
    if language not in ['ENG', 'MON']:
        language = 'ENG'
    
    # Get settings for the requested language
    site_settings = SiteSetting.query.filter_by(language=language).all()
    settings = {setting.key: setting.value for setting in site_settings}
    
    # If not English, get English settings as fallback
    if language != 'ENG':
        eng_settings = SiteSetting.query.filter_by(language='ENG').all()
        eng_settings_dict = {setting.key: setting.value for setting in eng_settings}
        
        # Add English values for any missing keys
        for key, value in eng_settings_dict.items():
            if key not in settings:
                settings[key] = value
    
    return settings


def get_settings_by_language():
    """
    Get all settings grouped by language
    
    Returns:
        dict: Dictionary with language codes as keys and setting dictionaries as values
    """
    settings_by_language = {'ENG': {}, 'MON': {}}
    
    all_settings = SiteSetting.query.all()
    for setting in all_settings:
        settings_by_language[setting.language][setting.key] = setting.value
    
    return settings_by_language


def create_or_update_setting(key, value, language='ENG', description=None):
    """
    Create or update a site setting for a specific language
    
    Args:
        key (str): Setting key
        value (str): Setting value
        language (str): Language code ('ENG' or 'MON')
        description (str): Optional description
    
    Returns:
        SiteSetting: The created or updated setting object
    """
    from db import db
    
    if language not in ['ENG', 'MON']:
        language = 'ENG'
    
    setting = SiteSetting.query.filter_by(key=key, language=language).first()
    if not setting:
        setting = SiteSetting(key=key, language=language)
        if description:
            setting.description = description
        db.session.add(setting)
    
    setting.value = value
    return setting
