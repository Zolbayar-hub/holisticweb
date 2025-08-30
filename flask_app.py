from dotenv import load_dotenv
# Load .flaskenv file specifically
load_dotenv('.flaskenv')
# Also load .env if it exists (for overrides)
load_dotenv()

from flask import Flask, render_template, redirect, url_for, flash, request, session, send_from_directory
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import markdown as md
from db import db
from flask_migrate import Migrate
from datetime import datetime
import os
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from db.models import User, Role, GeneratedContent, Booking, Service
from werkzeug.security import generate_password_hash
from flask_babel import Babel
from flask_login import LoginManager, current_user
from routes.booking import booking_bp


# Optional: CORS for local development
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("Flask-CORS not installed. Skipping...")

# ---- Flask Setup ----
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ---- Mail Config ----
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@holisticweb.com')
app.config['MAIL_TIMEOUT'] = 10  # Add 10 second timeout

# Debug email configuration
print("📧 Email Configuration:")
print(f"   Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
print(f"   TLS: {app.config['MAIL_USE_TLS']}, SSL: {app.config['MAIL_USE_SSL']}")
print(f"   Username: {'✅ Set' if app.config['MAIL_USERNAME'] else '❌ Not set'}")
print(f"   Password: {'✅ Set' if app.config['MAIL_PASSWORD'] else '❌ Not set'}")

mail = Mail(app)

# ---- Test Mail Route ----
@app.route("/send-email")
def send_email():
    try:
        msg = Message("Test Email", recipients=["dambazolbayar@gmail.com"])
        msg.body = "This is a test email from Flask."
        mail.send(msg)
        return "Email sent!"
    except Exception as e:
        return f"Email failed: {e}"

# ---- Enable CORS ----
if CORS_AVAILABLE:
    CORS(app, supports_credentials=True)

# ---- Init DB + Migrate + Babel ----
db.init_app(app)
migrate = Migrate(app, db)
babel = Babel(app)

# ---- Login Manager ----
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---- Register Blueprints ----
from routes.auth import auth_bp
app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)

# ---- Booking with Email Confirmation ----
@app.route("/bookings/new", methods=["GET", "POST"])
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

            # ---- Send confirmation email (non-blocking) ----
            service = Service.query.get(new_booking.service_id)
            if app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"):
                import threading
                
                def send_email_async():
                    """Send email in background thread to avoid blocking the request"""
                    try:
                        with app.app_context():
                            # ---- Send confirmation email to customer ----
                            print(f"📧 [Background] Sending confirmation email to {new_booking.email}")
                            msg = Message(
                                subject=f"🌟 Booking Confirmation - {service.name if service else 'HolisticWeb'}",
                                recipients=[new_booking.email],
                                sender=app.config.get('MAIL_DEFAULT_SENDER'),
                                body=f"""Hello {new_booking.user_name},

Thank you for booking with HolisticWeb! ✨

📌 Service: {service.name if service else "Unknown"}
💰 Price: ${service.price if service else "N/A"}
🕒 Start: {new_booking.start_time.strftime("%Y-%m-%d %H:%M")}
🕒 End:   {new_booking.end_time.strftime("%Y-%m-%d %H:%M")}

{service.description if service else ""}

We look forward to seeing you!

Best regards,
- The HolisticWeb Team

If you need to reschedule or have any questions, please contact us.
"""
                            )
                            
                            mail.send(msg)
                            print(f"✅ [Background] Confirmation email sent successfully to {new_booking.email}")
                            
                            # ---- Send notification email to admin ----
                            try:
                                admin_msg = Message(
                                    subject="📩 New Booking Received",
                                    recipients=["dambazolbayar@gmail.com"],   # replace with your admin email
                                    sender=app.config.get('MAIL_DEFAULT_SENDER'),
                                    body=f"""A new booking was created!

📌 Service: {service.name if service else "Unknown"} (ID: {new_booking.service_id})
📅 Date: {new_booking.start_time.strftime("%Y-%m-%d %H:%M")} - {new_booking.end_time.strftime("%Y-%m-%d %H:%M")}
👤 Customer: {new_booking.user_name}
📧 Email: {new_booking.email}
💰 Price: ${service.price if service else "N/A"}

Booking ID: {new_booking.id}

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
                
                # User gets immediate feedback without waiting for email
                flash("Booking created ✅ Email confirmation being sent...", "success")
                
            else:
                print("📧 Email credentials not configured")
                flash("Booking created ✅ (Email not configured)", "info")

            return redirect(url_for("home"))

        except Exception as e:
            flash(f"Error creating booking: {e}", "error")
            return redirect(url_for("create_booking"))

    services = Service.query.all()
    return render_template("new_booking.html", services=services)



# ---- Error Handlers ----
@app.errorhandler(500)
def internal_error(error):
    print(f"Internal server error: {error}")
    return f"Internal Server Error: {error}", 500

@app.errorhandler(404)
def not_found_error(error):
    print(f"404 error: {error}")
    return f"Not Found: {error}", 404

# ---- Health Check ----
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'Server is running'}, 200

# ---- Markdown filter ----
@app.template_filter('markdown')
def markdown_filter(text):
    return md.markdown(text or "", extensions=['fenced_code', 'codehilite', 'tables'])

# ---- Static Images ----
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(app.static_folder, 'images'), filename)

# ---- DB Init ----
with app.app_context():
    try:
        # Try to create all tables
        db.create_all()
        
        # Test if booking table has service_id column
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'booking' in inspector.get_table_names():
            columns = inspector.get_columns('booking')
            column_names = [col['name'] for col in columns]
            
            if 'service_id' not in column_names:
                print("Missing service_id column. Recreating database...")
                db.drop_all()
                db.create_all()
                print("Database recreated with service_id column.")
                
    except Exception as e:
        print(f"Database initialization error: {e}")
        print("Recreating database...")
        try:
            db.drop_all()
            db.create_all()
            print("Database recreated successfully.")
        except Exception as e2:
            print(f"Failed to recreate database: {e2}")

# ---- Helpers ----
def is_admin():
    return current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role.name == 'admin'

# ---- Flask-Admin ----
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login') if 'user_id' not in session else '/')

admin = Admin(app, name='Admin Panel', template_mode='bootstrap4', index_view=MyAdminIndexView())

class RoleModelView(ModelView):
    column_list = ('id', 'name')
    form_columns = ('name',)
    def is_accessible(self): return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))

class UserModelView(ModelView):
    column_list = ('id', 'username', 'email', 'role_id')
    column_exclude_list = ['password']
    form_excluded_columns = ['password']
    def is_accessible(self): return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))
    def on_model_change(self, form, model, is_created):
        if is_created and hasattr(form, 'password') and form.password.data:
            model.set_password(form.password.data)

class GeneratedContentModelView(ModelView):
    column_list = ('id', 'topic', 'content_preview', 'image_url', 'posted', 'posted_at')
    column_labels = {'content_preview': 'Content Preview'}
    form_columns = ('topic', 'content', 'image_url', 'image_prompt', 'user_name', 'when_post', 'code', 'input_data', 'posted', 'output_data', 'is_reposted')
    column_searchable_list = ['topic', 'content']
    column_filters = ['posted', 'created_at', 'posted_at']
    column_default_sort = ('created_at', True)

    def _format_datetime(self, context, model, name):
        value = getattr(model, name)
        return value.strftime('%Y-%m-%d %H:%M:%S') if value else '-'

    def _format_boolean(self, context, model, name):
        return '✓' if getattr(model, name) else '✗'

    def _format_content_preview(self, context, model, name):
        return (model.content[:100] + '...') if model.content and len(model.content) > 100 else (model.content or '-')

    column_formatters = {
        'created_at': _format_datetime,
        'posted_at': _format_datetime,
        'posted': _format_boolean,
        'content_preview': _format_content_preview
    }

    def is_accessible(self): return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))
    def on_model_change(self, form, model, is_created):
        if model.posted and not model.posted_at:
            model.posted_at = datetime.utcnow()
        elif not model.posted:
            model.posted_at = None

class BookingAdminView(ModelView):
    column_list = ('id', 'user_name', 'email', 'service', 'start_time', 'end_time', 'status', 'admin_notes', 'created_at')
    column_filters = ['status', 'service', 'start_time', 'created_at']
    form_columns = ('user_name', 'email', 'service', 'start_time', 'end_time', 'status', 'admin_notes')
    def is_accessible(self): return is_admin()
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))
    
class ServiceAdminView(ModelView):
    column_list = ('id', 'name', 'price', 'description')
    column_searchable_list = ['name']
    column_filters = ['price']
    form_columns = ('name', 'description', 'price')

    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('auth.login'))



# ✅ Only keep these three
admin.add_view(UserModelView(User, db.session))
admin.add_view(RoleModelView(Role, db.session))
admin.add_view(GeneratedContentModelView(GeneratedContent, db.session))
admin.add_view(BookingAdminView(Booking, db.session))
admin.add_view(ServiceAdminView(Service, db.session))


# ---- Run ----
if __name__ == '__main__':
    with app.app_context():
        try:
            # Try to create all tables
            db.create_all()
            
            # Test if booking table has service_id column
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'booking' in inspector.get_table_names():
                columns = inspector.get_columns('booking')
                column_names = [col['name'] for col in columns]
                
                if 'service_id' not in column_names:
                    print("Missing service_id column. Recreating database...")
                    db.drop_all()
                    db.create_all()
                    print("Database recreated with service_id column.")
                    
        except Exception as e:
            print(f"Database initialization error: {e}")
            print("Recreating database...")
            try:
                db.drop_all()
                db.create_all()
                print("Database recreated successfully.")
            except Exception as e2:
                print(f"Failed to recreate database: {e2}")

        # Insert roles if missing
        if not Role.query.first():
            roles = [
                Role(id=1, name='viewer'),
                Role(id=2, name='editor'),
                Role(id=3, name='admin')
            ]
            db.session.bulk_save_objects(roles)
            db.session.commit()

        # Insert admin user if missing
        if not User.query.filter_by(email='admin@example.com').first():
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role_id=3
            )
            db.session.add(admin_user)
            db.session.commit()

        # Insert sample services if missing
        if not Service.query.first():
            services = [
                Service(name='Mindfulness Therapy', description='Learn to be present and cultivate inner peace through guided mindfulness practices and meditation techniques.', price=80.0, duration=60),
                Service(name='Body Work', description='Release physical tension and restore balance through therapeutic massage, acupuncture, and energy healing.', price=100.0, duration=90),
                Service(name='Spiritual Guidance', description='Connect with your inner wisdom and explore your spiritual path through personalized guidance and support.', price=70.0, duration=60),
                Service(name='Nutritional Wellness', description='Nourish your body with personalized nutrition plans that support your overall health and vitality.', price=60.0, duration=45),
                Service(name='Creative Therapy', description='Express and heal through art, music, and movement therapy designed to unlock your creative potential.', price=75.0, duration=60),
                Service(name='Relationship Healing', description='Strengthen your connections with others and yourself through relationship counseling and communication skills.', price=90.0, duration=75)
            ]
            db.session.bulk_save_objects(services)
            db.session.commit()
            print("Sample services added to database.")

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=app.config['DEBUG'],
        threaded=True
    )

