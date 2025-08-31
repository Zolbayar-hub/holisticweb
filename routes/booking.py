from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_mail import Message
from db import db
from db.models import Booking, Service
from datetime import datetime
import threading

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
    services = Service.query.all()
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
            
            def send_email_async():
                """Send email in background thread to avoid blocking the request"""
                try:
                    with current_app.app_context():
                        from flask_mail import Mail
                        mail = Mail(current_app)
                        
                        # Send confirmation email to customer
                        print(f"📧 [Background] Sending confirmation email to {booking.email}")
                        msg = Message(
                            subject=f"🌟 Booking Confirmation - {service.name if service else 'HolisticWeb'}",
                            recipients=[booking.email],
                            sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                            body=f"""Hello {booking.user_name},

Thank you for booking with HolisticWeb! ✨

📌 Service: {service.name if service else "Unknown"}
💰 Price: ${service.price if service else "N/A"}
🕒 Start: {booking.start_time.strftime("%Y-%m-%d %H:%M")}
🕒 End:   {booking.end_time.strftime("%Y-%m-%d %H:%M")}

{service.description if service else ""}

We look forward to seeing you!

Best regards,
- The HolisticWeb Team

If you need to reschedule or have any questions, please contact us.
"""
                        )
                        
                        mail.send(msg)
                        print(f"✅ [Background] Confirmation email sent successfully to {booking.email}")
                        
                        # Send notification email to admin
                        try:
                            admin_msg = Message(
                                subject="📩 New Booking Received",
                                recipients=["dambazolbayar@gmail.com"],   # replace with your admin email
                                sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                                body=f"""A new booking was created!

📌 Service: {service.name if service else "Unknown"} (ID: {booking.service_id})
📅 Date: {booking.start_time.strftime("%Y-%m-%d %H:%M")} - {booking.end_time.strftime("%Y-%m-%d %H:%M")}
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
                    if "authentication" in str(email_error).lower():
                        print("❌ Authentication failed - check Gmail app password")
                    elif "timeout" in str(email_error).lower():
                        print("❌ Connection timeout - check network/firewall")
            
            # Start email sending in background
            email_thread = threading.Thread(target=send_email_async, daemon=True)
            email_thread.start()
            
            print(f"📧 Email confirmation being sent to {booking.email}")
        else:
            print("📧 Email credentials not configured")

        return jsonify({
            "success": True, 
            "id": booking.id,
            "message": "Booking created successfully! Confirmation email being sent."
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

    services = Service.query.all()
    return render_template("new_booking.html", services=services)
