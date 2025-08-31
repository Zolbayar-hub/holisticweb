#!/usr/bin/env python3
"""
Test booking email functionality specifically.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_app import app
from db import db
from db.models import Booking, Service
from datetime import datetime, timedelta
import threading

def test_booking_email():
    """Test the booking email functionality"""
    with app.app_context():
        try:
            print("🧪 Testing booking email functionality...")
            
            # Get a service
            service = Service.query.first()
            if not service:
                print("❌ No services found in database")
                return
            
            print(f"📌 Using service: {service.name}")
            
            # Create a test booking
            now = datetime.now()
            start_time = now + timedelta(days=1)  # Tomorrow
            end_time = start_time + timedelta(minutes=service.duration)
            
            test_email = input("Enter your email address for testing: ").strip()
            if not test_email:
                test_email = "dambazolbayar@gmail.com"
            
            booking = Booking(
                user_name="Test User",
                email=test_email,
                service_id=service.id,
                start_time=start_time,
                end_time=end_time,
                status="pending"
            )
            
            print(f"📧 Test booking:")
            print(f"   Name: {booking.user_name}")
            print(f"   Email: {booking.email}")
            print(f"   Service: {service.name}")
            print(f"   Start: {booking.start_time}")
            print(f"   End: {booking.end_time}")
            
            # Don't save to database, just test email
            print("📧 Testing email sending...")
            
            # Import here to avoid circular imports
            from flask_mail import Message
            from flask_app import mail
            
            # Send confirmation email
            msg = Message(
                subject=f"🌟 Booking Confirmation - {service.name}",
                recipients=[booking.email],
                sender=app.config.get('MAIL_DEFAULT_SENDER'),
                body=f"""Hello {booking.user_name},

Thank you for booking with HolisticWeb! ✨

📌 Service: {service.name}
💰 Price: ${service.price}
🕒 Start: {booking.start_time.strftime("%Y-%m-%d %H:%M")}
🕒 End:   {booking.end_time.strftime("%Y-%m-%d %H:%M")}

{service.description}

We look forward to seeing you!

Best regards,
- The HolisticWeb Team

If you need to reschedule or have any questions, please contact us.
"""
            )
            
            mail.send(msg)
            print(f"✅ Booking confirmation email sent successfully to {booking.email}")
            
            # Also send admin notification
            admin_msg = Message(
                subject="📩 New Booking Received (TEST)",
                recipients=["dambazolbayar@gmail.com"],
                sender=app.config.get('MAIL_DEFAULT_SENDER'),
                body=f"""A new booking was created! (THIS IS A TEST)

📌 Service: {service.name} (ID: {service.id})
📅 Date: {booking.start_time.strftime("%Y-%m-%d %H:%M")} - {booking.end_time.strftime("%Y-%m-%d %H:%M")}
👤 Customer: {booking.user_name}
📧 Email: {booking.email}
💰 Price: ${service.price}

This was a test booking - no actual appointment was created.
"""
            )
            mail.send(admin_msg)
            print("✅ Admin notification sent successfully")
            
        except Exception as e:
            print(f"❌ Booking email test failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=== Booking Email Test ===")
    test_booking_email()
    print("Done!")
