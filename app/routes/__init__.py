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

def safe_render(template_name: str):
    """
    Safely attempt to render a template. Falls back to 'under_construction'
    if the specified template is missing.

    Args:
        template_name (str): Name of the template to render.

    Returns:
        str: Rendered template HTML.
    """
    try:
        return render_template(template_name)
    except TemplateNotFound:
        logger.warning(f"Template '{template_name}' not found. Falling back to 'under_construction'.")
        return render_template("placeholders/under_construction.html")
    except Exception as e:
        logger.error(f"Unexpected error rendering '{template_name}': {e}")
        raise