# app/cli/commands.py

import click
from flask import current_app
from flask.cli import with_appcontext
import logging

from app.extensions import db
from app.models.user import User  # Placeholder for DB model imports
from app.models.audit_log import AuditLog  # Corrected import for the AuditLog model

logger = logging.getLogger(__name__)


@click.command("create-admin")
@with_appcontext
def create_admin():
    """
    CLI command to create a default administrator account.

    Usage:
        flask create-admin
    """
    try:
        # You can adjust these values or make them interactive via click.prompt()
        default_admin = User(
            email="admin@isreal.ai",
            name="Default Admin",
            role="admin",
            is_verified=True
        )

        db.session.add(default_admin)
        db.session.commit()

        logger.info("Default admin account created: admin@isreal.ai")
        click.echo("✅ Admin account created successfully.")

    except Exception:
        db.session.rollback()
        logger.exception("Failed to create admin account.")
        click.echo("❌ Error: Could not create admin account.")


@click.command("clear-audit-logs")
@with_appcontext
def clear_audit_logs():
    """
    CLI command to purge all audit log entries.

    Usage:
        flask clear-audit-logs
    """
    try:
        num_deleted = AuditLog.query.delete()
        db.session.commit()

        logger.info(f"Cleared {num_deleted} audit log entries.")
        click.echo(f"🧹 Successfully cleared {num_deleted} audit logs.")

    except Exception:
        db.session.rollback()
        logger.exception("Failed to clear audit logs.")
        click.echo("❌ Error: Could not clear audit logs.")


def register_cli_commands(app):
    """
    Register all custom CLI commands to the Flask app context.

    Args:
        app (Flask): The main Flask application instance.
    """
    app.cli.add_command(create_admin)
    app.cli.add_command(clear_audit_logs)
    logger.info("🔧 CLI commands registered: create-admin, clear-audit-logs")