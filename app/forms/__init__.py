"""
app/forms/__init__.py

Initialize ISREALAI form package by dynamically importing and
registering all form classes. Keeps public API clean, avoids
repetition, and surfaces import issues during development.
"""

import os
import warnings
import importlib
import logging

logger = logging.getLogger(__name__)

# Public API for this package
__all__ = []

# Internal registry to avoid name collisions
_FORM_CLASSES = {}


def _register_forms(form_definitions):
    """
    Dynamically import and register form classes.

    Parameters:
        form_definitions (list of tuple): Each tuple is
            (module_path: str, class_name: str)

    Behavior:
        - Imports module via import_module(module_path, package=__name__),
          ensuring relative resolution from app.forms.
        - Retrieves the class.
        - Checks for name collisions in globals() and _FORM_CLASSES.
        - Registers class in globals() and _FORM_CLASSES.
        - Appends the class's __name__ to __all__.
        - On failure: logs exception, emits a cleaner ImportWarning
          in development, or re-raises in production.
    """
    env = os.getenv("FLASK_ENV", "production").lower()
    for module_path, class_name in form_definitions:
        try:
            module = importlib.import_module(module_path, package=__name__)
            cls = getattr(module, class_name)

            # Collision check
            if class_name in globals() or class_name in _FORM_CLASSES:
                warning_msg = f"Name collision detected for form class '{class_name}'"
                logger.warning(warning_msg)
                warnings.warn(warning_msg, ImportWarning)

            # Register in namespace and registry
            globals()[class_name] = cls
            _FORM_CLASSES[class_name] = cls
            __all__.append(class_name)

        except (ImportError, AttributeError) as e:
            msg = f"Failed to import '{class_name}' from '{module_path}': {e}"
            logger.exception(msg)
            if env == "development":
                warnings.warn(msg, ImportWarning)
            else:
                raise


# ─── Auth Forms ───────────────────────────────────────────────────────────────
_auth_forms = [
    (".auth.login_form", "LoginForm"),
    (".auth.register_form", "RegisterForm"),
    (".auth.reset_password_form", "ResetPasswordForm"),
]
_register_forms(_auth_forms)


# ─── Profile Forms ────────────────────────────────────────────────────────────
_profile_forms = [
    (".profile.update_profile_form", "UpdateProfileForm"),
    (".profile.delete_account_form", "DeleteAccountForm"),
]
_register_forms(_profile_forms)


# ─── Subscription Forms ───────────────────────────────────────────────────────
_subscription_forms = [
    (".subscription.subscription_form", "SubscriptionForm"),
]
_register_forms(_subscription_forms)


# Sort __all__ for deterministic API (alphabetical order across groups)
__all__.sort()

# Note: Add a unit test in tests/test_forms.py to assert:
#       set(__all__) == set(_FORM_CLASSES.keys())