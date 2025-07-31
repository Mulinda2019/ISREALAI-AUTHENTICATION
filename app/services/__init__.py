"""
app/services/__init__.py

Collect and expose service layer classes for ISREALAI Technologies.
Provides a centralized registry for application services.
"""

from app.services.auth.auth_service import AuthService
from app.services.auth.token_service import TokenService
from app.services.auth.email_service import EmailService
from app.services.user.user_service import UserService
from app.services.subscription.subscription_service import SubscriptionService
from app.services.admin.admin_service import AdminService

__all__ = [
    "AuthService",
    "TokenService",
    "EmailService",
    "UserService",
    "SubscriptionService",
    "AdminService",
    "register_services",
]

def register_services() -> dict:
    """
    Return a mapping of service name to service class for CLI tools,
    shell contexts, or dependency injection frameworks.
    """
    return {
        "auth": AuthService,
        "token": TokenService,
        "email": EmailService,
        "user": UserService,
        "subscription": SubscriptionService,
        "admin": AdminService,
    }