"""Flask blueprint managing an about/credits section for the web app"""

from flask import Blueprint, render_template

from cubeserver_common.metadata import VERSION, LICENSE_FULL, AUTHORS, TIMESTAMP

bp = Blueprint('about', __name__, url_prefix='/about', template_folder='templates')

@bp.route('/')
def about():
    """Renders the main about page"""
    return render_template('about.html.jinja2', version=VERSION, license=LICENSE_FULL, contributors=AUTHORS, timestamp=TIMESTAMP)
