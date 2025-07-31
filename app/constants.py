# app/constants.py

"""
Global constants for ISREALAI Technologies.

This file centralizes magic values, environment fallbacks,
security defaults, role enums, pricing metadata, and render formatting.
All modules should reference these constants for consistency.
"""

import os
from enum import Enum
from datetime import timedelta
from typing import TypedDict, List, Union


# ------------------------------------------------------------------------------
# 🔐 Security & Tokens
# ------------------------------------------------------------------------------

# Token expirations
EMAIL_VERIFICATION_TOKEN_EXPIRY: timedelta = timedelta(hours=24)
PASSWORD_RESET_TOKEN_EXPIRY: timedelta = timedelta(hours=2)
API_ACCESS_TOKEN_EXPIRY: timedelta = timedelta(minutes=15)
API_REFRESH_TOKEN_EXPIRY: timedelta = timedelta(days=7)

# Secret key default — should be overridden by config or .env in production
DEFAULT_SECRET_KEY: str = os.getenv(
    "SECRET_KEY",
    "change-me-in-production-please!"
)

# Warn devs if default key is still used in production
if DEFAULT_SECRET_KEY.startswith("change-me") and os.getenv("FLASK_ENV") == "production":
    import logging
    logging.warning("🚨 Using insecure default SECRET_KEY in production. Please set a proper one!")


# ------------------------------------------------------------------------------
# 👤 Roles
# ------------------------------------------------------------------------------

class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUBSCRIBER = "subscriber"

ALL_ROLES = [role.value for role in RoleEnum]


# ------------------------------------------------------------------------------
# 💸 Subscription Plans
# ------------------------------------------------------------------------------

class SubscriptionPlanMeta(TypedDict):
    display_name: str
    price_usd: Union[int, float]
    monthly_quota: Union[int, float]
    features: List[str]

SUBSCRIPTION_PLANS: dict[str, SubscriptionPlanMeta] = {
    "free": {
        "display_name": "Free",
        "price_usd": 0,
        "monthly_quota": 100,
        "features": ["Basic support", "Community access"]
    },
    "pro": {
        "display_name": "Pro",
        "price_usd": 29.99,
        "monthly_quota": 1000,
        "features": ["Priority support", "Custom integrations"]
    },
    "enterprise": {
        "display_name": "Enterprise",
        "price_usd": 99.99,
        "monthly_quota": float("inf"),
        "features": ["Dedicated account manager", "Unlimited usage"]
    }
}


# ------------------------------------------------------------------------------
# 📦 Pagination & Limits
# ------------------------------------------------------------------------------

ITEMS_PER_PAGE: int = 20
MAX_ITEMS_PER_PAGE: int = 100
MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB uploads


# ------------------------------------------------------------------------------
# 📧 Email Defaults
# ------------------------------------------------------------------------------

EMAIL_SUBJECTS: dict[str, str] = {
    "verify_email": "Please verify your email address",
    "reset_password": "Reset your password",
    "welcome": "Welcome to ISREALAI Technologies!",
    "admin_notification": "New user registration: {username}"
}

DEFAULT_MAIL_SENDER: str = os.getenv(
    "MAIL_DEFAULT_SENDER",
    "no-reply@isrealai.tech"
)


# ------------------------------------------------------------------------------
# 🌐 API & Routing
# ------------------------------------------------------------------------------

API_VERSION: str = "v1"
API_PREFIX: str = f"/api/{API_VERSION}"
HEALTHCHECK_ENDPOINT: str = "/health"


# ------------------------------------------------------------------------------
# 🧾 Logging
# ------------------------------------------------------------------------------

LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT: str = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"


# ------------------------------------------------------------------------------
# 🕒 Formatting Helpers
# ------------------------------------------------------------------------------

DISPLAY_DATETIME_FORMAT: str = "%b %d, %Y %I:%M %p"