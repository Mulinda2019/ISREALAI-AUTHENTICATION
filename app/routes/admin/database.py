# app/routes/admin/database.py

from flask import Blueprint, request
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
import logging

from app.utils.decorators import safe_render, admin_required
from app.services.admin.admin_service import get_database_summary  # Placeholder for actual logic

database_bp = Blueprint("admin_database", __name__, url_prefix="/admin/database")

logger = logging.getLogger(__name__)


@database_bp.route("/", methods=["GET"])
@login_required
@admin_required
def database_console():
    """
    Render the database console interface for admins.

    Returns:
        HTML view with database insights or fallback page.
    """
    try:
        # Fetch database summary (tables, size, engine etc.)
        summary = get_database_summary() or {}

        context = {
            "user": current_user,
            "title": "Database Console — ISREAL.AI",
            "db_summary": summary
        }

        return safe_render("admin/db_console.html", context)

    except TemplateNotFound:
        logger.warning("Database console template not found. Fallback activated.")
        return safe_render("placeholders/under_construction.html")

    except Exception:
        logger.exception("Unexpected error during admin database view rendering.")
        return safe_render("placeholders/under_construction.html")