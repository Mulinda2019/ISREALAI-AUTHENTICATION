# app/routes/api/v1/__init__.py

from flask import Blueprint
import logging

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


def register_api_v1_routes(app):
    """
    Register all versioned (v1) API blueprints under /api/v1.

    Args:
        app (Flask): The Flask application instance.
    """
    try:
        from .user_api import user_api_bp
        from .subscription_api import subscription_api_bp

        # Register sub-blueprints onto versioned parent
        api_v1_bp.register_blueprint(user_api_bp)
        api_v1_bp.register_blueprint(subscription_api_bp)

        # Attach main versioned blueprint to app
        app.register_blueprint(api_v1_bp)

        logger.info("API v1 route registration completed.")
        logger.info("Sub-blueprints: user_api, subscription_api successfully mounted under /api/v1")

    except ImportError:
        logger.exception("Failed to import one or more v1 API modules.")
    except Exception:
        logger.exception("Unexpected error occurred during v1 API route registration.")