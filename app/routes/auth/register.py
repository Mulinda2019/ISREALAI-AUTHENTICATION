# app/routes/auth/register.py

"""
Registration route for ISREALAI Technologies.
Handles new user sign-up, validation, and email verification trigger.
Includes duplicate email checks, granular error handling, and client metadata logging.
"""

from flask import request, redirect, url_for, flash, current_app
from flask_login import current_user
from app.routes.auth import bp
from app.forms.auth.register_form import RegisterForm

from app.services.auth.auth_service import AuthService
from app.models.user import User
from app.services.auth.email_service import EmailService  # Updated import
from app.routes import safe_render

# Aliases matching previous usage
register_user = AuthService.register_user
user_exists = lambda email: User.query.filter_by(email=email).first() is not None


@bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Render registration form and handle new user creation.
    Sends verification email on success.
    Logs client metadata and handles duplicate email gracefully.
    """
    if current_user.is_authenticated:
        flash("You are already registered and logged in.", "info")
        return redirect(url_for("dashboard.home"))

    form = RegisterForm()
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    if request.method == "POST" and form.validate_on_submit():
        try:
            if user_exists(form.email.data):
                flash(
                    "Email already registered. Please login or reset your password.",
                    "warning"
                )
                current_app.logger.warning(
                    f"Duplicate registration attempt: {form.email.data} "
                    f"from IP {ip} ({user_agent})"
                )
                return redirect(url_for("auth.login"))

            user = register_user(
                email=form.email.data,
                password=form.password.data,
                full_name=form.full_name.data
            )

            # Use EmailService.send_verification_email instead of missing function
            EmailService.send_verification_email(user, AuthService.generate_confirmation_token(user.id))
            flash(
                "Registration successful! Please check your email to verify your account.",
                "success"
            )
            current_app.logger.info(
                f"New user registered: {user.email} from IP {ip} ({user_agent})"
            )
            return redirect(url_for("auth.login"))

        except Exception as e:
            flash("An unexpected error occurred. Please try again.", "danger")
            current_app.logger.error(
                f"Unexpected error during registration for {form.email.data}: {e}"
            )

    return safe_render("auth/signup.html", form=form)