"""
Main application routes
Contains core routes like home, health check, etc.
"""

from flask import Blueprint, render_template, redirect, url_for, send_from_directory, current_app, request, jsonify, flash
from flask_mail import Message
import os

from db.models import Service, SiteSetting, AboutImage
from routes.testimony import get_approved_testimonials
from routes.send_sms import get_sms_status, test_sms_connection, check_and_send_reminders
from utils.site_settings import get_site_settings


# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Home page with services and testimonials"""
    # Get site settings for the current language (default to 'ENG')
    # You can extend this to get language from user session, URL parameter, or browser settings
    current_language = request.args.get('lang', 'ENG')
    if current_language not in ['ENG', 'MON']:
        current_language = 'ENG'
    
    # Filter services by current language
    services = Service.query.filter_by(language=current_language).all()
    
    settings = get_site_settings(current_language)
    
    # Get approved testimonials for display
    testimonials = get_approved_testimonials()
    
    # Get active about images ordered by sort_order
    about_images = AboutImage.query.filter_by(is_active=True).order_by(AboutImage.sort_order).all()
    
    return render_template('home.html', 
                         services=services, 
                         settings=settings, 
                         testimonials=testimonials, 
                         about_images=about_images,
                         current_language=current_language)


@main_bp.route('/contact', methods=['POST'])
def contact_form():
    """Handle contact form submissions"""
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validate required fields
        if not name or not email or not message:
            return jsonify({
                'status': 'error',
                'message': 'Please fill in all required fields (name, email, and message).'
            }), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({
                'status': 'error',
                'message': 'Please enter a valid email address.'
            }), 400
        
        # Send email notification to admin
        try:
            mail = current_app.mail
            
            # Email to admin
            admin_subject = f"New Contact Form Submission from {name}"
            admin_body = f"""
You have received a new contact form submission:

Name: {name}
Email: {email}
Phone: {phone}
Message:
{message}

---
This message was sent via the contact form on your website.
"""
            
            admin_msg = Message(
                subject=admin_subject,
                recipients=[current_app.config.get('MAIL_USERNAME', 'admin@example.com')],
                body=admin_body
            )
            mail.send(admin_msg)
            
            # Send confirmation email to user
            user_subject = "Thank you for contacting us - Holistic Therapy"
            user_body = f"""
Dear {name},

Thank you for reaching out to us! We have received your message and will get back to you within 24 hours.

Your message:
{message}

If you have any urgent concerns, please feel free to call us directly.

Best regards,
Holistic Therapy Team
"""
            
            user_msg = Message(
                subject=user_subject,
                recipients=[email],
                body=user_body
            )
            mail.send(user_msg)
            
            return jsonify({
                'status': 'success',
                'message': 'Thank you for your message! We will get back to you soon. Please check your email for confirmation.'
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Failed to send contact form email: {e}")
            return jsonify({
                'status': 'error',
                'message': 'There was an error sending your message. Please try again or contact us directly.'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Contact form error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'There was an error processing your request. Please try again.'
        }), 500


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


@main_bp.route('/test-email')
def test_email():
    """Test email functionality with contact form format"""
    try:
        mail = current_app.mail
        
        # Test data
        name = "Test User"
        email = "test@example.com"
        phone = "123-456-7890"
        message = "This is a test message from the contact form functionality."
        
        # Email to admin (same format as contact form)
        admin_subject = f"TEST: New Contact Form Submission from {name}"
        admin_body = f"""
You have received a new contact form submission:

Name: {name}
Email: {email}
Phone: {phone}
Message:
{message}

---
This message was sent via the contact form on your website.
"""
        
        admin_msg = Message(
            subject=admin_subject,
            recipients=[current_app.config.get('MAIL_USERNAME', 'admin@example.com')],
            body=admin_body
        )
        mail.send(admin_msg)
        
        return f"""
        <h1>Email Test Results</h1>
        <p><strong>Status:</strong> ✅ Success</p>
        <p><strong>Test email sent to:</strong> {current_app.config.get('MAIL_USERNAME', 'admin@example.com')}</p>
        <p><strong>Subject:</strong> {admin_subject}</p>
        <p><strong>Message:</strong> Email sent successfully!</p>
        <p><a href="/">← Back to Home</a></p>
        """
        
    except Exception as e:
        return f"""
        <h1>Email Test Results</h1>
        <p><strong>Status:</strong> ❌ Error</p>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><strong>Config Status:</strong></p>
        <ul>
            <li>MAIL_SERVER: {current_app.config.get('MAIL_SERVER', 'Not set')}</li>
            <li>MAIL_PORT: {current_app.config.get('MAIL_PORT', 'Not set')}</li>
            <li>MAIL_USERNAME: {'Set' if current_app.config.get('MAIL_USERNAME') else 'Not set'}</li>
            <li>MAIL_PASSWORD: {'Set' if current_app.config.get('MAIL_PASSWORD') else 'Not set'}</li>
        </ul>
        <p><a href="/">← Back to Home</a></p>
        """
