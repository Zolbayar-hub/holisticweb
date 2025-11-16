# Booking Feature

**Complete standalone booking system**

## Files in this feature:
- `booking.py` - All routes and logic
- `templates/` - All HTML templates
- `static/` - All CSS and JavaScript files

## Installation:
1. Copy this entire folder to your Flask app
2. Import the blueprint: `from features.booking.booking import booking_bp`
3. Register it: `app.register_blueprint(booking_bp)`

## Dependencies:
- Flask-Mail
- pytz
- twilio (for SMS)

## Database Models Required:
- Booking
- Service
- EmailTemplate

## Routes:
- `/booking/` - Main booking page
- `/booking/calendar` - Calendar view
- `/booking/new` - New booking form
- `/booking/my-bookings` - User bookings
- `/booking/services` - API for services
- `/booking/events` - API for booking events
- `/booking/available-slots` - API for time slots

## To Remove:
Simply delete this entire `features/booking/` folder and remove the blueprint registration from your app.

## Features:
- ✅ Modern booking interface
- ✅ Calendar integration
- ✅ Email confirmations
- ✅ SMS notifications
- ✅ Multi-language support
- ✅ Time slot management
- ✅ Booking search and management
