"""
app/services/auth/auth_service.py

Service layer for user authentication, registration, email verification,
and password reset workflows.
"""

from datetime import datetime
import logging

from flask import current_app
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.auth.token_service import TokenService
from app.services.auth.email_service import EmailService

logger = logging.getLogger(__name__)

class AuthService:
    """
    Encapsulates business logic around user signup, login verification,
    email confirmation, and password reset workflows.
    """

    @staticmethod
    def _log_event(user_id: int | None, event_type: str, message: str) -> None:
        """
        Helper to append an AuditLog entry and commit in one go.
        """
        db.session.add(AuditLog(
            user_id=user_id,
            event_type=event_type,
            message=message
        ))
        db.session.commit()

    @staticmethod
    def register_user(
        email: str,
        password: str,
        username: str = None,
        full_name: str = None
    ) -> User:
        """
        Create a new user, hash their password (unless pre-hashed),
        persist to DB, queue verification email, and record audit.

        Raises:
            ValueError: on duplicate email or DB failure.
        """
        if User.query.filter_by(email=email).first():
            raise ValueError("Email is already registered.")

        user = User(
            email=email,
            username=username or email.split("@")[0],
            full_name=full_name
        )

        # Support pre-hashed passwords (e.g., fixtures starting with $2b$)
        if password.startswith("$2"):
            user.password_hash = password
        else:
            user.set_password(password)

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            current_app.logger.error("Registration DB error: %s", err)
            raise ValueError("Could not register user at this time.")

        token = TokenService.generate_confirmation_token(user.id)
        try:
            EmailService.send_verification_email(user, token)
        except Exception as err:
            current_app.logger.error("Verification email failed for user %s: %s", user.id, err)

        # Audit registration
        AuthService._log_event(
            user.id, "profile_update", "User registered; verification email sent"
        )

        return user

    @staticmethod
    def confirm_email(token: str) -> bool:
        """
        Validate a confirmation token and mark the user's email as verified.
        """
        user_id = TokenService.confirm_token(token)
        if not user_id:
            return False

        user = User.query.get(user_id)
        if not user:
            return False

        if user.is_email_verified:
            return True

        user.is_email_verified = True
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            current_app.logger.error("Email confirmation DB error for user %s: %s", user.id, err)
            return False

        AuthService._log_event(
            user.id, "email_change", "User email verified"
        )
        return True

    @staticmethod
    def authenticate(
        email: str,
        password: str,
        record_login: bool = True
    ) -> User:
        """
        Verify user credentials for login.

        Args:
            record_login: if False, skip timestamp update and audit.

        Returns:
            Authenticated User.

        Raises:
            ValueError: invalid credentials or inactive account.
        """
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise ValueError("Invalid email or password.")

        if not user.is_active or user.is_deleted:
            raise ValueError("Account inactive or deleted.")

        if record_login:
            user.mark_login()
            try:
                db.session.commit()
            except Exception as err:
                db.session.rollback()
                current_app.logger.warning(
                    "Could not update last_login for user %s: %s", user.id, err
                )
            AuthService._log_event(user.id, "login", "User logged in")

        return user

    @staticmethod
    def initiate_password_reset(email: str) -> bool:
        """
        Generate a password reset token and email it.

        Returns False if user not found or inactive.
        """
        user = User.query.filter_by(email=email).first()
        if not user or not user.is_active or user.is_deleted:
            return False

        token = TokenService.generate_reset_token(user.id)
        try:
            EmailService.send_password_reset_email(user, token)
            AuthService._log_event(user.id, "password_reset", "Password reset requested")
            return True
        except Exception as err:
            current_app.logger.error("Password reset email failed for user %s: %s", user.id, err)
            return False

    @staticmethod
    def reset_password(token: str, new_password: str) -> bool:
        """
        Validate reset token, optionally check strength, and set new password.
        """
        user_id = TokenService.confirm_reset_token(token)
        if not user_id:
            return False

        user = User.query.get(user_id)
        if not user or not user.is_active or user.is_deleted:
            return False

        # Minimal strength check (customize as needed)
        if len(new_password) < 8:
            current_app.logger.warning("Password reset aborted—weak password for user %s", user.id)
            return False

        user.set_password(new_password)
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            current_app.logger.error("Reset password DB error for user %s: %s", user.id, err)
            return False

        AuthService._log_event(user.id, "password_reset", "Password successfully reset")
        return True