"""
app/forms/auth/reset_password_form.py

Defines the forms for users to request a password reset and to set a new password
in ISREALAI. Includes CSRF protection via FlaskForm, field normalization,
length checks, basic password complexity, and email validation.
"""

import re
import logging

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import (
    DataRequired,
    Length,
    EqualTo,
    ValidationError,
    Email
)

logger = logging.getLogger(__name__)


class ResetRequestForm(FlaskForm):
    """
    Form for requesting a password reset link.
    
    Fields:
        email   – User's email address (required, must be valid).
        submit  – Submission button.
    """
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address.")
        ],
        render_kw={"placeholder": "Enter your email", "autofocus": True},
    )
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    """
    Form for setting a new password after a reset request.

    Fields:
        password          – New password (required, 8–128 chars;
                             must include at least one digit and one special character).
        confirm_password  – Must match `password`.
        submit            – Submission button.

    CSRF protection is provided automatically by FlaskForm.
    Password complexity is enforced via validate_password().
    """
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(message="New password is required."),
            Length(min=8, max=128, message="Password must be 8–128 characters long."),
        ],
        render_kw={"placeholder": "Enter your new password", "autofocus": True},
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(message="Please confirm your new password."),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "Repeat your new password"},
    )

    submit = SubmitField("Reset Password")

    def _normalize_fields(self):
        """
        Strip whitespace from password fields to avoid accidental spaces.
        Logs a warning with truncated values if normalization fails.
        """
        try:
            if self.password.data:
                self.password.data = self.password.data.strip()
            if self.confirm_password.data:
                self.confirm_password.data = self.confirm_password.data.strip()
        except Exception as e:
            raw_pw = self.password.data or ""
            raw_confirm = self.confirm_password.data or ""
            logger.warning(
                "Normalization issue in ResetPasswordForm: %s; "
                "password=%r, confirm_password=%r",
                e,
                raw_pw[:20] + "...",
                raw_confirm[:20] + "...",
            )

    @staticmethod
    def _is_password_complex(value: str) -> bool:
        """
        Validate that `value` has at least one digit and one special character.
        """
        return bool(re.search(r"\d", value) and re.search(r"[^\w\s]", value))

    def validate_password(self, field):
        """
        Enforce password complexity rules.

        Raises ValidationError if missing digit or special character.
        """
        pwd = field.data or ""
        if not self._is_password_complex(pwd):
            raise ValidationError(
                "Password must include at least one digit and one special character."
            )

    def validate(self, extra_validators=None):
        """
        Override validate:
        - Normalize fields first
        - Delegate to WTForms validate(), passing any extra_validators
          (extra_validators: dict[str, list[Validator]] | None)
        """
        self._normalize_fields()
        return super().validate(extra_validators)