"""Flask blueprint managing an about/credits section for the web app"""

from flask import Blueprint, render_template

from cubeserver_common.metadata import LICENSE_FULL, AUTHORS, SERVER_NAME
from cubeserver_common.environ import EnvConfig

bp = Blueprint("about", __name__, url_prefix="/about", template_folder="templates")


@bp.route("/")
def about():
    """Renders the main about page"""
    return render_template(
        "about.html.jinja2",
        license=LICENSE_FULL,
        contributors=AUTHORS,
        server_str=SERVER_NAME,
        commit_hash=EnvConfig.CS_COMMIT_HASH,
    )
