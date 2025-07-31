# app/routes/auth/login.py

"""
Login route for ISREALAI Technologies.
Handles user authentication, session management, and post-login redirection.
Includes rate-limiting, IP/User-Agent logging, and geolocation stub.
"""

from flask import request, redirect, url_for, flash, current_app
from flask_login import login_user, current_user
from app.routes.auth import bp
from app.forms.auth.login_form import LoginForm
from app.services.auth.auth_service import AuthService  # Updated import
from app.utils.decorators import safe_render          # ← fixed import
from app.extensions import limiter  # ✅ Use global limiter instance

@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # ✅ Rate limit attached correctly
def login():
    """
    Render login form and handle user authentication.
    Redirects to dashboard or intended page on success.
    Logs failed and successful attempts with IP, User-Agent, and (optional) geolocation.
    """
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("dashboard.home"))

    form = LoginForm()
    next_page = request.args.get("next")
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    if request.method == "POST" and form.validate_on_submit():
        try:
            user = AuthService.authenticate(
                email=form.email.data,
                password=form.password.data
            )
        except ValueError:
            user = None

        if user:
            login_user(user, remember=form.remember_me.data)
            flash("Login successful.", "success")

            try:
                current_app.logger.info(f"User {user.email} logged in from IP {ip} ({user_agent})")
                # Geolocation stub (optional)
                # location = get_geolocation(ip)
                # current_app.logger.info(f"Login location: {location}")
            except Exception:
                pass

            redirect_url = next_page or current_app.config.get("LOGIN_REDIRECT_URL", url_for("dashboard.home"))
            return redirect(redirect_url)
        else:
            flash("Invalid email or password.", "danger")
            try:
                current_app.logger.warning(f"Failed login for {form.email.data} from IP {ip} ({user_agent})")
            except Exception:
                pass

    return safe_render("auth/login.html", form=form)