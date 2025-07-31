"""
app/config/base.py

Base configuration class for ISREALAI Technologies.
Defines default settings and pulls sensitive values from environment variables.
"""

import os
from pathlib import Path
from flask import Flask

# Determine the project root (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class BaseConfig:
    """
    Base configuration with sensible defaults.
    Other environments (development, production) should inherit from this.
    """

    # SECURITY
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")

    # FLASK ENV FLAGS
    DEBUG: bool = False
    TESTING: bool = False

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI: str = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{BASE_DIR / 'instance' / 'database.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Flask-Mail (for email confirmations, password resets, notifications)
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS: bool = os.environ.get("MAIL_USE_TLS", "True").lower() in ["true", "1", "yes"]
    MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER: str = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        f"no-reply@{os.environ.get('MAIL_DOMAIN', 'isreal.ai')}"
    )

    # JWT Settings
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))

    # Pagination
    ITEMS_PER_PAGE: int = int(os.environ.get("ITEMS_PER_PAGE", 20))

    # JSON behavior
    JSON_SORT_KEYS: bool = False  # preserve key order in jsonify()

    # Optional host/CORS guards
    # ALLOWED_HOSTS: list[str] = os.environ.get("ALLOWED_HOSTS", "*").split(",")
    # CORS_ORIGINS: list[str] = os.environ.get("CORS_ORIGINS", "").split(",")

    # Debug toolbar toggle
    DEBUG_TB_ENABLED: bool = False

    @staticmethod
    def init_app(app: Flask) -> None:
        """
        Hook for initializing app with BaseConfig.
        Can be used to set up logging, error tracking, etc.
        """
        # Warn if secrets are left as defaults
        if app.config["SECRET_KEY"] == "change-me-in-production":
            app.logger.warning(
                "SECRET_KEY is using the default value; override in your environment!"
            )
        if app.config["JWT_SECRET_KEY"] == "change-me-in-production":
            app.logger.warning(
                "JWT_SECRET_KEY is using the default value; override in your environment!"
            )
        # Place to initialize logging handlers, Sentry, metrics, etc.