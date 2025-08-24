from flask import Flask, render_template, redirect, url_for, flash, session, send_from_directory
import markdown as md
from db import db
from datetime import datetime
import os
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from db.models import User, Role, GeneratedContent
from werkzeug.security import generate_password_hash
from flask_babel import Babel
from flask_login import LoginManager, current_user

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

if CORS_AVAILABLE:
    CORS(app, supports_credentials=True)

db.init_app(app)
babel = Babel(app)

# ---- Login Manager ----
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---- Blueprints ----
from routes.auth import auth_bp
app.register_blueprint(auth_bp)

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
    db.create_all()

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

# ✅ Only keep these three
admin.add_view(UserModelView(User, db.session))
admin.add_view(RoleModelView(Role, db.session))
admin.add_view(GeneratedContentModelView(GeneratedContent, db.session))

# ---- Run ----
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

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

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=app.config['DEBUG'],
        threaded=True
    )

