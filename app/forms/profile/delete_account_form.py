"""
app/forms/profile/delete_account_form.py

Defines the form for users to delete their account in ISREALAI.
Includes confirmation text, password re-authentication via AuthService,
CSRF protection provided by FlaskForm, and normalization.
"""

import logging

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    Length,
    ValidationError,
)

logger = logging.getLogger(__name__)

# Attempt to import AuthService for password re-authentication; warn if unavailable
try:
    from app.services.auth.auth_service import AuthService
except ImportError:
    AuthService = None
    logger.warning("AuthService not available; skipping password re-authentication.")


class DeleteAccountForm(FlaskForm):
    """
    Form for users to delete their account.

    Fields:
        confirm_text – Required; user must type "DELETE" exactly to confirm irreversible account deletion.
        password     – Required; current password for re-authentication.
        submit       – Submission button.

    CSRF protection is provided automatically by FlaskForm.
    """

    confirm_text = StringField(
        "Type DELETE to confirm account deletion",
        validators=[
            DataRequired(message="You must type DELETE to confirm."),
            Length(min=6, max=6, message="Confirmation text must be exactly 6 characters."),
        ],
        render_kw={"placeholder": "DELETE", "autofocus": True},
    )

    password = PasswordField(
        "Current Password",
        validators=[DataRequired(message="Your current password is required.")],
        render_kw={"placeholder": "Your password"},
    )

    submit = SubmitField("Delete Account")

    def _normalize_fields(self):
        """
        Pre-validation hook to normalize inputs:
        - Strips whitespace
        - Uppercases confirm_text for comparison
        - Strips whitespace from password
        Logs an info if normalization fails, with truncated raw values.
        """
        raw_confirm = self.confirm_text.data or ""
        raw_password = self.password.data or ""
        try:
            if self.confirm_text.data:
                self.confirm_text.data = self.confirm_text.data.strip().upper()
            if self.password.data:
                self.password.data = self.password.data.strip()
        except Exception as e:
            truncated_confirm = (
                raw_confirm[:20] + "..." if len(raw_confirm) > 20 else raw_confirm
            )
            truncated_password = (
                raw_password[:20] + "..." if len(raw_password) > 20 else raw_password
            )
            logger.info(
                "Normalization issue in DeleteAccountForm: %s; raw_confirm=%r, raw_password=%r",
                e,
                truncated_confirm,
                truncated_password,
            )

    def validate_confirm_text(self, field):
        """
        Ensure the user typed 'DELETE' exactly.
        """
        if field.data != "DELETE":
            raise ValidationError("Confirmation text must be DELETE.")

    def validate_password(self, field):
        """
        Re-authenticate the user by verifying the provided password.
        """
        pwd = field.data or ""
        # Password already normalized in _normalize_fields()

        if AuthService:
            if not AuthService.verify_password(current_user.id, pwd):
                raise ValidationError("Incorrect password. Please try again.")
        else:
            logger.info(
                "AuthService not available during password validation; skipping check."
            )

    def validate(self, extra_validators=None):
        """
        Override validate:
        - Normalize fields first
        - Delegate to WTForms validate(), passing any extra_validators
        """
        self._normalize_fields()
        return super().validate(extra_validators)
