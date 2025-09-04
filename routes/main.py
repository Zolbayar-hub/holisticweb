"""
Main application routes
Contains core routes like home, health check, etc.
"""

from flask import Blueprint, render_template, redirect, url_for, send_from_directory, current_app
from flask_mail import Message
import os

from db.models import Service, SiteSetting
from routes.testimony import get_approved_testimonials
from routes.send_sms import get_sms_status, test_sms_connection, check_and_send_reminders


# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Home page with services and testimonials"""
    services = Service.query.all()
    
    # Get site settings
    site_settings = SiteSetting.query.all()
    settings = {setting.key: setting.value for setting in site_settings}
    
    # Get approved testimonials for display
    testimonials = get_approved_testimonials()
    
    return render_template('home.html', services=services, settings=settings, testimonials=testimonials)


@main_bp.route('/book')
def book_redirect():
    """Redirect to the booking page for easy access"""
    return redirect(url_for('booking_bp.booking_page'))


@main_bp.route('/bookings/new')
def old_booking_redirect():
    """Redirect old booking URL to new booking page"""
    return redirect(url_for('booking_bp.create_booking'))


@main_bp.route('/submit-testimonial', methods=['GET', 'POST'])
def old_testimonial_redirect():
    """Redirect old testimonial URL to new testimonial route"""
    return redirect(url_for('testimony.submit_testimonial'))


@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'ok', 'message': 'Server is running'}, 200


@main_bp.route('/sms-status')
def sms_status():
    """Check SMS service status"""
    status = get_sms_status()
    return {
        'sms_service': status,
        'message': 'SMS service status'
    }, 200


@main_bp.route('/test-sms')
def test_sms():
    """Test SMS connection and configuration"""
    success = test_sms_connection()
    return {
        'status': 'success' if success else 'error',
        'message': 'SMS connection test completed. Check logs for details.'
    }, 200 if success else 500


@main_bp.route('/send-reminders')
def manual_send_reminders():
    """Manually trigger SMS reminders - for testing or manual use"""
    try:
        from db.models import Booking
        check_and_send_reminders(current_app._get_current_object(), Booking)
        return {'status': 'success', 'message': 'Reminder check completed. Check logs for details.'}, 200
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to send reminders: {e}'}, 500


@main_bp.route('/send-email')
def send_test_email():
    """Test email functionality"""
    try:
        mail = current_app.mail
        msg = Message("Test Email", recipients=["dambazolbayar@gmail.com"])
        msg.body = "This is a test email from Flask."
        mail.send(msg)
        return "Email sent!"
    except Exception as e:
        return f"Email failed: {e}"


@main_bp.route('/images/<filename>')
def serve_image(filename):
    """Serve static images"""
    return send_from_directory(os.path.join(current_app.static_folder, 'images'), filename)
