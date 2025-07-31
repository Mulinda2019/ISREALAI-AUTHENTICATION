# app/routes/admin/users.py

from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
import logging

from app.utils.decorators import safe_render, admin_required
from app.services.admin.admin_service import get_all_users  # Placeholder for real service call

users_bp = Blueprint("admin_users", __name__, url_prefix="/admin/users")

logger = logging.getLogger(__name__)


@users_bp.route("/", methods=["GET"])
@login_required
@admin_required
def manage_users():
    """
    Render the user management interface for administrators.

    Returns:
        HTML view listing user accounts, or fallback page if template is missing.
    """
    try:
        # Pull all users (mocked for now, real DB logic goes in admin_service)
        users = get_all_users() or []

        context = {
            "user": current_user,
            "title": "Manage Users — ISREAL.AI",
            "users": users
        }

        return safe_render("admin/manage_users.html", context)

    except TemplateNotFound:
        logger.warning("User management template not found. Fallback triggered.")
        return safe_render("placeholders/under_construction.html")

    except Exception:
        logger.exception("Unexpected error while rendering admin user management view.")
        return safe_render("placeholders/under_construction.html")