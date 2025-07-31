"""
app/forms/subscription/subscription_form.py

WTForm for managing user subscription selection or update.

Fields:
- plan_name: string ID of a valid subscription plan (loaded dynamically).
- user_id: integer primary key of the user; hidden in form, validated for numeric integrity.
"""

import logging

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError

from app.services.subscription.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

class SubscriptionForm(FlaskForm):
    """
    Allows users to select or change their subscription plan.
    """

    plan_name = SelectField(
        "Choose Your Plan",
        choices=[],
        description="Select the subscription tier you wish to purchase.",
        validators=[DataRequired(message="Please select a valid plan.")]
    )
    user_id = IntegerField(
        "User ID",
        description="Hidden field containing the user's numeric ID.",
        validators=[
            DataRequired(message="User ID is required."),
            NumberRange(min=1, message="Invalid user ID.")
        ],
        render_kw={"type": "hidden"}
    )
    submit = SubmitField(
        "Subscribe",
        description="Click to confirm and activate your selected plan."
    )

    def __init__(self, *args, **kwargs):
        """
        Populate plan choices dynamically on form initialization.
        """
        super().__init__(*args, **kwargs)
        try:
            plans = SubscriptionService.get_all_plans()
            # Expect each plan to have `id` and `display_name` attributes
            self.plan_name.choices = [
                (str(plan.id), plan.display_name) for plan in plans
            ]
        except Exception as e:
            self.plan_name.choices = []
            logger.warning("Failed to load subscription plans: %s", e)

    def validate_plan_name(self, field):
        """
        Ensure the submitted plan_name matches one of the loaded choices.
        Protects against tampering with form data.
        """
        valid_keys = {choice[0] for choice in self.plan_name.choices}
        if field.data not in valid_keys:
            raise ValidationError("Invalid subscription plan selected.")

    def get_selected_plan_id(self) -> str:
        """
        Returns the selected plan identifier as a string.
        """
        return self.plan_name.data