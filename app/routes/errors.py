# app/routes/errors.py

from flask import Blueprint, request
from flask_login import current_user
from jinja2 import TemplateNotFound
import logging

from app.utils.decorators import safe_render

errors_bp = Blueprint("errors", __name__)

logger = logging.getLogger(__name__)


@errors_bp.app_errorhandler(404)
def handle_404_error(error):
    """
    Handle 404 Not Found errors globally.

    Returns:
        Rendered 404 template or fallback page.
    """
    try:
        context = {
            "title": "Page Not Found — ISREAL.AI",
            "user": current_user if not current_user.is_anonymous else None,
            "error": str(error)
        }
        return safe_render("errors/404.html", context), 404

    except TemplateNotFound:
        logger.warning("404 template missing. Fallback to placeholder activated.")
        return safe_render("placeholders/under_construction.html"), 404

    except Exception:
        logger.exception("Unhandled exception in 404 error handler.")
        return safe_render("placeholders/under_construction.html"), 404


@errors_bp.app_errorhandler(500)
def handle_500_error(error):
    """
    Handle 500 Internal Server errors globally.

    Returns:
        Rendered 500 template or fallback page.
    """
    try:
        context = {
            "title": "Server Error — ISREAL.AI",
            "user": current_user if not current_user.is_anonymous else None,
            "error": str(error)
        }
        return safe_render("errors/500.html", context), 500

    except TemplateNotFound:
        logger.warning("500 template missing. Fallback to placeholder activated.")
        return safe_render("placeholders/under_construction.html"), 500

    except Exception:
        logger.exception("Unhandled exception in 500 error handler.")
        return safe_render("placeholders/under_construction.html"), 500