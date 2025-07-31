# app/services/subscription/subscription_service.py

from typing import TypedDict, Optional, Any, List
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models.subscription import Subscription  # Placeholder — must define Subscription model
from app.models.user import User  # Assumes User has subscription relationship/field
import logging

logger = logging.getLogger(__name__)

# ✅ Return structuring for strong typing
class SubscriptionResult(TypedDict, total=False):
    success: bool
    message: str
    plan_id: int
    plan: dict[str, Any]
    plans: list[dict[str, Any]]

class SubscriptionService:
    """
    Manages subscription plans and user-subscription assignments.
    """

    def __init__(self, model=Subscription, user_model=User, session=db.session):
        self.Subscription = model
        self.User = user_model
        self.db = session

    def create_subscription_plan(
        self, name: str, price: float, duration_days: int,
        tier: str = "basic", features: str = ""
    ) -> SubscriptionResult:
        """
        Create a new subscription plan with optional tier and feature metadata.
        """
        try:
            if self.Subscription.query.filter_by(name=name).first():
                return {"success": False, "message": "Subscription plan already exists."}

            plan = self.Subscription(
                name=name,
                price=price,
                duration_days=duration_days,
                tier=tier,
                features=features
            )
            self.db.add(plan)
            self.db.commit()

            logger.info(f"Created subscription plan: {name}")
            return {"success": True, "message": "Subscription plan created successfully.", "plan_id": plan.id}

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Plan creation failed: {str(e)}")
            return {"success": False, "message": f"Database error: {str(e)}"}

    def get_subscription_plan(self, plan_id: int) -> SubscriptionResult:
        """
        Retrieve plan by ID.
        """
        plan = self.Subscription.query.get(plan_id)
        if not plan:
            return {"success": False, "message": "Subscription plan not found."}

        return {
            "success": True,
            "message": "Plan retrieved successfully.",
            "plan": {
                "id": plan.id,
                "name": plan.name,
                "price": plan.price,
                "duration_days": plan.duration_days,
                "tier": getattr(plan, "tier", "basic"),
                "features": getattr(plan, "features", "")
            }
        }

    def list_all_plans(self) -> SubscriptionResult:
        """
        Return all available plans. Warn if none found.
        """
        try:
            plans = self.Subscription.query.all()
            if not plans:
                return {"success": True, "plans": [], "message": "No subscription plans found."}

            plan_list = [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "duration_days": p.duration_days,
                    "tier": getattr(p, "tier", "basic"),
                    "features": getattr(p, "features", "")
                }
                for p in plans
            ]
            return {"success": True, "plans": plan_list}

        except SQLAlchemyError as e:
            logger.error(f"Plan listing failed: {str(e)}")
            return {"success": False, "message": f"Listing failed: {str(e)}"}

    def assign_subscription_to_user(self, user_id: int, plan_id: int) -> SubscriptionResult:
        """
        Assign subscription plan to user.
        """
        user = self.User.query.get(user_id)
        plan = self.Subscription.query.get(plan_id)

        if not user:
            return {"success": False, "message": "User not found."}
        if not plan:
            return {"success": False, "message": "Subscription plan not found."}
        if not hasattr(user, "subscription_id"):
            return {"success": False, "message": "User model lacks subscription field."}

        try:
            user.subscription_id = plan.id
            self.db.commit()

            logger.info(f"Assigned plan '{plan.name}' to user: {user.email}")
            return {"success": True, "message": "Subscription assigned successfully."}

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Subscription assignment failed: {str(e)}")
            return {"success": False, "message": f"Assignment failed: {str(e)}"}

    def cancel_user_subscription(self, user_id: int) -> SubscriptionResult:
        """
        Remove user's subscription safely.
        """
        user = self.User.query.get(user_id)
        if not user:
            return {"success": False, "message": "User not found."}
        if not hasattr(user, "subscription_id"):
            return {"success": False, "message": "User model lacks subscription field."}

        try:
            user.subscription_id = None
            self.db.commit()

            logger.warning(f"Subscription cancelled for user: {user.email}")
            return {"success": True, "message": "Subscription cancelled."}
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Subscription cancellation failed: {str(e)}")
            return {"success": False, "message": f"Cancellation failed: {str(e)}"}

    def get_user_subscriptions(self, user_id: int) -> List[Subscription]:
        """
        Return all subscription instances for a given user.
        """
        return self.Subscription.query.filter_by(user_id=user_id).all()

    def get_subscription_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """
        Return a single subscription instance by its ID.
        """
        return self.Subscription.query.get(subscription_id)


# Module-level wrappers for route imports

def get_user_subscriptions(user_id: int) -> List[Subscription]:
    """
    Wrapper to call the SubscriptionService get_user_subscriptions method.
    """
    return SubscriptionService().get_user_subscriptions(user_id)


def get_subscription_by_id(subscription_id: int) -> Optional[Subscription]:
    """
    Wrapper to call the SubscriptionService get_subscription_by_id method.
    """
    return SubscriptionService().get_subscription_by_id(subscription_id)