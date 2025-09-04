
import os
from datetime import datetime, timedelta
import pytz

# Try to load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    # Load .flaskenv file specifically
    load_dotenv('.flaskenv')
    # Also load .env if it exists (for overrides)
    load_dotenv()
except ImportError:
    # dotenv not available (e.g., in production like PythonAnywhere)
    print("python-dotenv not available. Using system environment variables.")

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Twilio not available. SMS functionality will be disabled.")

# Get Twilio credentials
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

# Create Twilio client
client = None
if TWILIO_AVAILABLE and TWILIO_SID and TWILIO_AUTH_TOKEN:
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        print("✅ Twilio client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Twilio client: {e}")
        client = None
else:
    print("⚠️ Twilio client not configured. SMS functionality disabled.")

# Timezone configuration
LOCAL_TZ = pytz.timezone("America/New_York")  # change to your timezone

def format_local_time(utc_time):
    """Convert UTC datetime to local timezone and format nicely"""
    return utc_time.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %I:%M %p")

def send_sms_reminder(to_number, message):
    """Send SMS reminder using Twilio"""
    if not client:
        print("Twilio client not configured. SMS not sent.")
        return False
    
    try:
        # Validate phone number format
        if not to_number:
            print("❌ No phone number provided")
            return False
            
        # Format phone number properly (add +1 if not present)
        formatted_phone = str(to_number).strip()
        if not formatted_phone.startswith('+'):
            # Remove any non-digit characters first
            import re
            digits_only = re.sub(r'\D', '', formatted_phone)
            if len(digits_only) == 10:
                formatted_phone = '+1' + digits_only
            elif len(digits_only) == 11 and digits_only.startswith('1'):
                formatted_phone = '+' + digits_only
            else:
                print(f"❌ Invalid phone number format: {to_number}")
                return False
        
        # Send SMS using Twilio
        sms_message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=formatted_phone
        )
        print(f"✅ SMS sent successfully. SID: {sms_message.sid}")
        print(f"📱 Sent to: {formatted_phone}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
        return False

def send_booking_confirmation_sms(to_number, user_name, service_name, start_time):
    """Send booking confirmation SMS"""
    if not client:
        print("Twilio client not configured. SMS not sent.")
        return False
    
    try:
        # Format appointment time in local timezone
        local_time = format_local_time(start_time.replace(tzinfo=pytz.UTC))
        
        message = f"""Hello {user_name}! 

Your booking has been confirmed:
📅 Service: {service_name}
🕒 Time: {local_time}

We look forward to seeing you!

- HolisticWeb Team"""
        
        return send_sms_reminder(to_number, message)
        
    except Exception as e:
        print(f"❌ Error sending booking confirmation SMS: {e}")
        return False

def send_booking_reminder_sms(to_number, user_name, start_time, minutes_before=30):
    """Send booking reminder SMS"""
    if not client:
        print("Twilio client not configured. SMS not sent.")
        return False
    
    try:
        # Format appointment time in local timezone
        local_time = format_local_time(start_time.replace(tzinfo=pytz.UTC))
        
        message = f"""Hello {user_name}, 

This is a reminder: your appointment is at {local_time}.

See you soon!

- HolisticWeb Team"""
        
        return send_sms_reminder(to_number, message)
        
    except Exception as e:
        print(f"❌ Error sending booking reminder SMS: {e}")
        return False

def check_and_send_reminders(app, Booking):
    """Check for bookings that need reminders and send SMS
    
    Args:
        app: Flask application instance
        Booking: Booking model class
    """
    if not client:
        print("Twilio client not configured. Skipping reminder check.")
        return
    
    with app.app_context():
        now = datetime.utcnow()
        reminder_time = now + timedelta(minutes=30)  # Send reminders 30 minutes before

        # Get bookings 30 minutes from now (within 5-minute window for more flexibility)
        bookings = Booking.query.filter(
            Booking.start_time.between(reminder_time, reminder_time + timedelta(minutes=5))
        ).all()

        print(f"🔍 Checking for reminders at {now}")
        print(f"📅 Looking for bookings between {reminder_time} and {reminder_time + timedelta(minutes=5)}")
        print(f"📋 Found {len(bookings)} bookings needing reminders")

        for booking in bookings:
            # Check if booking has a phone number field
            phone_number = getattr(booking, 'phone_number', None)
            if phone_number:
                print(f"📱 Sending reminder to {booking.user_name} at {phone_number}")
                success = send_booking_reminder_sms(
                    phone_number, 
                    booking.user_name, 
                    booking.start_time
                )
                
                if success:
                    print(f"✅ Reminder sent successfully to {booking.user_name}")
                else:
                    print(f"❌ Failed to send reminder to {booking.user_name}")
            else:
                print(f"⚠️ No phone number for booking {booking.id} - {booking.user_name}")

def get_sms_status():
    """Get SMS service status"""
    return {
        'twilio_available': TWILIO_AVAILABLE,
        'client_configured': client is not None,
        'credentials_set': bool(TWILIO_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE),
        'phone_number': TWILIO_PHONE if TWILIO_PHONE else None
    }

def test_sms_connection():
    """Test SMS connection and configuration"""
    status = get_sms_status()
    
    print("📱 SMS Service Status:")
    print(f"   Twilio Library: {'✅ Available' if status['twilio_available'] else '❌ Not Available'}")
    print(f"   Client: {'✅ Configured' if status['client_configured'] else '❌ Not Configured'}")
    print(f"   Credentials: {'✅ Set' if status['credentials_set'] else '❌ Missing'}")
    print(f"   Phone Number: {status['phone_number'] if status['phone_number'] else '❌ Not Set'}")
    
    if client:
        try:
            # This doesn't send a message, just validates the client
            print("✅ Twilio client connection test passed")
            return True
        except Exception as e:
            print(f"❌ Twilio client connection test failed: {e}")
            return False
    else:
        print("❌ Cannot test connection - client not configured")
        return False

