"""Unauthorized user home page"""

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from cubeserver_common.models.user import UserLevel

bp = Blueprint("home", __name__, url_prefix="/", template_folder="templates")


@bp.route("/")
def home():
    """Renders the home page"""
    if (
        current_user
        and current_user.is_authenticated
        and current_user.level == UserLevel.ADMIN
    ):
        return redirect(url_for("admin.home"))
    return render_template("home.html.jinja2")
