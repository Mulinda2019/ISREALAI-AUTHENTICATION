# app/routes/auth/verify.py

"""
Email verification route for ISREALAI Technologies.
Handles token-based account activation via secure link.
Includes IP/User-Agent logging, redundant verification checks, and graceful fallback.
"""

from flask import request, redirect, url_for, flash, current_app
from flask_login import current_user
from app.routes.auth import bp
from app.services.auth.token_service import TokenService  # Updated import
from app.models.user import User  # Needed to load user by ID
from app.services.user.user_service import activate_user_account
from app.routes import safe_render

@bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """
    Verifies a user's email using a secure token.
    Activates account and redirects to login with feedback.
    Logs IP/User-Agent and handles redundant verification gracefully.
    """
    if current_user.is_authenticated:
        flash("Your account is already verified.", "info")
        return redirect(url_for("dashboard.home"))

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    try:
        # Validate token and extract user ID
        user_id = TokenService.confirm_token(token)
        if not user_id:
            flash("Invalid or expired verification link.", "danger")
            return safe_render("auth/verify_email.html")

        user = User.query.get(user_id)
        if not user:
            flash("Invalid or expired verification link.", "danger")
            return safe_render("auth/verify_email.html")

        if user.is_active:
            flash("Your account is already verified.", "info")
            return redirect(url_for("auth.login"))

        # Activate the user account
        activate_user_account(user)
        flash("Email verified successfully! You can now log in.", "success")
        current_app.logger.info(
            f"Email verified for {user.email} from IP {ip} ({user_agent})"
        )
        return redirect(url_for("auth.login"))

    except Exception as e:
        flash("Verification failed. Please try again or request a new link.", "danger")
        current_app.logger.error(
            f"Email verification error from IP {ip} ({user_agent}): {e}"
        )
        return safe_render("auth/verify_email.html")