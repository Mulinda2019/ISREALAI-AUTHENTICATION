# app/services/user/user_service.py

from typing import Any, TypedDict
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User  # Placeholder import — must define a SQLAlchemy User class
from app.extensions import db
from app.services.auth.token_service import TokenService  # Abstracted token generator & verifier
from sqlalchemy.exc import SQLAlchemyError
import logging

# TypedDict for consistent return typing
class ServiceResult(TypedDict):
    success: bool
    message: str
    token: str | None
    user_id: int | None

# Initialize logger
logger = logging.getLogger(__name__)

# Whitelisted fields for safe profile updates
ALLOWED_UPDATE_FIELDS = {"email", "username", "bio", "profile_picture"}

class UserService:
    """
    Handles user-related logic: registration, authentication, updates, and deletion.
    """

    def __init__(self, model=User, session=db.session):
        self.User = model
        self.db = session

    def create_user(self, email: str, username: str, password: str) -> ServiceResult:
        """
        Create a new user if email and username are unique.
        Returns success flag, message, token, and user_id.
        """
        try:
            if self.User.query.filter_by(email=email).first():
                return {"success": False, "message": "Email already registered.", "token": None, "user_id": None}
            if self.User.query.filter_by(username=username).first():
                return {"success": False, "message": "Username already taken.", "token": None, "user_id": None}

            hashed_password = generate_password_hash(password)
            new_user = self.User(email=email, username=username, password_hash=hashed_password)
            self.db.add(new_user)
            self.db.commit()

            verification_token = TokenService.generate_user_verification_token(email)
            logger.info(f"User created: {email}")

            return {
                "success": True,
                "message": "User created successfully.",
                "token": verification_token,
                "user_id": new_user.id
            }

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"User creation failed: {str(e)}")
            return {"success": False, "message": f"Database error: {str(e)}", "token": None, "user_id": None}

    def authenticate_user(self, email: str, password: str) -> ServiceResult:
        """
        Authenticate user credentials.
        Returns success, token, and user_id.
        """
        user = self.User.query.filter_by(email=email).first()
        if not user:
            return {"success": False, "message": "User not found.", "token": None, "user_id": None}

        if not check_password_hash(user.password_hash, password):
            return {"success": False, "message": "Incorrect password.", "token": None, "user_id": None}

        auth_token = TokenService.generate_user_auth_token(email)
        logger.info(f"User authenticated: {email}")

        return {
            "success": True,
            "message": "Authentication successful.",
            "token": auth_token,
            "user_id": user.id
        }

    def update_user_profile(self, user_id: int, **updates) -> dict[str, Any]:
        """
        Safely update allowed fields on user profile.
        """
        user = self.User.query.get(user_id)
        if not user:
            return {"success": False, "message": "User not found."}

        for field, value in updates.items():
            if field in ALLOWED_UPDATE_FIELDS:
                setattr(user, field, value)

        try:
            self.db.commit()
            logger.info(f"User updated: {user.email}")
            return {"success": True, "message": "Profile updated successfully."}
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Profile update failed: {str(e)}")
            return {"success": False, "message": f"Update failed: {str(e)}"}

    def delete_user(self, user_id: int, soft_delete: bool = True) -> dict[str, Any]:
        """
        Delete or deactivate user. Set soft_delete=False for permanent deletion.
        """
        user = self.User.query.get(user_id)
        if not user:
            return {"success": False, "message": "User not found."}

        try:
            if soft_delete and hasattr(user, "is_active"):
                user.is_active = False
                self.db.commit()
                logger.warning(f"User soft-deleted: {user.email}")
                return {"success": True, "message": "Account deactivated."}
            else:
                self.db.delete(user)
                self.db.commit()
                logger.warning(f"User permanently deleted: {user.email}")
                return {"success": True, "message": "Account deleted permanently."}
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Deletion failed: {str(e)}")
            return {"success": False, "message": f"Deletion failed: {str(e)}"}

    def get_user_profile(self, user_id: int) -> User | None:
        """
        Retrieve a user instance by ID.
        """
        return self.User.query.get(user_id)


def update_user_password(token: str, new_password: str) -> ServiceResult:
    """
    Reset user password using a valid reset token.
    Verifies token, updates hash, and commits.
    """
    try:
        email = TokenService.verify_password_reset_token(token)
        if not email:
            return {"success": False, "message": "Invalid or expired token.", "token": None, "user_id": None}

        user = User.query.filter_by(email=email).first()
        if not user:
            return {"success": False, "message": "User not found.", "token": None, "user_id": None}

        hashed_password = generate_password_hash(new_password)
        user.password_hash = hashed_password
        db.session.commit()
        logger.info(f"Password updated for user: {email}")
        return {"success": True, "message": "Password updated successfully.", "token": None, "user_id": user.id}

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Password update failed for token: {token}, error: {e}")
        return {"success": False, "message": f"Password update failed: {e}", "token": None, "user_id": None}


def activate_user_account(user: User) -> bool:
    """
    Activate a user's account by setting is_active to True.
    Returns True on success, False on failure.
    """
    try:
        user.is_active = True
        db.session.commit()
        logger.info(f"User activated: {user.email}")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Account activation failed for {user.email}: {e}")
        return False


# Module-level wrappers for route imports
def update_user_profile(user_id: int, **updates) -> dict[str, Any]:
    """
    Wrapper to call the UserService update_user_profile method.
    """
    return UserService().update_user_profile(user_id, **updates)


def delete_user(user_id: int, soft_delete: bool = True) -> dict[str, Any]:
    """
    Wrapper to call the UserService delete_user method.
    """
    return UserService().delete_user(user_id, soft_delete)


def get_user_profile(user_id: int) -> User | None:
    """
    Wrapper to call the UserService get_user_profile method.
    """
    return UserService().get_user_profile(user_id)