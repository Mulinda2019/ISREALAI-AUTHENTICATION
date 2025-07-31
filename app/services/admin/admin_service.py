# app/services/admin/admin_service.py

from typing import TypedDict, Optional, Any
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models.user import User
from app.models.audit_log import AuditLog
import logging

logger = logging.getLogger(__name__)

class AdminResult(TypedDict, total=False):
    success: bool
    message: str
    user_list: list[dict[str, Any]]
    logs: list[dict[str, Any]]
    user_id: int

class AdminService:
    """
    Handles administrative functions like user management and log inspection.
    """

    def __init__(self, user_model=User, log_model=AuditLog, session=db.session):
        self.User = user_model
        self.AuditLog = log_model
        self.db = session

    def list_all_users(self, active_only: bool = False, search_email: Optional[str] = None, search_username: Optional[str] = None) -> AdminResult:
        """
        Retrieve user list, optionally filtered by activity status or search query.
        """
        try:
            query = self.User.query
            if active_only:
                query = query.filter_by(is_active=True)
            if search_email:
                query = query.filter(self.User.email.ilike(f"%{search_email}%"))
            if search_username:
                query = query.filter(self.User.username.ilike(f"%{search_username}%"))

            users = query.all()
            user_list = [
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "is_active": getattr(user, "is_active", True),
                    "role": getattr(user, "role", "user")
                }
                for user in users
            ]
            return {"success": True, "user_list": user_list}

        except SQLAlchemyError as e:
            logger.error(f"Failed to list users: {str(e)}")
            return {"success": False, "message": f"Error listing users: {str(e)}"}

    def deactivate_user(self, user_id: int) -> AdminResult:
        """
        Disable a user account.
        """
        user = self.User.query.get(user_id)
        if not user:
            return {"success": False, "message": "User not found."}
        if not hasattr(user, "is_active"):
            return {"success": False, "message": "User model lacks 'is_active' field."}

        try:
            user.is_active = False
            self.db.commit()
            self._log_admin_action("deactivate_user", user_id)
            logger.warning(f"Admin deactivated user: {user.email}")
            return {"success": True, "message": "User deactivated.", "user_id": user.id}
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Deactivation failed: {str(e)}")
            return {"success": False, "message": f"Deactivation failed: {str(e)}"}

    def delete_user(self, user_id: int) -> AdminResult:
        """
        Permanently delete a user.
        """
        user = self.User.query.get(user_id)
        if not user:
            return {"success": False, "message": "User not found."}

        try:
            self.db.delete(user)
            self.db.commit()
            self._log_admin_action("delete_user", user_id)
            logger.warning(f"Admin deleted user: {user.email}")
            return {"success": True, "message": "User deleted.", "user_id": user.id}
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"User deletion failed: {str(e)}")
            return {"success": False, "message": f"Deletion failed: {str(e)}"}

    def view_audit_logs(self, limit: int = 100, user_id: Optional[int] = None, action: Optional[str] = None) -> AdminResult:
        """
        Retrieve audit logs, optionally filtered by user or action.
        """
        try:
            query = self.AuditLog.query.order_by(self.AuditLog.timestamp.desc())
            if user_id:
                query = query.filter_by(user_id=user_id)
            if action:
                query = query.filter_by(action=action)

            logs = query.limit(limit).all()
            log_data = [
                {
                    "id": log.id,
                    "action": log.action,
                    "user_id": log.user_id,
                    "timestamp": log.timestamp.isoformat(),
                    "metadata": log.metadata
                }
                for log in logs
            ]
            return {"success": True, "logs": log_data}
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch logs: {str(e)}")
            return {"success": False, "message": f"Log retrieval failed: {str(e)}"}

    def _log_admin_action(self, action: str, user_id: int, metadata: Optional[dict[str, Any]] = None) -> None:
        """
        Internal helper to record audit log events.
        """
        try:
            log_entry = self.AuditLog(action=action, user_id=user_id, metadata=metadata or {})
            self.db.add(log_entry)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Audit log failed: {str(e)}")

# ⚠️ Future Feature Suggestion:
# @require_admin(role="superuser") — Add role-based access guards when you integrate permissions