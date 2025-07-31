# app/routes/admin/dashboard.py

from flask import Blueprint
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
import logging

from app.utils.decorators import safe_render, admin_required  # Modular decorator for DRY access control

dashboard_bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin/dashboard")

logger = logging.getLogger(__name__)


@dashboard_bp.route("/", methods=["GET"])
@login_required
@admin_required
def admin_dashboard():
    """
    Render the administrative dashboard for privileged users.

    Returns:
        HTML dashboard view or fallback template if unavailable.
    """
    try:
        # Placeholder stats (TASK-20250723-192149-0809) for layout scaffolding and template binding
        context = {
            "user": current_user,
            "title": "Admin Dashboard — ISREALAI",
            "stats": {
                "active_users": 0,
                "pending_logs": 0,
                "system_health": "OK"
            }
        }

        return safe_render("admin/dashboard.html", context)

    except TemplateNotFound:
        logger.warning("Admin dashboard template not found. Fallback initiated.")
        return safe_render("placeholders/under_construction.html")

    except Exception:
        logger.exception("Unexpected error during admin dashboard rendering.")
        return safe_render("placeholders/under_construction.html")