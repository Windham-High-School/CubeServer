"""Flask blueprint to manage the home page"""

from flask import Blueprint, render_template

bp = Blueprint('home', __name__, url_prefix='/', template_folder='templates')

@bp.route('/')
def home():
    """Renders the home page"""
    return render_template('home.html.jinja2')
