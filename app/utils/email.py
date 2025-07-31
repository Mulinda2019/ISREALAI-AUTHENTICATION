# app/utils/email.py

"""
Email utilities for ISREALAI Technologies.

Handles templated email rendering and secure delivery with
HTML/text fallback, input validation, retry logic, and logging.
"""

from flask import render_template
from flask_mail import Message
from app.extensions import mail
from app.utils.validators import validate_email
import logging
import time

logger = logging.getLogger(__name__)

class EmailSendError(Exception):
    """Raised when email fails to send after all retries."""
    pass

DEFAULT_FALLBACK_HTML = "placeholders/under_construction.html"
DEFAULT_FALLBACK_TEXT = "This message is currently unavailable."

def format_email_content(
    subject: str,
    recipient: str,
    template_base: str,
    context: dict,
    fallback_html: str = DEFAULT_FALLBACK_HTML,
    fallback_text: str = DEFAULT_FALLBACK_TEXT
) -> Message:
    """
    Renders HTML and plain-text email templates using given context.

    Args:
        subject: Email subject line.
        recipient: Target email address.
        template_base: Name of template (e.g., 'verify_email').
        context: Data passed to Jinja templates.
        fallback_html: Optional fallback HTML file path.
        fallback_text: Optional fallback plain text.

    Returns:
        Flask-Mail Message object.
    
    Raises:
        ValueError if email is invalid.
    """
    if not validate_email(recipient):
        logger.warning(f"Invalid email address: {recipient}")
        raise ValueError("Recipient email address is invalid.")

    try:
        html_body = render_template(f"email/{template_base}.html", **context)
        text_body = render_template(f"email/{template_base}.txt", **context)
    except Exception as e:
        logger.error(f"Template rendering failed for '{template_base}': {e}")
        html_body = render_template(fallback_html)
        text_body = fallback_text

    return Message(
        subject=subject,
        recipients=[recipient],
        html=html_body,
        body=text_body
    )

def send_email(msg: Message, retries: int = 3, delay: float = 2.5) -> None:
    """
    Sends an email with retry logic. Raises EmailSendError on failure.

    Args:
        msg: Formatted email message.
        retries: Number of retry attempts before failure.
        delay: Seconds to wait between attempts.

    Raises:
        EmailSendError if all attempts fail.
    """
    for attempt in range(1, retries + 1):
        try:
            with mail.connect() as conn:
                conn.send(msg)
            logger.info(f"Email sent to: {msg.recipients[0]}")
            return
        except Exception as e:
            logger.warning(f"Email send attempt {attempt} failed for {msg.recipients[0]}: {e}")
            time.sleep(delay)

    logger.error(f"Email delivery failed after {retries} retries: {msg.recipients[0]}")
    raise EmailSendError(f"Could not send email to {msg.recipients[0]}")