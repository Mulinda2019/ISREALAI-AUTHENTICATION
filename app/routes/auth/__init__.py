# app/routes/auth/__init__.py

"""
Authentication blueprint initializer for ISREALAI Technologies.

Handles:
- Login routes (login.py)
- Registration routes (register.py)
- Email verification (verify.py)
- Password reset flows (reset.py)

Provides the 'auth' blueprint for namespacing all authentication-related endpoints.
"""

from flask import Blueprint

bp = Blueprint("auth", __name__, url_prefix="/auth")

# alias for consistency in imports elsewhere
auth_bp = bp

# Explicit module export (improves IDE discoverability and import control)
__all__ = ["bp", "auth_bp"]

# Ensure modular routes are registered
# These modules should only define routes and bind them to 'bp' — no side effects.
from . import login, register, verify, reset