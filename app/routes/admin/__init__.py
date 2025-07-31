# app/routes/admin/__init__.py

from flask import Blueprint
import logging

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
logger = logging.getLogger(__name__)


def register_admin_routes(app):
    """
    Register all admin-related routes to the Flask app instance.

    Args:
        app (Flask): The main Flask application instance.
    """
    try:
        from .dashboard import dashboard_bp
        from .users import users_bp
        from .database import database_bp

        # Register route blueprints
        app.register_blueprint(admin_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(users_bp)
        app.register_blueprint(database_bp)

        # Confirmation log for successful registration
        logger.info("Admin routes registered successfully.")

    except ImportError:
        logger.exception("Failed to import one or more admin route modules.")
    except Exception:
        logger.exception("Unexpected error occurred while registering admin routes.")