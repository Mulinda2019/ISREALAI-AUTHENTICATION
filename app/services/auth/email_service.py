"""
app/services/auth/email_service.py

Service layer for sending transactional emails such as
email verification and password reset notifications.
"""

import logging
from flask import current_app, url_for, render_template
from flask_mail import Message
from jinja2 import TemplateNotFound
from app.extensions import mail

logger = logging.getLogger(__name__)

class EmailService:
    """
    Handles composition and delivery of all authentication-related emails.
    """

    @staticmethod
    def _build_message(subject: str, recipients: list[str], 
                       text_template: str, html_template: str,
                       **context) -> Message:
        """
        Helper to render templates and assemble the Flask-Mail Message.
        """
        try:
            text_body = render_template(text_template, **context)
            html_body = render_template(html_template, **context)
        except TemplateNotFound as e:
            logger.error("Missing email template: %s", e)
            return None  # caller should skip send

        msg = Message(
            subject,
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=recipients
        )
        msg.body = text_body
        msg.html = html_body
        return msg

    @staticmethod
    def send_verification_email(user, token: str) -> None:
        """
        Send an email containing a link for the user to confirm their address.
        """
        subject = "Confirm Your Email Address"
        verify_url = url_for("auth.confirm_email", token=token, _external=True)
        recipients = [user.email]
        logger.info("Sending verification email to %s", user.email)

        msg = EmailService._build_message(
            subject,
            recipients,
            text_template="email/verify_email.txt",
            html_template="email/verify_email.html",
            user=user,
            verify_url=verify_url
        )
        if not msg:
            return

        mail.send(msg)

    @staticmethod
    def send_password_reset_email(user, token: str) -> None:
        """
        Send an email containing a link for the user to reset their password.
        """
        subject = "Password Reset Request"
        reset_url = url_for("auth.reset_password", token=token, _external=True)
        recipients = [user.email]
        logger.info("Sending password reset email to %s", user.email)

        msg = EmailService._build_message(
            subject,
            recipients,
            text_template="email/reset_password.txt",
            html_template="email/reset_password.html",
            user=user,
            reset_url=reset_url
        )
        if not msg:
            return

        mail.send(msg)