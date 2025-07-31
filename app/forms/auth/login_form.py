"""
app/forms/auth/login_form.py

Defines the login form for ISREALAI authentication with
field normalization, email length enforcement, and basic
password complexity (digits + special characters) enforced
via validate_password().
"""

import re
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

logger = logging.getLogger(__name__)


class LoginForm(FlaskForm):
    """
    Form for users to log in.

    Fields:
        email         – User's email address (required, valid format,
                        length between 5 and 254 characters).
        password      – User's password (required, length 8–128 characters,
                        must include at least one digit and one special character).
        remember_me   – Stay logged in across sessions.
        submit        – Submission button.

    Password complexity is enforced via the validate_password() hook.
    """

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
            Length(min=5, max=254, message="Email must be 5–254 characters long."),
        ],
        render_kw={"placeholder": "you@example.com", "autofocus": True},
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, max=128, message="Password must be 8–128 characters long."),
        ],
        render_kw={"placeholder": "Your password"},
    )

    remember_me = BooleanField("Remember Me", default=False)
    submit = SubmitField("Log In")

    def _normalize_fields(self):
        """
        Pre-validation hook to normalize inputs:
        - Strips whitespace
        - Lowercases the email
        """
        try:
            if self.email.data:
                self.email.data = self.email.data.strip().lower()
            if self.password.data:
                self.password.data = self.password.data.strip()
        except Exception as e:
            logger.warning(f"Normalization issue in LoginForm: {e}")

    def validate_password(self, field):
        """
        Enforce basic password complexity:
        - At least one digit
        - At least one special character
        """
        pwd = field.data or ""
        if not re.search(r"\d", pwd) or not re.search(r"[^\w\s]", pwd):
            raise ValidationError(
                "Password must include at least one digit and one special character."
            )

    def validate(self, extra_validators=None):
        """
        Override default validator:
        - Run normalization first
        - Delegate to WTForms' validate(), passing any extra_validators
        """
        self._normalize_fields()
        return super().validate(extra_validators)