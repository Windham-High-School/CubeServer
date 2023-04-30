"""Flask blueprint managing the IP camera"""

from flask import Blueprint, render_template, Response

bp = Blueprint('ipcam', __name__, url_prefix='/ipcam', template_folder='templates')

@bp.route('/')
def about():
    """Renders the main streaming page"""
    return render_template('stream.html.jinja2')
