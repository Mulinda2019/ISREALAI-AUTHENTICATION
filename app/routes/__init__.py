import logging
from flask import render_template
from jinja2 import TemplateNotFound

# Fallback logger setup
logger = logging.getLogger("safe_render")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def safe_render(template_name: str, **context):
    """Render a template, falling back to a placeholder if missing."""

    try:
        return render_template(template_name, **context)
    except TemplateNotFound:
        logger.warning(
            f"Template '{template_name}' not found. Falling back to 'under_construction'."
        )
        return render_template("placeholders/under_construction.html", **context)
    except Exception as e:
        logger.error(f"Unexpected error rendering '{template_name}': {e}")
        raise
