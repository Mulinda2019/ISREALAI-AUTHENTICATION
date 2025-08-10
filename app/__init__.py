import os
import logging

from flask import Flask, render_template, redirect, url_for
from jinja2 import TemplateNotFound
from flask_login import current_user

# Core configs
from app.config.base import BaseConfig
from app.config.development import DevelopmentConfig
from app.config.production import ProductionConfig

# Extensions
from app.extensions import db, migrate, login_manager, mail

# CLI
from app.cli.commands import register_cli_commands

# Blueprints
from app.routes.auth import auth_bp
from app.routes.profile.account import profile_bp
from app.routes.dashboard.home import dashboard_bp
from app.routes.subscription.plans import subscription_bp
from app.routes.admin import admin_bp
from app.routes.main.home import main_bp
from app.routes.api.v1.user_api import user_api_bp
from app.routes.api.v1.subscription_api import subscription_api_bp

# Determine project root (one level above app/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def create_app(config_name: str | None = None):
    """
    Factory to create and configure the Flask application.
    """
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=os.path.join(project_root, "frontend"),
        static_folder=os.path.join(project_root, "frontend"),
        static_url_path="/static",
    )

    # Extend Jinja search path so "auth/login.html" finds
    # frontend/modules/auth/login.html, and placeholders work:
    from jinja2 import ChoiceLoader, FileSystemLoader

    tpl_root     = os.path.join(project_root, "frontend")
    modules_root = os.path.join(tpl_root, "modules")

    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(tpl_root),
        FileSystemLoader(modules_root),
    ])

    # ---------- Load configuration ----------
    config = (config_name or os.getenv("FLASK_ENV", "production")).lower()
    if config == "development":
        app.config.from_object(DevelopmentConfig)
    elif config == "testing":
        from app.config.testing import TestingConfig
        app.config.from_object(TestingConfig)
    elif config == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(BaseConfig)

    # Override with instance config if present
    try:
        app.config.from_pyfile("config.py", silent=False)
    except FileNotFoundError:
        logging.warning("No instance/config.py found; using defaults")
    except Exception as e:
        logging.error(f"Error loading instance config: {e}")
        raise

    # Validate SECRET_KEY
    if not app.config.get("SECRET_KEY"):
        fallback = os.getenv("SECRET_KEY")
        if fallback:
            app.config["SECRET_KEY"] = fallback
            logging.warning("Loaded SECRET_KEY from environment variable")
        else:
            logging.warning("SECRET_KEY not set! This is insecure in production.")

    # ---------- Logging startup info ----------
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    logging.info(f"Starting app in '{config}' mode")
    logging.info(f"DEBUG={app.config.get('DEBUG')}  DATABASE_URI={app.config.get('SQLALCHEMY_DATABASE_URI')}")

    # ---------- Initialize extensions ----------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # ---------- Security settings ----------
    app.config.setdefault("SESSION_COOKIE_SECURE", True)
    app.config.setdefault("REMEMBER_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)

    # ---------- Register blueprints ----------
    for bp in (
        main_bp, auth_bp, profile_bp, dashboard_bp,
        subscription_bp, admin_bp,
        user_api_bp, subscription_api_bp
    ):
        app.register_blueprint(bp)

    # ---------- Root route handler to avoid 404 at "/" ----------
    @app.route("/", methods=["GET"])
    def index():
        """
        Redirect root URL to dashboard if logged in, otherwise to login.
        """
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.home"))
        return redirect(url_for("auth.login"))

    # ---------- Register CLI commands ----------
    register_cli_commands(app)

    # ---------- Error handlers ----------
    @app.errorhandler(404)
    def not_found(err):
        db.session.rollback()
        return _safe_render("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(err):
        db.session.rollback()
        return _safe_render("errors/500.html"), 500

    return app


def _safe_render(template_name: str, **context):
    """
    Render template or fallback to a placeholder if missing.
    """
    try:
        return render_template(template_name, **context)
    except TemplateNotFound:
        logging.warning(f"Template '{template_name}' missing—using placeholder.")
        return render_template("placeholders/under_construction.html", **context)