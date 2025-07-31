"""
app/config/production.py

Production configuration for ISREALAI Technologies.
Optimized for security, performance, and monitoring in production.
"""

import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request, redirect
from .base import BaseConfig

class ProductionConfig(BaseConfig):
    """
    Production environment configuration.
    Inherits from BaseConfig and applies production best practices.
    """

    ENV: str = "production"
    DEBUG: bool = False
    TESTING: bool = False

    # Secure cookies and URL scheme
    SESSION_COOKIE_SECURE: bool = True
    REMEMBER_COOKIE_SECURE: bool = True
    PREFERRED_URL_SCHEME: str = "https"

    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

    # Admins to notify on critical errors
    ADMINS: list[str] = (
        os.environ.get("ADMINS", "").split(",")
        if os.environ.get("ADMINS")
        else []
    )

    # Optional error tracking
    SENTRY_DSN: str = os.environ.get("SENTRY_DSN", "")

    # SQLAlchemy tuning
    SQLALCHEMY_POOL_SIZE: int = int(os.environ.get("SQLALCHEMY_POOL_SIZE", 10))
    SQLALCHEMY_POOL_TIMEOUT: int = int(os.environ.get("SQLALCHEMY_POOL_TIMEOUT", 30))

    @staticmethod
    def init_app(app: Flask) -> None:
        """
        Initialize the Flask app with production settings:
        - Apply base config logic
        - Configure email error reporting
        - Setup rotating file logging
        - Enforce HTTPS
        - Initialize Sentry (optional)
        """

        # Apply base config warnings and hooks
        BaseConfig.init_app(app)

        # Set dynamic log level
        app.logger.setLevel(app.config["LOG_LEVEL"].upper())

        # Log startup path
        app.logger.info(f"App root: {app.root_path}")
        app.logger.info("ISREALAI starting in Production mode")

        # Secure HTTPS enforcement (safe from debug/test mode or reverse proxy conflict)
        @app.before_request
        def enforce_https_in_production():
            if not request.is_secure and not app.debug and not app.testing:
                return redirect(request.url.replace("http://", "https://"))

        # ---------------------------------------------------------------------
        # Email error notifications
        # ---------------------------------------------------------------------
        mail_server = app.config.get("MAIL_SERVER")
        mail_port = app.config.get("MAIL_PORT")
        mail_sender = app.config.get("MAIL_DEFAULT_SENDER")
        admins = app.config.get("ADMINS", [])

        if mail_server and admins:
            auth = None
            if app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"):
                auth = (
                    app.config["MAIL_USERNAME"],
                    app.config["MAIL_PASSWORD"],
                )
            secure = () if app.config.get("MAIL_USE_TLS") else None

            smtp_handler = SMTPHandler(
                mailhost=(mail_server, mail_port),
                fromaddr=mail_sender,
                toaddrs=admins,
                subject="ISREALAI Application Error",
                credentials=auth,
                secure=secure,
            )
            smtp_handler.setLevel(logging.ERROR)
            app.logger.addHandler(smtp_handler)

        # ---------------------------------------------------------------------
        # Rotating file logs
        # ---------------------------------------------------------------------
        logs_path = os.path.join(app.root_path, "..", "logs")
        try:
            os.makedirs(logs_path, exist_ok=True)
            file_handler = RotatingFileHandler(
                os.path.join(logs_path, "isrealai.log"),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=10,
            )
            file_formatter = logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
        except Exception as e:
            app.logger.error(f"Failed to set up file logging: {e}")

        # ---------------------------------------------------------------------
        # Sentry integration (if enabled)
        # ---------------------------------------------------------------------
        sentry_dsn = app.config.get("SENTRY_DSN")
        if sentry_dsn:
            try:
                import sentry_sdk
                from sentry_sdk.integrations.flask import FlaskIntegration

                sentry_sdk.init(
                    dsn=sentry_dsn,
                    integrations=[FlaskIntegration()],
                    environment="production",
                )
                app.logger.info("✅ Sentry SDK initialized")
            except ImportError:
                app.logger.warning("sentry-sdk not installed; Sentry skipped")