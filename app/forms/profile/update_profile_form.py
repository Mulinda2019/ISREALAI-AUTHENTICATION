"""
app/forms/profile/update_profile_form.py

Defines the form for users to update their profile in ISREALAI.
Includes normalization, length checks, and optional uniqueness
validation via UserService for username and email.

CSRF protection is provided automatically by FlaskForm.
"""

import logging

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Length,
    Regexp,
    Email,
    ValidationError,
)

logger = logging.getLogger(__name__)

# Attempt to import UserService for uniqueness checks; warn if unavailable
try:
    from app.services.user.user_service import UserService
except ImportError:
    UserService = None
    logger.warning("UserService not available; skipping uniqueness checks.")


class UpdateProfileForm(FlaskForm):
    """
    Form for updating user profile fields.

    Parameters:
        original_username (str|None): Current username to skip self-check.
        original_email    (str|None): Current email to skip self-check.

    Fields:
        username    – Required; 3–30 chars, letters/numbers/underscores;
                       normalized to lowercase. Must not collide with others.
        email       – Required; valid format, 5–254 chars, normalized to lowercase.
        submit      – Submission button.

    CSRF protection is provided automatically by FlaskForm.
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
        render_kw={"placeholder": "your_username", "autofocus": True},
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

    submit = SubmitField("Update Profile")

    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        """
        Store original values to allow skipping uniqueness check when unchanged.
        """
        super().__init__(*args, **kwargs)
        self.original_username = original_username.lower() if original_username else None
        self.original_email = original_email.lower() if original_email else None

    def _normalize_fields(self):
        """
        Pre-validation hook to normalize inputs:
        - Strips whitespace
        - Lowercases username and email
        Logs a warning with truncated raw field values if normalization fails.
        """
        raw_username = self.username.data or ""
        raw_email = self.email.data or ""
        try:
            if self.username.data:
                self.username.data = self.username.data.strip().lower()
            if self.email.data:
                self.email.data = self.email.data.strip().lower()
        except Exception as e:
            truncated_uname = (
                raw_username[:20] + "..." if len(raw_username) > 20 else raw_username
            )
            truncated_email = (
                raw_email[:20] + "..." if len(raw_email) > 20 else raw_email
            )
            logger.warning(
                "Normalization issue in UpdateProfileForm: %s; raw username=%r, raw email=%r",
                e,
                truncated_uname,
                truncated_email,
            )

    def validate_username(self, field):
        """
        Ensure username is not purely numeric and is unique if changed.
        """
        uname = field.data or ""
        if uname.isdigit():
            raise ValidationError("Username cannot consist of only numbers.")

        if (
            UserService
            and self.original_username
            and uname != self.original_username
            and UserService.is_username_taken(uname)
        ):
            raise ValidationError("Username is already in use.")

    def validate_email(self, field):
        """
        Ensure email is unique if changed.
        """
        email = field.data or ""

        if (
            UserService
            and self.original_email
            and email != self.original_email
            and UserService.is_email_taken(email)
        ):
            raise ValidationError("Email address is already registered.")

    def validate(self, extra_validators=None):
        """
        Override validate:
        - Normalize fields first
        - Delegate to WTForms validate(), passing any extra_validators
        """
        self._normalize_fields()
        return super().validate(extra_validators)