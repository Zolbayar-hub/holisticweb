from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from datetime import datetime



class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # viewer, editor, admin, owner
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Role {self.name}>"


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_paid = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<User {self.username}, Role {self.role.name}>"

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Checks the provided password against the stored hash."""
        return check_password_hash(self.password, password)


class GeneratedContent(db.Model):
    __tablename__ = 'generated_content'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    code = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(512), nullable=True)
    image_prompt = db.Column(db.Text, nullable=True)
    user_name = db.Column(db.Text, nullable=True)
    input_data = db.Column(db.Text, nullable=True)
    output_data = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=db.func.now())
    posted = db.Column(db.Boolean, default=False, nullable=False)
    posted_at = db.Column(db.DateTime, nullable=True)
    when_post = db.Column(db.Text, nullable=True)

    twitter_id = db.Column(db.String(255), nullable=True)  # Twitter/X tweet ID
    is_reposted = db.Column(db.Boolean, default=False, nullable=False)
    reposted_at = db.Column(db.DateTime, nullable=True)
    

    def __repr__(self):
        return f"<GeneratedContent id={self.id} topic={self.topic}>"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)  # Added for SMS reminders
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    admin_notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Booking {self.user_name} {self.start_time}>"
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)
    service = db.relationship("Service", backref="bookings")
    

class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    image_path = db.Column(db.String(255), nullable=True)  # Path to service image

    def __repr__(self):
        return f"<Service {self.name}>"


class SiteSetting(db.Model):
    __tablename__ = "site_settings"
    __table_args__ = (
        db.UniqueConstraint('key', 'language', name='uq_site_settings_key_language'),
    )

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    language = db.Column(db.String(3), nullable=False, default='ENG')  # ENG or MON
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<SiteSetting {self.key} ({self.language})>"


class EmailTemplate(db.Model):
    __tablename__ = "email_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<EmailTemplate {self.name}>"

class Testimonial(db.Model):
    __tablename__ = "testimonials"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_title = db.Column(db.String(100), nullable=True)  # Job title or profession
    testimonial_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)  # 1-5 star rating
    is_approved = db.Column(db.Boolean, default=False, nullable=False)  # Admin approval
    is_featured = db.Column(db.Boolean, default=False, nullable=False)  # Show on homepage
    email = db.Column(db.String(120), nullable=True)  # Optional client email
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    approver = db.relationship('User', backref=db.backref('approved_testimonials', lazy=True))

    def __repr__(self):
        return f"<Testimonial {self.client_name} - {'Approved' if self.is_approved else 'Pending'}>"

    def get_star_display(self):
        """Returns star rating as emoji string"""
        return "⭐" * self.rating


class AboutImage(db.Model):
    __tablename__ = "about_images"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # Display title for the image
    caption = db.Column(db.String(255), nullable=True)  # Caption text that appears on the image
    image_path = db.Column(db.String(255), nullable=False)  # Path to the image file
    sort_order = db.Column(db.Integer, nullable=False, default=0)  # Order in the carousel
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Whether to show this image
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<AboutImage {self.title} - {'Active' if self.is_active else 'Inactive'}>"
