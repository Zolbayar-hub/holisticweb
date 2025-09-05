from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_mail import Message, Mail
from db import db
from db.models import Booking, Service, EmailTemplate
from datetime import datetime
import threading
import pytz
from .send_sms import send_booking_confirmation_sms, format_local_time as sms_format_local_time

LOCAL_TZ = pytz.timezone("America/New_York")  # change to your timezone

def format_local_time(utc_time):
    """Convert UTC datetime to local timezone and format nicely"""
    return utc_time.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %I:%M %p")

booking_bp = Blueprint("booking_bp", __name__, url_prefix="/booking")

# 📅 Calendar page (old version)
@booking_bp.route("/calendar")
def booking_calendar():
    return render_template("booking.html")

# 📅 New modern booking page
@booking_bp.route("/")
def booking_page():
    return render_template("book.html")

# 📅 API: Get available services
@booking_bp.route("/services")
def get_services():
    # Get language from query parameter or default to 'ENG'
    current_language = request.args.get('lang', 'ENG')
    if current_language not in ['ENG', 'MON']:
        current_language = 'ENG'
    
    # Filter services by language
    services = Service.query.filter_by(language=current_language).all()
    services_data = [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "price": s.price,
            "duration": s.duration
        }
        for s in services
    ]
    return jsonify(services_data)

# 📅 API: Get all bookings (for FullCalendar)
@booking_bp.route("/events")
def booking_events():
    bookings = Booking.query.all()
    events = [
        {
            "id": b.id,
            "title": f"{b.user_name} ({b.status})",  # Show name + status
            "start": b.start_time.isoformat(),
            "end": b.end_time.isoformat(),
        }
        for b in bookings
    ]
    return jsonify(events)

# 📅 API: Add new booking (enhanced with email confirmation)
@booking_bp.route("/events", methods=["POST"])
def add_booking():
    data = request.get_json()
    try:
        # Create new booking
        booking = Booking(
            user_name=data["user_name"],
            email=data["email"],
            phone_number=data.get("phone"),  # Added phone number support
            service_id=data.get("service_id"),
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            status="pending"
        )
        db.session.add(booking)
        db.session.commit()

        # Send confirmation email (non-blocking)
        if current_app.config.get("MAIL_USERNAME") and current_app.config.get("MAIL_PASSWORD"):
            service = Service.query.get(booking.service_id) if booking.service_id else None
            
            # Capture the app instance for use in the background thread
            app = current_app._get_current_object()
            
            def send_email_async():
                """Send email in background thread to avoid blocking the request"""
                try:
                    with app.app_context():
                        # Get the mail instance from the app
                        mail = app.mail
                        
                        # Send confirmation email to customer
                        print(f"📧 [Background] Sending confirmation email to {booking.email}")
                        print(f"📧 [Background] SMTP Config: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
                        print(f"📧 [Background] From: {app.config.get('MAIL_DEFAULT_SENDER')}")
                        
                        # Get email template
                        email_template = EmailTemplate.query.filter_by(name='booking_confirmation').first()
                        
                        if email_template:
                            # Use custom template
                            subject = email_template.subject
                            body = email_template.body
                            
                            # Replace variables in template
                            variables = {
                                '{user_name}': booking.user_name,
                                '{email}': booking.email,
                                '{service_name}': service.name if service else 'Unknown',
                                '{service_price}': str(service.price) if service else 'N/A',
                                '{start_time}': format_local_time(booking.start_time.replace(tzinfo=pytz.UTC)),
                                '{end_time}': format_local_time(booking.end_time.replace(tzinfo=pytz.UTC))
                            }
                            
                            for variable, value in variables.items():
                                subject = subject.replace(variable, value)
                                body = body.replace(variable, value)
                        else:
                            # Fallback to default template
                            subject = f"🌟 Booking Confirmation - {service.name if service else 'HolisticWeb'}"
                            body = f"""Hello {booking.user_name},

Thank you for booking with HolisticWeb! ✨

📌 Service: {service.name if service else "Unknown"}
💰 Price: ${service.price if service else "N/A"}
🕒 Start: {format_local_time(booking.start_time.replace(tzinfo=pytz.UTC))}
🕒 End:   {format_local_time(booking.end_time.replace(tzinfo=pytz.UTC))}

{service.description if service else ""}

We look forward to seeing you!

Best regards,
- The HolisticWeb Team

If you need to reschedule or have any questions, please contact us.
"""
                        
                        msg = Message(
                            subject=subject,
                            recipients=[booking.email],
                            sender=app.config.get('MAIL_DEFAULT_SENDER'),
                            body=body
                        )
                        
                        mail.send(msg)
                        print(f"✅ [Background] Confirmation email sent successfully to {booking.email}")
                        
                        # Send notification email to admin
                        try:
                            admin_msg = Message(
                                subject="📩 New Booking Received",
                                recipients=["dambazolbayar@gmail.com"],   # replace with your admin email
                                sender=app.config.get('MAIL_DEFAULT_SENDER'),
                                body=f"""A new booking was created!

📌 Service: {service.name if service else "Unknown"} (ID: {booking.service_id})
📅 Date: {format_local_time(booking.start_time.replace(tzinfo=pytz.UTC))} - {format_local_time(booking.end_time.replace(tzinfo=pytz.UTC))}
👤 Customer: {booking.user_name}
📧 Email: {booking.email}
💰 Price: ${service.price if service else "N/A"}

Booking ID: {booking.id}

Login to admin panel to manage this booking.
"""
                            )
                            mail.send(admin_msg)
                            print("✅ [Background] Admin notification sent successfully")
                        except Exception as admin_email_error:
                            print(f"❌ [Background] Admin email failed: {admin_email_error}")
                        
                except Exception as email_error:
                    print(f"❌ [Background] Failed to send customer email: {email_error}")
                    print(f"❌ Error type: {type(email_error).__name__}")
                    print(f"❌ Error details: {str(email_error)}")
                    if "authentication" in str(email_error).lower():
                        print("❌ Authentication failed - check Gmail app password")
                    elif "timeout" in str(email_error).lower():
                        print("❌ Connection timeout - check network/firewall")
                    # Print full traceback for debugging
                    import traceback
                    traceback.print_exc()
            
            # Start email sending in background
            email_thread = threading.Thread(target=send_email_async, daemon=True)
            email_thread.start()
            
            print(f"📧 Email confirmation being sent to {booking.email}")
        else:
            print("📧 Email credentials not configured")
            print(f"📧 MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')}")
            print(f"📧 MAIL_PASSWORD: {'***' if current_app.config.get('MAIL_PASSWORD') else 'Not set'}")

        # Send SMS confirmation (non-blocking)
        if hasattr(booking, 'phone_number') and booking.phone_number:
            service = Service.query.get(booking.service_id) if booking.service_id else None
            
            def send_sms_async():
                """Send SMS in background thread to avoid blocking the request"""
                try:
                    print(f"📱 [Background] Sending SMS confirmation to {booking.phone_number}")
                    
                    success = send_booking_confirmation_sms(
                        booking.phone_number,
                        booking.user_name,
                        service.name if service else 'HolisticWeb Service',
                        booking.start_time
                    )
                    
                    if success:
                        print(f"✅ [Background] SMS confirmation sent successfully to {booking.phone_number}")
                    else:
                        print(f"❌ [Background] Failed to send SMS confirmation to {booking.phone_number}")
                        
                except Exception as sms_error:
                    print(f"❌ [Background] SMS sending error: {sms_error}")
            
            # Start SMS sending in background
            sms_thread = threading.Thread(target=send_sms_async, daemon=True)
            sms_thread.start()
            
            print(f"📱 SMS confirmation being sent to {booking.phone_number}")
        else:
            print("📱 No phone number provided for SMS confirmation")

        return jsonify({
            "success": True, 
            "id": booking.id,
            "message": "Booking created successfully! Confirmation email and SMS being sent."
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating booking: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

# 📅 Form-based booking (for backwards compatibility)
@booking_bp.route("/new", methods=["GET", "POST"])
def create_booking():
    if request.method == "POST":
        try:
            new_booking = Booking(
                user_name=request.form["user_name"],
                email=request.form["email"],
                phone_number=request.form.get("phone_number"),  # Added phone number support
                service_id=request.form["service_id"],
                start_time=datetime.fromisoformat(request.form["start_time"]),
                end_time=datetime.fromisoformat(request.form["end_time"]),
            )
            db.session.add(new_booking)
            db.session.commit()

            # Redirect to the new booking page
            flash("Booking created successfully!", "success")
            return redirect(url_for("booking_bp.booking_page"))

        except Exception as e:
            flash(f"Error creating booking: {e}", "error")
            return redirect(url_for("booking_bp.create_booking"))

    # Get language from query parameter or default to 'ENG'
    current_language = request.args.get('lang', 'ENG')
    if current_language not in ['ENG', 'MON']:
        current_language = 'ENG'
    
    # Filter services by language
    services = Service.query.filter_by(language=current_language).all()
    return render_template("new_booking.html", services=services, current_language=current_language)
