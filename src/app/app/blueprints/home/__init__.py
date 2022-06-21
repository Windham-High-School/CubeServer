from flask import Blueprint, render_template

bp = Blueprint('home', __name__, url_prefix='/', template_folder='templates')

@bp.route('/')
def home():
    return render_template('home.html.jinja2')