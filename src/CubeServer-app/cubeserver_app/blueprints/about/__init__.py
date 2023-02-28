"""Flask blueprint managing an about/credits section for the web app"""

from flask import Blueprint, render_template

from cubeserver_common.metadata import VERSION, LICENSE, AUTHORS, TIMESTAMP

bp = Blueprint('about', __name__, url_prefix='/about', template_folder='templates')

@bp.route('/')
def about():
    """Renders the main about page"""
    print(AUTHORS)
    return render_template('about.html.jinja2', version=VERSION, license=LICENSE, contributors=AUTHORS, timestamp=TIMESTAMP)
