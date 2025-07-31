# app/routes/api/v1/user_api.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging

from app.services.user.user_service import get_user_profile  # Placeholder for actual DB/service call
from app.utils.decorators import api_admin_required  # Optional: admin-only access if needed

user_api_bp = Blueprint("user_api", __name__, url_prefix="/api/v1/users")

logger = logging.getLogger(__name__)


@user_api_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """
    Retrieve profile data for the currently authenticated user.

    Returns:
        JSON response containing user profile fields.
    """
    try:
        profile = get_user_profile(current_user.id)

        if not profile:
            logger.warning(f"Profile not found for user ID: {current_user.id}")
            return jsonify({"error": "User profile not found."}), 404

        return jsonify({
            "user_id": profile.id,
            "email": profile.email,
            "name": profile.name,
            "role": profile.role,
            "created_at": profile.created_at.isoformat()
        })

    except Exception:
        logger.exception("Error fetching current user profile.")
        return jsonify({"error": "Internal server error."}), 500


@user_api_bp.route("/<int:user_id>", methods=["GET"])
@login_required
@api_admin_required
def get_user_by_id(user_id):
    """
    Admin-only: Fetch profile for any user by ID.

    Args:
        user_id (int): ID of the target user.

    Returns:
        JSON profile data or error response.
    """
    try:
        profile = get_user_profile(user_id)

        if not profile:
            logger.info(f"User with ID {user_id} not found.")
            return jsonify({"error": "User not found."}), 404

        return jsonify({
            "user_id": profile.id,
            "email": profile.email,
            "name": profile.name,
            "role": profile.role,
            "created_at": profile.created_at.isoformat()
        })

    except Exception:
        logger.exception(f"Error retrieving user by ID: {user_id}")
        return jsonify({"error": "Internal server error."}), 500