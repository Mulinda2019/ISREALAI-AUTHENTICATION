# app/routes/profile/account.py

"""
Profile management routes for ISREALAI Technologies.
Handles user profile updates and account deletion with confirmation and audit logging.
"""

from flask import Blueprint, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, logout_user
from app.forms.profile.update_profile_form import UpdateProfileForm
from app.forms.profile.delete_account_form import DeleteAccountForm
from app.services.user.user_service import update_user_profile, delete_user
from app.routes import safe_render
from app.extensions import limiter

# Define and export the blueprint directly in this module
profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per minute")
def edit_profile():
    """
    Allows authenticated users to update their profile information.
    """
    form = UpdateProfileForm(obj=current_user)

    if request.method == "POST" and form.validate_on_submit():
        try:
            update_user_profile(current_user.id,
                                full_name=form.full_name.data,
                                bio=form.bio.data)
            flash("Profile updated successfully.", "success")
            current_app.logger.info(f"Profile updated for user: {current_user.email}")
            return redirect(url_for("profile.edit_profile"))
        except Exception as e:
            flash("Failed to update profile. Please try again.", "danger")
            current_app.logger.error(f"Profile update error for {current_user.email}: {e}")

    return safe_render("profile/edit.html", form=form)

@profile_bp.route("/delete", methods=["GET", "POST"])
@login_required
@limiter.limit("5 per minute")
def delete_account():
    """
    Allows authenticated users to delete their account with confirmation.
    """
    form = DeleteAccountForm()

    if request.method == "POST" and form.validate_on_submit():
        if not form.confirm.data:
            flash("Please confirm account deletion by checking the box.", "warning")
            return safe_render("profile/delete.html", form=form)

        try:
            email = current_user.email
            delete_user(current_user.id)
            logout_user()
            flash("Your account has been deleted.", "info")
            current_app.logger.warning(f"Account deleted: {email}")
            return redirect(url_for("auth.login"))
        except Exception as e:
            flash("Account deletion failed. Please try again.", "danger")
            current_app.logger.error(f"Account deletion error for {current_user.email}: {e}")

    return safe_render("profile/delete.html", form=form)