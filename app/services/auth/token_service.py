"""
app/services/auth/token_service.py

TokenService for generating and validating timed tokens for
email confirmations and password resets using itsdangerous.
"""

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app

class TokenService:
    """
    Creates and verifies secure, URL-safe tokens for
    email confirmation and password reset workflows.
    """

    SALT_CONFIRM = "email-confirmation"
    SALT_RESET = "password-reset"

    @staticmethod
    def _get_serializer(salt: str) -> URLSafeTimedSerializer:
        """
        Returns a configured URLSafeTimedSerializer with given salt.
        """
        return URLSafeTimedSerializer(
            current_app.config["SECRET_KEY"],
            salt=salt
        )

    @staticmethod
    def generate_confirmation_token(user_id: int) -> str:
        """
        Generate a timed token for email confirmation.
        """
        serializer = TokenService._get_serializer(TokenService.SALT_CONFIRM)
        return serializer.dumps({"id": user_id})

    @staticmethod
    def confirm_token(token: str) -> int | None:
        """
        Validate an email confirmation token.

        Returns the user_id if valid and not expired, else None.
        """
        serializer = TokenService._get_serializer(TokenService.SALT_CONFIRM)
        max_age = current_app.config.get("CONFIRMATION_TOKEN_EXPIRES", 3600 * 24)
        try:
            data = serializer.loads(token, max_age=max_age)
            return data.get("id")
        except SignatureExpired:
            current_app.logger.warning("Confirmation token expired: %s...", token[:10])
        except BadSignature:
            current_app.logger.warning("Invalid confirmation token: %s...", token[:10])
        return None

    @staticmethod
    def generate_reset_token(user_id: int) -> str:
        """
        Generate a timed token for password reset.
        """
        serializer = TokenService._get_serializer(TokenService.SALT_RESET)
        return serializer.dumps({"id": user_id})

    @staticmethod
    def confirm_reset_token(token: str) -> int | None:
        """
        Validate a password reset token.

        Returns the user_id if valid and not expired, else None.
        """
        serializer = TokenService._get_serializer(TokenService.SALT_RESET)
        max_age = current_app.config.get("RESET_TOKEN_EXPIRES", 3600)
        try:
            data = serializer.loads(token, max_age=max_age)
            return data.get("id")
        except SignatureExpired:
            current_app.logger.warning("Password reset token expired: %s...", token[:10])
        except BadSignature:
            current_app.logger.warning("Invalid password reset token: %s...", token[:10])
        return None