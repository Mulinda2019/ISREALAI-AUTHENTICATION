# app/routes/dashboard/home.py

from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
import logging

from app.utils.decorators import safe_render

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# Set up module-level logger for production-grade logging
logger = logging.getLogger(__name__)


@dashboard_bp.route("/", methods=["GET"])
@login_required
def home():
    """
    Render the main dashboard view for authenticated users.

    Returns:
        HTML response for dashboard or placeholder if template is missing.
    """
    try:
        # Page-specific context for future dynamic content integration
        context = {
            "user": current_user,
            "title": "Dashboard — ISREAL.AI",
        }

        # Attempt to render main dashboard template
        return safe_render("dashboard/index.html", context)

    except TemplateNotFound:
        # Specific template error handling
        logger.warning("Dashboard template not found. Falling back to placeholder.")
        return safe_render("placeholders/under_construction.html")

    except Exception as e:
        # Catch unforeseen errors and log with full traceback
        logger.exception("Dashboard rendering failed due to unexpected error.")
        return safe_render("placeholders/under_construction.html")