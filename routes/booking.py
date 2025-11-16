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
            "title": f"{b.user_name} ({b.num_people} {'person' if b.num_people == 1 else 'people'}) - {b.status}",  # Show name + people count + status
            "start": b.start_time.isoformat(),
            "end": b.end_time.isoformat(),
        }
        for b in bookings
    ]
    return jsonify(events)

# 📅 API: Add new booking (enhanced with email confirmation)
@booking_bp.route("/events", methods=["POST"])
def add_booking():
    try:
        data = request.get_json()
        
        # Validate input data
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        required_fields = ["user_name", "email", "start_time", "end_time"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Validate email format
        email = data["email"]
        if "@" not in email:
            return jsonify({"success": False, "error": "Invalid email format"}), 400
        
        # Parse booking times
        try:
            start_time = datetime.fromisoformat(data["start_time"])
            end_time = datetime.fromisoformat(data["end_time"])
        except ValueError as e:
            return jsonify({"success": False, "error": f"Invalid date format: {str(e)}"}), 400
        
        # Get number of people (default to 1, max 10)
        num_people = int(data.get("num_people", 1))
        if num_people < 1:
            num_people = 1
        elif num_people > 10:
            num_people = 10
        
        # Check current capacity for this time slot
        existing_bookings = Booking.query.filter(
            Booking.start_time <= start_time,
            Booking.end_time > start_time,
            Booking.status != 'cancelled'
        ).all()
        
        # Calculate total people already booked
        total_existing_people = sum(booking.num_people for booking in existing_bookings)
        
        # Check if adding this booking would exceed capacity
        new_total = total_existing_people + num_people
        is_fully_booked = new_total > 10
        
        # Allow booking but warn if over capacity
        booking = Booking(
            user_name=data["user_name"],
            email=data["email"],
            phone_number=data.get("phone"),  # Added phone number support
            service_id=data.get("service_id"),
            num_people=num_people,  # Add number of people
            start_time=start_time,
            end_time=end_time,
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
                                '{num_people}': str(booking.num_people),
                                '{people_text}': 'person' if booking.num_people == 1 else 'people',
                                '{start_time}': format_local_time(booking.start_time.replace(tzinfo=pytz.UTC)),
                                '{end_time}': format_local_time(booking.end_time.replace(tzinfo=pytz.UTC))
                            }
                            
                            for variable, value in variables.items():
                                subject = subject.replace(variable, value)
                                body = body.replace(variable, value)
                        else:
                            # Fallback to default template
                            people_text = "person" if booking.num_people == 1 else "people"
                            subject = f"🌟 Booking Confirmation - {service.name if service else 'HolisticWeb'}"
                            body = f"""Hello {booking.user_name},

Thank you for booking with HolisticWeb! ✨

📌 Service: {service.name if service else "Unknown"}
� Number of People: {booking.num_people} {people_text}
�💰 Price: ${service.price if service else "N/A"}
🕒 Start: {format_local_time(booking.start_time.replace(tzinfo=pytz.UTC))}
🕒 End:   {format_local_time(booking.end_time.replace(tzinfo=pytz.UTC))}

{service.description if service else ""}

We look forward to seeing you and your group!

Best regards,
- Serenity Wellness Studio

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
                            people_text = "person" if booking.num_people == 1 else "people"
                            admin_msg = Message(
                                subject="📩 New Booking Received",
                                recipients=["dambazolbayar@gmail.com"],   # replace with your admin email
                                sender=app.config.get('MAIL_DEFAULT_SENDER'),
                                body=f"""A new booking was created!

📌 Service: {service.name if service else "Unknown"} (ID: {booking.service_id})
📅 Date: {format_local_time(booking.start_time.replace(tzinfo=pytz.UTC))} - {format_local_time(booking.end_time.replace(tzinfo=pytz.UTC))}
👤 Customer: {booking.user_name}
📧 Email: {booking.email}
👥 Number of People: {booking.num_people} {people_text}
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
            "num_people": num_people,
            "isFullyBooked": is_fully_booked,
            "totalPeople": new_total,
            "availableSpots": max(0, 10 - new_total),
            "message": f"Booking created successfully for {num_people} {'person' if num_people == 1 else 'people'}! Confirmation email and SMS being sent." + 
                      (f" Note: This time slot now has {new_total}/10 people." if new_total > 10 else f" ({new_total}/10 spots filled)")
        }), 201
        
    except ValueError as ve:
        error_msg = f"Invalid input data: {str(ve)}"
        print(f"❌ Validation error: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 400
        
    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print(f"❌ Error creating booking: {error_msg}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": error_msg}), 500

# 📅 API: Get available time slots for a specific date
@booking_bp.route("/available-slots")
def get_available_slots():
    date_str = request.args.get('date')
    service_id = request.args.get('service_id')
    
    if not date_str:
        return jsonify({"error": "Date parameter is required"}), 400
    
    try:
        # Parse the date
        selected_date = datetime.fromisoformat(date_str).date()
        
        # Generate time slots (8:30 AM to 2:00 PM, 30-minute intervals)
        slots = []
        start_hour = 8
        end_hour = 15  # Set to 15 to include 2:00 PM (14:00)
        
        for hour in range(start_hour, end_hour):
            for minutes in [0, 30]:
                # Skip 8:00 AM slot, start from 8:30 AM
                if hour == 8 and minutes == 0:
                    continue
                # Stop after 2:00 PM (don't include 2:30 PM)
                if hour == 14 and minutes == 30:
                    break
                    break  # Don't go past 2:00 PM
                
                # Create datetime for this slot
                slot_datetime = datetime.combine(selected_date, datetime.min.time().replace(hour=hour, minute=minutes))
                
                # Get existing bookings for this time slot (overlapping bookings)
                existing_bookings = Booking.query.filter(
                    Booking.start_time <= slot_datetime,
                    Booking.end_time > slot_datetime,
                    Booking.status != 'cancelled'
                ).all()
                
                # Calculate total people booked for this slot
                total_people = sum(booking.num_people for booking in existing_bookings)
                available_spots = max(0, 10 - total_people)
                
                # Format time string
                time_str = slot_datetime.strftime("%I:%M %p").lstrip('0')
                
                slots.append({
                    "time": slot_datetime.isoformat(),
                    "timeString": time_str,
                    "totalPeople": total_people,
                    "availableSpots": available_spots,
                    "isFullyBooked": total_people >= 10,
                    "bookingCount": len(existing_bookings),  # Number of individual bookings
                    "available": True  # Always true - we still allow overbooking
                })
        
        return jsonify(slots)
        
    except Exception as e:
        print(f"❌ Error getting available slots: {e}")
        return jsonify({"error": str(e)}), 400

# 📅 Form-based booking (for backwards compatibility)
@booking_bp.route("/new", methods=["GET", "POST"])
def create_booking():
    if request.method == "POST":
        try:
            # Get number of people (default to 1, max 10)
            num_people = int(request.form.get("num_people", 1))
            if num_people < 1:
                num_people = 1
            elif num_people > 10:
                num_people = 10
                
            new_booking = Booking(
                user_name=request.form["user_name"],
                email=request.form["email"],
                phone_number=request.form.get("phone_number"),  # Added phone number support
                service_id=request.form["service_id"],
                num_people=num_people,  # Add number of people
                start_time=datetime.fromisoformat(request.form["start_time"]),
                end_time=datetime.fromisoformat(request.form["end_time"]),
            )
            db.session.add(new_booking)
            db.session.commit()

            # Redirect to the new booking page
            flash(f"Booking created successfully for {num_people} {'person' if num_people == 1 else 'people'}!", "success")
            return redirect(url_for("booking.booking_page"))

        except Exception as e:
            flash(f"Error creating booking: {e}", "error")
            return redirect(url_for("booking.create_booking"))

    # Get language from query parameter or default to 'ENG'
    current_language = request.args.get('lang', 'ENG')
    if current_language not in ['ENG', 'MON']:
        current_language = 'ENG'
    
    # Filter services by language
    services = Service.query.filter_by(language=current_language).all()
    return render_template("new_booking.html", services=services, current_language=current_language)

# 📅 API: Cancel a booking
@booking_bp.route("/events/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if booking is already cancelled
        if booking.status == 'cancelled':
            return jsonify({"success": False, "error": "Booking is already cancelled"}), 400
        
        # Update booking status to cancelled
        booking.status = 'cancelled'
        db.session.commit()
        
        # Send cancellation email notification
        if current_app.config.get("MAIL_USERNAME") and current_app.config.get("MAIL_PASSWORD"):
            service = Service.query.get(booking.service_id) if booking.service_id else None
            
            # Capture the app instance for use in the background thread
            app = current_app._get_current_object()
            
            def send_cancellation_email_async():
                """Send cancellation email in background thread"""
                try:
                    with app.app_context():
                        mail = app.mail
                        
                        # Send cancellation email to customer
                        people_text = "person" if booking.num_people == 1 else "people"
                        subject = f"🚫 Booking Cancellation - {service.name if service else 'HolisticWeb'}"
                        body = f"""Hello {booking.user_name},

Your booking has been cancelled.

📌 Service: {service.name if service else "Unknown"}
👥 Number of People: {booking.num_people} {people_text}
🕒 Original Time: {format_local_time(booking.start_time.replace(tzinfo=pytz.UTC))} - {format_local_time(booking.end_time.replace(tzinfo=pytz.UTC))}
🆔 Booking ID: {booking.id}

If you did not request this cancellation or have any questions, please contact us immediately.

Best regards,
- Serenity Wellness Studio
"""
                        
                        from flask_mail import Message
                        msg = Message(
                            subject=subject,
                            recipients=[booking.email],
                            sender=app.config.get('MAIL_DEFAULT_SENDER'),
                            body=body
                        )
                        
                        mail.send(msg)
                        print(f"✅ [Background] Cancellation email sent to {booking.email}")
                        
                except Exception as email_error:
                    print(f"❌ [Background] Failed to send cancellation email: {email_error}")
            
            # Start email sending in background
            email_thread = threading.Thread(target=send_cancellation_email_async, daemon=True)
            email_thread.start()
        
        return jsonify({
            "success": True,
            "message": "Booking cancelled successfully",
            "booking_id": booking.id
        }), 200
        
    except Exception as e:
        print(f"❌ Error cancelling booking: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

# 📅 Customer booking management page
@booking_bp.route("/my-bookings")
def my_bookings():
    return render_template("my_bookings.html")

# 📅 API: Get bookings by email
@booking_bp.route("/my-bookings/search")
def search_my_bookings():
    email = request.args.get('email')
    
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400
    
    try:
        # Get all bookings for this email
        bookings = Booking.query.filter_by(email=email).order_by(Booking.start_time.desc()).all()
        
        bookings_data = []
        for booking in bookings:
            service = Service.query.get(booking.service_id) if booking.service_id else None
            
            bookings_data.append({
                "id": booking.id,
                "user_name": booking.user_name,
                "email": booking.email,
                "phone_number": booking.phone_number,
                "num_people": booking.num_people,
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat(),
                "status": booking.status,
                "service": {
                    "name": service.name if service else "Unknown",
                    "price": service.price if service else 0,
                    "duration": service.duration if service else 0
                } if service else None,
                "created_at": booking.created_at.isoformat() if booking.created_at else None
            })
        
        return jsonify(bookings_data)
        
    except Exception as e:
        print(f"❌ Error searching bookings: {e}")
        return jsonify({"error": str(e)}), 400

# Debug endpoint to check database schema
@booking_bp.route("/debug/schema")
def debug_schema():
    """Debug endpoint to check database schema"""
    try:
        from db.models import Booking
        columns = Booking.__table__.columns.keys()
        
        # Also check actual database
        import sqlite3
        import os
        
        db_path = os.path.join('instance', 'data.sqlite')
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('PRAGMA table_info(booking)')
            db_columns = cursor.fetchall()
            conn.close()
            
            return jsonify({
                "model_columns": list(columns),
                "database_columns": [{"name": col[1], "type": col[2]} for col in db_columns],
                "database_path": db_path
            })
        else:
            return jsonify({
                "model_columns": list(columns),
                "error": "Database file not found",
                "database_path": db_path
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
