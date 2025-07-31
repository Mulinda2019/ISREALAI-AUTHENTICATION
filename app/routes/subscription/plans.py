# app/routes/subscription/plans.py

from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
import logging

from app.utils.decorators import safe_render

subscription_bp = Blueprint("subscription", __name__, url_prefix="/subscription")

# Initialize logger for this module
logger = logging.getLogger(__name__)


@subscription_bp.route("/plans", methods=["GET"])
@login_required
def view_plans():
    """
    Display available subscription plans for the authenticated user.

    Returns:
        HTML response with plan details, or placeholder if template is missing.
    """
    try:
        # Context to pass to template, extend later with DB-based plan info
        context = {
            "user": current_user,
            "title": "Subscription Plans — ISREAL.AI",
            # "plans": get_available_plans()  ← future DB/service integration point
        }

        # Attempt to render subscription plans page
        return safe_render("subscription/plans.html", context)

    except TemplateNotFound:
        logger.warning("Subscription plans template not found. Fallback to placeholder.")
        return safe_render("placeholders/under_construction.html")

    except Exception as e:
        logger.exception("Error occurred while rendering subscription plans.")
        return safe_render("placeholders/under_construction.html")