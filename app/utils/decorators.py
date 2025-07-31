# app/utils/decorators.py

"""
Authentication and authorization decorators for ISREALAI Technologies.

Includes login enforcement, role-based admin checks, API-specific admin decorator,
and public-route protection for authenticated users. Supports error handling
and future role extensibility. Also provides safe_render helper to centralize
template rendering, with empty-template detection.
"""

from functools import wraps
from typing import Callable
from flask import (
    session,
    flash,
    redirect,
    url_for,
    request,
    Response,
    render_template,
    abort,
    current_app,
    jsonify,
)
from app.models.user import User
from jinja2 import TemplateNotFound
import logging

logger = logging.getLogger(__name__)

# Role constants
ADMIN_ROLE = "admin"


def login_required(view_func: Callable[..., Response]) -> Callable[..., Response]:
    """
    Requires user to be logged in.
    Redirects to login page if not authenticated.
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs) -> Response:
        user_id = session.get("user_id")
        if not user_id:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapped_view


def admin_required(view_func: Callable[..., Response]) -> Callable[..., Response]:
    """
    Requires user to have admin privileges.
    Assumes User model has 'role' and 'is_active' fields.
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs) -> Response:
        user_id = session.get("user_id")
        if not user_id:
            flash("Access denied. Please log in first.", "warning")
            return redirect(url_for("auth.login"))

        try:
            user = User.query.get(user_id)
        except Exception as e:
            logger.error(f"DB error during admin check: {e}")
            flash("An error occurred. Please try again later.", "danger")
            return redirect(url_for("auth.login"))

        if not user or getattr(user, "role", "") != ADMIN_ROLE or not getattr(user, "is_active", True):
            flash("Admin access required.", "danger")
            logger.warning(f"Unauthorized admin access attempt from user_id: {user_id}")
            return redirect(url_for("dashboard.home"))

        return view_func(*args, **kwargs)
    return wrapped_view


def api_admin_required(view_func: Callable[..., Response]) -> Callable[..., Response]:
    """
    API-only decorator: requires user to be logged in and have admin role.
    Returns JSON 401 or 403 on failure.
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Authentication required."}), 401

        try:
            user = User.query.get(user_id)
        except Exception as e:
            logger.error(f"DB error during API admin check: {e}")
            return jsonify({"error": "Internal server error."}), 500

        if not user or getattr(user, "role", "") != ADMIN_ROLE or not getattr(user, "is_active", True):
            return jsonify({"error": "Admin privileges required."}), 403

        return view_func(*args, **kwargs)
    return wrapped_view


def prevent_authenticated_access(view_func: Callable[..., Response]) -> Callable[..., Response]:
    """
    Prevents authenticated users from accessing public routes
    such as login, register, or reset password.
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs) -> Response:
        if session.get("user_id"):
            flash("You are already logged in.", "info")
            return redirect(url_for("dashboard.home"))
        return view_func(*args, **kwargs)
    return wrapped_view


def safe_render(template_name: str, **context):
    """
    Safely render a template or fallback to under_construction if
    the template is missing or its rendered output is blank.
    """
    try:
        rendered = render_template(template_name, **context)

        # If the template exists but is empty, show placeholder
        if not rendered.strip():
            current_app.logger.warning(
                f"Template '{template_name}' is empty—using placeholder."
            )
            return render_template(
                "placeholders/under_construction.html", **context
            )

        return rendered

    except TemplateNotFound:
        current_app.logger.warning(
            f"Template '{template_name}' not found—using placeholder."
        )
        return render_template(
            "placeholders/under_construction.html", **context
        )