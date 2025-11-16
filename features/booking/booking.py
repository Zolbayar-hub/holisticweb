"""
Standalone Booking Feature
Complete booking system with routes, templates, and static files
This file contains everything needed for the booking functionality
"""

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_mail import Message, Mail
from db import db
from db.models import Booking, Service, EmailTemplate
from datetime import datetime
import threading
import pytz
from routes.send_sms import send_booking_confirmation_sms, format_local_time as sms_format_local_time

LOCAL_TZ = pytz.timezone("America/New_York")  # change to your timezone

def format_local_time(utc_time):
    """Convert UTC datetime to local timezone and format nicely"""
    return utc_time.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %I:%M %p")

# Create blueprint with custom template and static folders
booking_bp = Blueprint(
    "booking", 
    __name__, 
    url_prefix="/booking",
    template_folder='templates',
    static_folder='static',
    static_url_path='/booking/static'
)

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
    events = []
    for booking in bookings:
        events.append({
            "id": booking.id,
            "title": f"{booking.user_name} - {booking.service.name}",
            "start": booking.start_time.isoformat(),
            "end": booking.end_time.isoformat(),
            "backgroundColor": "#28a745" if booking.status == "confirmed" else "#ffc107",
            "borderColor": "#28a745" if booking.status == "confirmed" else "#ffc107"
        })
    return jsonify(events)

# 📅 API: Create new booking
@booking_bp.route("/events", methods=["POST"])
def add_booking():
    try:
        data = request.json
        print(f"Received booking data: {data}")
        
        # Validate required fields
        required_fields = ['user_name', 'user_email', 'phone', 'service_id', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Parse datetime strings
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        
        # Get service
        service = Service.query.get(data['service_id'])
        if not service:
            return jsonify({"error": "Service not found"}), 400
        
        # Get number of people (default to 1)
        num_people = data.get('num_people', 1)
        
        # Create booking
        booking = Booking(
            user_name=data['user_name'],
            user_email=data['user_email'],
            phone=data['phone'],
            service_id=data['service_id'],
            start_time=start_time,
            end_time=end_time,
            status='confirmed',
            num_people=num_people
        )
        
        db.session.add(booking)
        db.session.commit()
        
        print(f"✅ Booking created successfully: ID {booking.id}")
        
        # Send confirmation email and SMS in background
        def send_notifications():
            try:
                send_booking_confirmation_email(booking, service)
                send_booking_confirmation_sms(booking, service)
            except Exception as e:
                print(f"❌ Error sending notifications: {e}")
        
        # Start background thread for notifications
        notification_thread = threading.Thread(target=send_notifications)
        notification_thread.daemon = True
        notification_thread.start()
        
        return jsonify({
            "id": booking.id,
            "message": "Booking created successfully!",
            "start_time": format_local_time(booking.start_time),
            "end_time": format_local_time(booking.end_time),
            "service": service.name,
            "num_people": num_people
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating booking: {e}")
        return jsonify({"error": f"Failed to create booking: {str(e)}"}), 500

def send_booking_confirmation_email(booking, service):
    """Send booking confirmation email"""
    try:
        # Get email template
        template = EmailTemplate.query.filter_by(name='booking_confirmation').first()
        
        if template:
            subject = template.subject.format(
                service_name=service.name,
                user_name=booking.user_name
            )
            body = template.body.format(
                user_name=booking.user_name,
                service_name=service.name,
                service_price=service.price,
                start_time=format_local_time(booking.start_time),
                end_time=format_local_time(booking.end_time)
            )
        else:
            subject = f"Booking Confirmation - {service.name}"
            body = f"""
Dear {booking.user_name},

Your booking has been confirmed!

Service: {service.name}
Date & Time: {format_local_time(booking.start_time)} - {format_local_time(booking.end_time)}
Price: ${service.price}

Thank you for choosing our services!
"""
        
        mail = current_app.mail
        msg = Message(
            subject=subject,
            recipients=[booking.user_email],
            body=body
        )
        mail.send(msg)
        print(f"✅ Confirmation email sent to {booking.user_email}")
        
    except Exception as e:
        print(f"❌ Failed to send confirmation email: {e}")

# 📅 API: Get available time slots
@booking_bp.route("/available-slots")
def get_available_slots():
    try:
        date = request.args.get('date')
        service_id = request.args.get('service_id')
        
        if not date or not service_id:
            return jsonify({"error": "Date and service_id are required"}), 400
        
        # Parse date
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get service
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"error": "Service not found"}), 400
        
        # Get existing bookings for that date
        existing_bookings = Booking.query.filter(
            db.func.date(Booking.start_time) == selected_date,
            Booking.status == 'confirmed'
        ).all()
        
        # Generate available slots (9 AM to 6 PM, every hour)
        available_slots = []
        for hour in range(9, 18):  # 9 AM to 5 PM (last slot)
            slot_time = datetime.combine(selected_date, datetime.min.time().replace(hour=hour))
            
            # Check if this slot conflicts with existing bookings
            conflict = False
            for booking in existing_bookings:
                booking_start = booking.start_time.replace(tzinfo=None)
                booking_end = booking.end_time.replace(tzinfo=None)
                slot_end = slot_time + timedelta(minutes=service.duration)
                
                if (slot_time < booking_end and slot_end > booking_start):
                    conflict = True
                    break
            
            if not conflict:
                available_slots.append({
                    "time": slot_time.strftime("%H:%M"),
                    "display": slot_time.strftime("%I:%M %p")
                })
        
        return jsonify(available_slots)
        
    except Exception as e:
        print(f"❌ Error getting available slots: {e}")
        return jsonify({"error": str(e)}), 500

# 📅 New booking form page
@booking_bp.route("/new")
def create_booking():
    return render_template("create_booking.html")

# 📅 Cancel booking
@booking_bp.route("/events/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        booking.status = 'cancelled'
        db.session.commit()
        
        return jsonify({"message": "Booking cancelled successfully"}), 200
        
    except Exception as e:
        print(f"❌ Error cancelling booking: {e}")
        return jsonify({"error": str(e)}), 500

# 📅 My Bookings page
@booking_bp.route("/my-bookings")
def my_bookings():
    return render_template("my_bookings.html")

# 📅 API: Search my bookings
@booking_bp.route("/my-bookings/search")
def search_my_bookings():
    try:
        email = request.args.get('email')
        phone = request.args.get('phone')
        
        if not email and not phone:
            return jsonify({"error": "Email or phone number required"}), 400
        
        # Build query
        query = Booking.query
        if email:
            query = query.filter(Booking.user_email.ilike(f"%{email}%"))
        if phone:
            query = query.filter(Booking.phone.ilike(f"%{phone}%"))
        
        bookings = query.order_by(Booking.start_time.desc()).all()
        
        bookings_data = []
        for booking in bookings:
            bookings_data.append({
                "id": booking.id,
                "user_name": booking.user_name,
                "user_email": booking.user_email,
                "phone": booking.phone,
                "service_name": booking.service.name,
                "start_time": format_local_time(booking.start_time),
                "end_time": format_local_time(booking.end_time),
                "status": booking.status,
                "num_people": getattr(booking, 'num_people', 1)
            })
        
        return jsonify(bookings_data)
        
    except Exception as e:
        print(f"❌ Error searching bookings: {e}")
        return jsonify({"error": str(e)}), 500

# 📅 Debug: Database schema
@booking_bp.route("/debug/schema")
def debug_schema():
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'booking' in inspector.get_table_names():
            columns = inspector.get_columns('booking')
            column_info = [{"name": col['name'], "type": str(col['type'])} for col in columns]
            return jsonify({
                "status": "success",
                "table_exists": True,
                "columns": column_info
            })
        else:
            return jsonify({
                "status": "error",
                "table_exists": False,
                "message": "Booking table not found"
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Helper function for time calculations
from datetime import timedelta

def get_feature_info():
    """Return information about this feature"""
    return {
        "name": "Booking System",
        "version": "1.0.0",
        "description": "Complete booking system with calendar, forms, and notifications",
        "dependencies": ["Flask-Mail", "pytz", "twilio"],
        "routes": [
            "/booking/",
            "/booking/calendar", 
            "/booking/new",
            "/booking/my-bookings",
            "/booking/services",
            "/booking/events",
            "/booking/available-slots"
        ],
        "templates": ["book.html", "booking.html", "create_booking.html", "my_bookings.html"],
        "static_files": ["book.css", "book.js", "book_new.js"]
    }
