"""
app/models/admin.py

Defines the Admin model for ISREALAI Technologies.
Handles identity, access levels, and secure session metadata.
"""

from datetime import datetime
from sqlalchemy import Enum
from flask_login import UserMixin
from app.extensions import db, bcrypt

class Admin(UserMixin, db.Model):
    """
    Represents an administrative user of the ISREALAI platform.
    Supports roles, session tracking, and potential soft deletion.
    """

    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    # Identity
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    full_name = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)

    # Access & Status
    role = db.Column(
        Enum("admin", "superadmin", name="admin_roles"),
        default="admin",
        nullable=False,
        index=True
    )
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def mark_login(self) -> None:
        self.last_login = datetime.utcnow()

    def soft_delete(self) -> None:
        self.is_active = False
        self.is_deleted = True

    def is_superadmin(self) -> bool:
        return self.role == "superadmin"

    def get_full_name(self) -> str:
        return self.full_name or self.username

    def __repr__(self):
        return f"<Admin {self.username} ({self.email})>"