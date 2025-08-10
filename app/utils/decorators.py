"""Minimal decorators and template helper used in tests."""

from functools import wraps
import logging
from flask import render_template, current_app, session, redirect, url_for, flash
from jinja2 import TemplateNotFound


def safe_render(template_name: str, **context):
    """Render a template, falling back to a simple placeholder."""

    try:
        return render_template(template_name, **context)
    except TemplateNotFound:
        current_app.logger.warning(
            f"Template '{template_name}' not found—using placeholder."
        )
        return render_template("placeholders/under_construction.html", **context)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("user_role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard.home"))
        return view(*args, **kwargs)

    return wrapper


def api_admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("user_role") != "admin":
            return {"error": "Admin privileges required."}, 403
        return view(*args, **kwargs)

    return wrapper


def prevent_authenticated_access(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("user_id"):
            return redirect(url_for("dashboard.home"))
        return view(*args, **kwargs)

    return wrapper

