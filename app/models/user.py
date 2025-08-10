"""
app/models/user.py

Defines the User model for ISREALAI Technologies.
Handles authentication, profile, audit trail, and relationships.
"""

from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_email_verified = db.Column(db.Boolean, default=False)

    # Alias for tests expecting 'is_verified'
    @property
    def is_verified(self) -> bool:
        return self.is_email_verified

    @is_verified.setter
    def is_verified(self, value: bool) -> None:
        self.is_email_verified = value

    # Profile
    full_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)

    # Status & Access
    role = db.Column(db.String(20), default="user")  # roles: "user", "admin", etc.
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

    # Activity tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    subscriptions = db.relationship(
        "Subscription",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    audit_logs = db.relationship(
        "AuditLog",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    # Password handling
    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    # Login tracker
    def mark_login(self) -> None:
        self.last_login = datetime.utcnow()

    # Account management
    def soft_delete(self) -> None:
        self.is_deleted = True
        self.is_active = False

    # Role checks
    def is_admin(self) -> bool:
        return self.role.lower() == "admin"

    # Name resolver
    # Backward compatibility property
    @property
    def username(self) -> str:
        return self.name

    @username.setter
    def username(self, value: str) -> None:
        self.name = value

    def get_full_name(self) -> str:
        return self.full_name or self.name

    def __repr__(self):
        return f"<User {self.name} ({self.email})>"
