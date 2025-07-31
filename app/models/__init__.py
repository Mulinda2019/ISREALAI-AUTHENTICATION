"""
app/models/__init__.py

Initialize SQLAlchemy models for ISREALAI Technologies.
This file enables `import models` access across the application.
"""

from app.extensions import db
from .user import User
from .subscription import Subscription
from .admin import Admin
from .audit_log import AuditLog

__all__ = [
    "User",
    "Subscription",
    "Admin",
    "AuditLog",
    "register_models",
]

def register_models():
    """
    Return a dictionary of model references for use in CLI, shell context,
    admin tools, or interactive debugging.
    """
    return {
        "db": db,
        "User": User,
        "Subscription": Subscription,
        "Admin": Admin,
        "AuditLog": AuditLog,
    }