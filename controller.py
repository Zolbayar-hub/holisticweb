"""
Admin Panel Controller - Unified admin functionality
This module provides a centralized controller for admin-related operations
including upload, terminal, and screenshot functionalities.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import os
import logging

from flask_login import login_required, current_user

# Create admin panel blueprint
admin_panel_controller = Blueprint('admin_panel', __name__, url_prefix='/admin-panel')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_admin():
    return current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role.name == 'admin'


def admin_required(f):
    """
    Decorator to require admin authentication for admin routes
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and has admin privileges
        if not is_admin():
            flash('Access denied. Admin role required.', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


@admin_panel_controller.route('/')
@admin_required
def dashboard():
    """
    Admin dashboard - main landing page for admin panel
    """
    try:
        # Get some basic stats for the dashboard
        stats = {
            'total_users': 0,  # You can implement actual user counting
            'total_uploads': 0,  # You can implement actual upload counting
            'total_screenshots': 0,  # You can implement actual screenshot counting
            'server_status': 'Online'
        }
        
        return render_template('admin_dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}")
        flash('Error loading dashboard', 'error')
        return render_template('adminBase.html')

@admin_panel_controller.route('/upload')
@admin_required
def upload_redirect():
    """
    Redirect to the main upload functionality
    """
    return redirect('/upload')

@admin_panel_controller.route('/terminal')
@admin_required
def terminal_redirect():
    """
    Redirect to the terminal functionality
    """
    return redirect('/terminal')

@admin_panel_controller.route('/screenshot')
@admin_required
def screenshot_redirect():
    """
    Redirect to the screenshot functionality
    """
    return redirect('/screenshot')

@admin_panel_controller.route('/content-generator')
@admin_required
def content_generator_redirect():
    """
    Redirect to the content generation functionality
    """
    return redirect('/gen_ingest/generate-content')

@admin_panel_controller.route('/markdown-editor')
@admin_required
def markdown_editor_redirect():
    """
    Redirect to the markdown editor functionality
    """
    return redirect(url_for('tutorials.markdown_editor'))

@admin_panel_controller.route('/users')
@admin_required
def user_management():
    """
    User management interface
    """
    try:
        # This is a placeholder - implement actual user management
        users = []  # Get users from your database
        return render_template('admin_users.html', users=users)
    except Exception as e:
        logger.error(f"Error in user management: {str(e)}")
        flash('Error loading user management', 'error')
        return redirect(url_for('admin_panel.dashboard'))

@admin_panel_controller.route('/settings')
@admin_required
def settings():
    """
    Admin settings interface
    """
    try:
        # This is a placeholder - implement actual settings
        settings_data = {
            'app_name': 'Tutorial Hub',
            'debug_mode': False,
            'maintenance_mode': False
        }
        return render_template('admin_settings.html', settings=settings_data)
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        flash('Error loading settings', 'error')
        return redirect(url_for('admin_panel.dashboard'))

@admin_panel_controller.route('/api/stats')
@admin_required
def api_stats():
    """
    API endpoint to get admin statistics
    """
    try:
        # Import here to avoid circular imports
        from db.models import GeneratedContent
        
        # Get actual counts from database
        total_generated_content = GeneratedContent.query.count()
        
        stats = {
            'users': {
                'total': 0,  # Implement actual counting
                'active': 0,
                'new_today': 0
            },
            'content': {
                'total_uploads': 0,  # Implement actual counting
                'total_screenshots': 0,
                'total_sessions': 0,
                'generated_content': total_generated_content
            },
            'system': {
                'uptime': '0 days',  # Implement actual uptime
                'memory_usage': '0%',
                'disk_usage': '0%'
            }
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({'error': 'Failed to get stats'}), 500

@admin_panel_controller.route('/api/logs')
@admin_required
def api_logs():
    """
    API endpoint to get recent logs
    """
    try:
        # This is a placeholder - implement actual log retrieval
        logs = [
            {'timestamp': '2025-01-27 12:00:00', 'level': 'INFO', 'message': 'User logged in'},
            {'timestamp': '2025-01-27 11:59:00', 'level': 'INFO', 'message': 'File uploaded successfully'},
            {'timestamp': '2025-01-27 11:58:00', 'level': 'WARNING', 'message': 'High memory usage detected'}
        ]
        return jsonify(logs)
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        return jsonify({'error': 'Failed to get logs'}), 500

@admin_panel_controller.route('/tools')
@admin_required
def admin_tools():
    """
    Admin tools and utilities page
    """
    try:
        tools = [
            {
                'name': 'File Upload',
                'description': 'Upload and manage files',
                'url': '/upload',
                'icon': '📁'
            },
            {
                'name': 'Terminal Interface',
                'description': 'Interactive terminal for development',
                'url': '/terminal',
                'icon': '💻'
            },
            {
                'name': 'Screenshot Tool',
                'description': 'Generate screenshots and images',
                'url': '/screenshot',
                'icon': '📷'
            },
            {
                'name': 'Content Generator',
                'description': 'Generate AI-powered content and code snippets',
                'url': '/gen_ingest/generate-content',
                'icon': '🤖'
            }
        ]
        return render_template('admin_tools.html', tools=tools)
    except Exception as e:
        logger.error(f"Error loading admin tools: {str(e)}")
        flash('Error loading admin tools', 'error')
        return redirect(url_for('admin_panel.dashboard'))

# Error handlers for admin routes
@admin_panel_controller.errorhandler(404)
def admin_not_found(error):
    """Handle 404 errors in admin panel"""
    return render_template('admin_error.html', 
                         error_code=404, 
                         error_message='Page not found'), 404

@admin_panel_controller.errorhandler(500)
def admin_internal_error(error):
    """Handle 500 errors in admin panel"""
    return render_template('admin_error.html', 
                         error_code=500, 
                         error_message='Internal server error'), 500

# Utility functions for admin functionality
def get_admin_navigation():
    """
    Get navigation items for admin panel
    """
    return [
        {'name': 'Dashboard', 'url': url_for('admin_panel.dashboard'), 'icon': '📊'},
        {'name': 'Upload', 'url': '/upload', 'icon': '📁'},
        {'name': 'Terminal', 'url': '/terminal', 'icon': '💻'},
        {'name': 'Screenshot', 'url': '/screenshot', 'icon': '📷'},
        {'name': 'Content Generator', 'url': '/gen_ingest/generate-content', 'icon': '🤖'},
        {'name': 'Users', 'url': url_for('admin_panel.user_management'), 'icon': '👥'},
        {'name': 'Settings', 'url': url_for('admin_panel.settings'), 'icon': '⚙️'}
    ]

def log_admin_action(action, details=None):
    """
    Log admin actions for audit trail
    """
    user_id = session.get('user_id', 'Unknown')
    logger.info(f"Admin action by user {user_id}: {action}. Details: {details}")
