"""
app/config/development.py

Development configuration for ISREALAI Technologies.
Enables debug features, verbose logging, and development‐only settings.
"""

import os
from flask import Flask
from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """
    Development environment configuration.
    Inherits from BaseConfig and turns on debugging, SQL echoing,
    and other developer conveniences.
    """

    # General Flask settings
    ENV: str = "development"
    DEBUG: bool = True
    TESTING: bool = True

    # SQLAlchemy
    SQLALCHEMY_ECHO: bool = True  # log all SQL statements for debugging

    # Flask-DebugToolbar toggle (requires flask_debugtoolbar extension)
    DEBUG_TB_ENABLED: bool = True

    # Flask-Mail
    MAIL_DEBUG: bool = True            # emit email info to console
    MAIL_SUPPRESS_SEND: bool = False   # actually send if SMTP is configured

    @staticmethod
    def init_app(app: Flask) -> None:
        """
        Initialize the app with development‐specific settings.
        Calls the BaseConfig initializer, then applies dev overrides.
        """

        # First run BaseConfig logic (warnings, logging, etc.)
        BaseConfig.init_app(app)

        # Development banner
        app.logger.debug("⚙️  ISREALAI running in Development mode")
        
        # Optional: catch mis-configured mail server
        if not app.config.get("MAIL_SERVER"):
            app.logger.warning("MAIL_SERVER not set; emails will fail.")

        # You can attach development‐only extensions here:
        # from flask_debugtoolbar import DebugToolbarExtension
        # toolbar = DebugToolbarExtension()
        # toolbar.init_app(app)