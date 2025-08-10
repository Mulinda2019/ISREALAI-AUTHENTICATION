"""Expose form classes for easy importing in tests and views."""

from .auth.login_form import LoginForm
from .auth.register_form import RegisterForm, RegistrationForm
from .auth.reset_password_form import ResetRequestForm as ResetPasswordForm

__all__ = [
    "LoginForm",
    "RegisterForm",
    "RegistrationForm",
    "ResetPasswordForm",
]

