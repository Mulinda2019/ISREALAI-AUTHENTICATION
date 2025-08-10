from flask import Blueprint
from app.utils.decorators import safe_render

main_bp = Blueprint("main", __name__)

@main_bp.route("/home", methods=["GET"])
def home():
    """Render the public landing page."""
    return safe_render("main/home.html")
