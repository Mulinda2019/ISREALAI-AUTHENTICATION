"""
app/models/subscription.py

Defines the Subscription model for ISREALAI Technologies.
Tracks user plans, status, and payment metadata.
"""

from datetime import datetime, timedelta
from sqlalchemy import Enum
from app.extensions import db

class Subscription(db.Model):
    """
    Represents a user's subscription to the ISREALAI platform.
    Includes plan details, lifecycle dates, provider info, and helper logic.
    """

    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)

    # Relationship to user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Plan details
    plan_name = db.Column(db.String(50), nullable=False)
    plan_tier = db.Column(db.String(20), default="basic")  # basic, pro, enterprise
    price_cents = db.Column(db.Integer, nullable=False)    # store in cents

    # Status & lifecycle
    status = db.Column(
        Enum("active", "canceled", "expired", name="subscription_status"),
        default="active",
        nullable=False
    )
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    renewed_at = db.Column(db.DateTime, nullable=True)
    canceled_at = db.Column(db.DateTime, nullable=True)

    # Payment metadata
    payment_provider = db.Column(db.String(50))    # e.g., Stripe, PayPal
    external_reference = db.Column(db.String(100)) # transaction ID or customer ID

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_active(self, grace_days: int = 3) -> bool:
        """
        Check if subscription is active, including optional grace period.
        """
        if self.status != "active":
            return False
        if not self.end_date:
            return True
        return self.end_date + timedelta(days=grace_days) >= datetime.utcnow()

    def cancel(self) -> None:
        """
        Cancel subscription and record timestamp.
        """
        self.status = "canceled"
        self.canceled_at = datetime.utcnow()

    def renew(self, duration_days: int = 30) -> None:
        """
        Extend end date by `duration_days`, and mark renewal.
        """
        now = datetime.utcnow()
        self.renewed_at = now
        self.status = "active"
        if not self.end_date or self.end_date < now:
            self.end_date = now + timedelta(days=duration_days)
        else:
            self.end_date += timedelta(days=duration_days)

    def days_remaining(self) -> int:
        """
        Returns days left until subscription expires.
        """
        if not self.end_date:
            return 0
        return max((self.end_date - datetime.utcnow()).days, 0)

    def __repr__(self):
        return f"<Subscription {self.plan_name} for user {self.user_id}>"