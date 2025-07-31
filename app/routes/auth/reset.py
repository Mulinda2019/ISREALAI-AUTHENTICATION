# app/routes/auth/reset.py

"""
Password reset routes for ISREALAI Technologies.
Handles reset request and token-based password update.
Includes IP/User-Agent logging, token validation, and CSRF-safe forms.
"""

from flask import request, redirect, url_for, flash, current_app
from flask_login import current_user
from app.routes.auth import bp
from app.forms.auth.reset_password_form import ResetRequestForm, ResetPasswordForm

# Alias AuthService.initiate_password_reset to match send_reset_email usage
from app.services.auth.auth_service import AuthService
send_reset_email = AuthService.initiate_password_reset

# Use TokenService.confirm_reset_token in place of nonexistent verify_reset_token
from app.services.auth.token_service import TokenService
verify_reset_token = TokenService.confirm_reset_token

from app.services.user.user_service import update_user_password
from app.routes import safe_render

@bp.route("/reset-password", methods=["GET", "POST"])
def reset_request():
    """
    Initiates password reset by sending a secure email link.
    """
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("dashboard.home"))

    form = ResetRequestForm()
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    if request.method == "POST" and form.validate_on_submit():
        try:
            send_reset_email(form.email.data)
            flash("Password reset instructions have been sent to your email.", "info")
            current_app.logger.info(
                f"Password reset requested for {form.email.data} from IP {ip} ({user_agent})"
            )
            return redirect(url_for("auth.login"))
        except Exception as e:
            flash("Failed to send reset email. Please try again.", "danger")
            current_app.logger.error(
                f"Reset email error for {form.email.data} from IP {ip} ({user_agent}): {e}"
            )

    return safe_render("auth/reset_request.html", form=form)

@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """
    Handles password update via secure token.
    Logs invalid token attempts and successful resets.
    """
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("dashboard.home"))

    form = ResetPasswordForm()
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    try:
        user = verify_reset_token(token)
        if not user:
            current_app.logger.warning(
                f"Invalid password reset token attempt from IP {ip} ({user_agent})"
            )
            flash("Invalid or expired reset link.", "danger")
            return safe_render("auth/reset_password.html", form=form)

        if request.method == "POST" and form.validate_on_submit():
            update_user_password(user, form.password.data)
            flash("Your password has been updated. You can now log in.", "success")
            current_app.logger.info(
                f"Password reset for {user.email} from IP {ip} ({user_agent})"
            )
            return redirect(url_for("auth.login"))

    except Exception as e:
        flash("Password reset failed. Please try again or request a new link.", "danger")
        current_app.logger.error(
            f"Password reset error from IP {ip} ({user_agent}): {e}"
        )

    return safe_render("auth/reset_password.html", form=form)