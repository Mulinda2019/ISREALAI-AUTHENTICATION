"""
app/extensions.py

Initialize and configure Flask extensions for ISREALAI Technologies.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Rate limiting support
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Core database object
db = SQLAlchemy()

# Handle database migrations
migrate = Migrate()

# User session management
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Email support
mail = Mail()

# Password hashing utility
bcrypt = Bcrypt()

# JSON Web Token support for API authentication
jwt = JWTManager()

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


# Defer importing User until function call to avoid circular imports
@login_manager.user_loader
def load_user(user_id: str):
    """
    Given a user_id (from session), return the corresponding User object.
    """
    try:
        # Local import prevents circular dependency at module load time
        from app.models.user import User
        return User.query.get(int(user_id))
    except Exception:
        return None


def init_extensions(app):
    """
    Initialize all Flask extensions with the application instance.

    This function should be called from app/__init__.py in create_app().
    """
    try:
        # Database & migrations
        db.init_app(app)
        migrate.init_app(app, db)

        # Login management
        login_manager.init_app(app)

        # Email
        mail.init_app(app)

        # Password hashing
        bcrypt.init_app(app)

        # JWT support
        jwt.init_app(app)

        # Rate limiter
        limiter.init_app(app)

        # TODO: Initialize Flask-CORS, CSRFProtect, etc. as needed

    except Exception as e:
        if app.debug:
            app.logger.exception("Extension initialization failed:")
            raise
        else:
            app.logger.error(f"Extension initialization failed: {e}")