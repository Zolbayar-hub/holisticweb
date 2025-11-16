# Testimonials Feature

**Complete standalone testimonials system**

## Files in this feature:
- `testimonials.py` - All routes and logic
- `templates/` - All HTML templates
- `static/` - All CSS and JavaScript files

## Installation:
1. Copy this entire folder to your Flask app
2. Import the blueprint: `from features.testimonials.testimonials import testimony_bp`
3. Register it: `app.register_blueprint(testimony_bp)`

## Dependencies:
- Flask-Mail
- Flask-Login

## Database Models Required:
- Testimonial

## Routes:
- `/testimonials/submit` - Public submission form
- `/testimonials/api/approved` - API for approved testimonials
- `/testimonials/api/featured` - API for featured testimonials
- `/testimonials/admin` - Admin management page
- `/testimonials/admin/<id>/approve` - Approve testimonial
- `/testimonials/admin/<id>/feature` - Toggle featured status
- `/testimonials/admin/<id>/delete` - Delete testimonial

## To Remove:
Simply delete this entire `features/testimonials/` folder and remove the blueprint registration from your app.

## Features:
- ✅ Public testimonial submission
- ✅ Admin approval system
- ✅ Featured testimonials
- ✅ Email notifications
- ✅ API endpoints for display
- ✅ Star ratings
- ✅ Complete admin management
