# app/utils/tokens.py

"""
Token utility functions for ISREALAI Technologies.

Generates context-aware, time-sensitive tokens using itsdangerous.
"""

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def get_serializer() -> URLSafeTimedSerializer:
    """
    Create a URL-safe timed serializer using app's secret key and salt.
    """
    secret_key = current_app.config.get("SECRET_KEY")
    salt = current_app.config.get("SECURITY_SALT", "isrealai-token-salt")
    return URLSafeTimedSerializer(secret_key, salt=salt)

def get_expiration() -> int:
    """
    Get token expiration (in seconds) from config, with fallback default.
    """
    return int(current_app.config.get("TOKEN_EXPIRATION_SECONDS", 3600))  # default: 1 hour

def generate_token(data: str, context: str = "default") -> str:
    """
    Generate a signed token with context tag and embedded data.
    """
    serializer = get_serializer()
    token = serializer.dumps({"ctx": context, "val": data})
    logger.debug(f"Generated token for context='{context}' and data='{data}'")
    return token

def verify_token(token: str, context: str = "default", max_age: int | None = None) -> str | None:
    """
    Verify token with matching context. Returns original data if valid, else None.
    """
    serializer = get_serializer()
    expiration = max_age if max_age is not None else get_expiration()

    try:
        payload = serializer.loads(token, max_age=expiration)
        if payload.get("ctx") == context:
            logger.debug(f"Verified token for context='{context}' successfully.")
            return payload.get("val")

        logger.warning(f"Token context mismatch: expected '{context}', got '{payload.get('ctx')}'")
        return None

    except SignatureExpired:
        logger.warning(f"Expired token for context='{context}'")
        return None
    except BadSignature:
        logger.warning(f"Invalid token signature for context='{context}'")
        return None