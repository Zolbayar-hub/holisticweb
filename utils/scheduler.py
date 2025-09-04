"""
Background scheduler setup for SMS reminders
"""

from routes.send_sms import check_and_send_reminders


def create_scheduler_function(app):
    """Create a scheduler function with app context"""
    
    def check_and_send_reminders_with_context():
        """Check for bookings that need reminders and send SMS"""
        from db.models import Booking
        check_and_send_reminders(app, Booking)
    
    return check_and_send_reminders_with_context


def init_scheduler(app):
    """Initialize the background scheduler for SMS reminders"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        
        scheduler = BackgroundScheduler()
        reminder_function = create_scheduler_function(app)
        scheduler.add_job(func=reminder_function, trigger="interval", minutes=5)
        scheduler.start()
        
        print("📅 SMS reminder scheduler started - checking every 5 minutes")
        return scheduler
        
    except Exception as e:
        print(f"❌ Failed to start scheduler: {e}")
        print("💡 Tip: Run the Flask app and use manual reminders instead")
        return None
