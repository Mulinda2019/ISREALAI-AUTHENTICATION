# app/routes/api/v1/subscription_api.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging

from app.services.subscription.subscription_service import get_user_subscriptions, get_subscription_by_id
from app.utils.decorators import api_admin_required  # Optional: for admin-only views

subscription_api_bp = Blueprint("subscription_api", __name__, url_prefix="/api/v1/subscriptions")

logger = logging.getLogger(__name__)


@subscription_api_bp.route("/me", methods=["GET"])
@login_required
def fetch_my_subscriptions():
    """
    Retrieve all subscriptions associated with the authenticated user.

    Returns:
        JSON list of subscription records.
    """
    try:
        subscriptions = get_user_subscriptions(current_user.id)

        if not subscriptions:
            logger.info(f"No subscriptions found for user: {current_user.email}")
            return jsonify({"subscriptions": []}), 200

        return jsonify({
            "subscriptions": [
                {
                    "id": sub.id,
                    "plan": sub.plan_name,
                    "status": sub.status,
                    "renewal_date": sub.renewal_date.isoformat(),
                    "created_at": sub.created_at.isoformat()
                } for sub in subscriptions
            ]
        })

    except Exception:
        logger.exception("Error retrieving subscriptions for current user.")
        return jsonify({"error": "Internal server error"}), 500


@subscription_api_bp.route("/<int:subscription_id>", methods=["GET"])
@login_required
@api_admin_required
def fetch_subscription_by_id(subscription_id):
    """
    Admin-only: Fetch detailed info about a specific subscription by ID.

    Args:
        subscription_id (int): ID of the target subscription.

    Returns:
        JSON subscription data or error response.
    """
    try:
        sub = get_subscription_by_id(subscription_id)

        if not sub:
            logger.info(f"Subscription with ID {subscription_id} not found.")
            return jsonify({"error": "Subscription not found"}), 404

        return jsonify({
            "id": sub.id,
            "user_id": sub.user_id,
            "plan": sub.plan_name,
            "status": sub.status,
            "renewal_date": sub.renewal_date.isoformat(),
            "created_at": sub.created_at.isoformat()
        })

    except Exception:
        logger.exception(f"Error fetching subscription with ID: {subscription_id}")
        return jsonify({"error": "Internal server error"}), 500