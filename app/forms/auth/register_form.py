"""
app/forms/auth/register_form.py

Defines the registration form for new users in ISREALAI,
with field normalization, case-insensitive usernames,
boolean TOS enforcement, and password complexity via a
shared helper.
"""

import re
import logging
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Regexp,
    InputRequired,
    ValidationError,
)

logger = logging.getLogger(__name__)


class RegisterForm(FlaskForm):
    """
    Form for users to register a new account.

    Fields:
        username          – Required, 3–30 chars; letters, numbers, underscores;
                             normalized to lowercase.
        email             – Required, valid format, 5–254 chars.
        password          – Required, 8–128 chars; must include digit & special char.
        confirm_password  – Must match password.
        accept_tos        – Must be checked to agree to Terms of Service.
        submit            – Submission button.

    Password complexity is enforced via validate_password().
    """

    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=30, message="Username must be 3–30 characters long."),
            Regexp(
                r"^[A-Za-z0-9_]+$",
                message="Username may only contain letters, numbers, and underscores.",
            ),
        ],
        render_kw={"placeholder": "choose_a_username", "autofocus": True},
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
            Length(min=5, max=254, message="Email must be 5–254 characters long."),
        ],
        render_kw={"placeholder": "you@example.com"},
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, max=128, message="Password must be 8–128 characters long."),
        ],
        render_kw={"placeholder": "Create a password"},
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "Repeat your password"},
    )

    accept_tos = BooleanField(
        "I agree to the Terms of Service",
        validators=[InputRequired(message="You must accept the Terms of Service.")],
    )

    submit = SubmitField("Sign Up")

    def _normalize_fields(self):
        """
        Pre-validation hook to normalize inputs:
        - Strips whitespace
        - Lowercases username and email for consistency
        """
        try:
            if self.username.data:
                self.username.data = self.username.data.strip().lower()
            if self.email.data:
                self.email.data = self.email.data.strip().lower()
        except Exception as e:
            logger.warning(f"Normalization issue in RegisterForm: {e}")

    @staticmethod
    def _is_password_complex(pwd: str) -> bool:
        """
        Checks basic password complexity:
        - At least one digit
        - At least one non-alphanumeric (special) character
        """
        return bool(re.search(r"\d", pwd) and re.search(r"[^\w\s]", pwd))

    def validate_username(self, field):
        """
        Ensure username is not purely numeric to avoid confusion with IDs.
        """
        if field.data.isdigit():
            raise ValidationError("Username cannot consist of only numbers.")

    def validate_password(self, field):
        """
        Enforce password complexity using shared helper.
        """
        pwd = field.data or ""
        if not self._is_password_complex(pwd):
            raise ValidationError(
                "Password must include at least one digit and one special character."
            )

    def validate_accept_tos(self, field):
        """
        Confirm that the user has agreed to the Terms of Service.
        """
        if not field.data:
            raise ValidationError("You must accept the Terms of Service to register.")

    def validate(self, extra_validators=None):
        """
        Override default validate:
        - Normalize fields first
        - Delegate to WTForms validate(), passing any extra_validators
        """
        self._normalize_fields()
        return super().validate(extra_validators)