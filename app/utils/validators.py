# app/utils/validators.py

"""
Validation utilities for ISREALAI Technologies.

Supports email format checking and password strength validation with
optional feedback for improving user error messages.
"""

import re
from typing import Tuple

EMAIL_REGEX = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$")
SPECIAL_CHAR_REGEX = re.compile(r"[!@#$%^&*(),.?\":{}|<>]")

def validate_email(email: str) -> bool:
    """
    Validates email format using regex.

    Args:
        email: Email string to validate.

    Returns:
        True if format looks valid, False otherwise.
    """
    return bool(EMAIL_REGEX.match(email))

def validate_password(password: str) -> bool:
    """
    Validates password strength.
    Must contain:
        - 8+ characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit

    Args:
        password: Password string.

    Returns:
        True if password meets strength criteria.
    """
    return bool(PASSWORD_REGEX.match(password))

def validate_password_detailed(password: str) -> Tuple[bool, list[str]]:
    """
    Returns validation result and a list of reasons why a password might fail.

    Args:
        password: Password string.

    Returns:
        Tuple: (True/False, [list of validation error messages])
    """
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        errors.append("Must include at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Must include at least one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Must include at least one digit.")
    # Optional: Uncomment if you want special characters enforced
    # if not SPECIAL_CHAR_REGEX.search(password):
    #     errors.append("Must include at least one special character.")

    return (len(errors) == 0, errors)