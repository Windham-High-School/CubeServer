from flask import Blueprint, render_template

from app import app

bp = Blueprint('team', __name__, url_prefix='/team', template_folder='templates')

@bp.route('/register')
def register():
    if app.config['REGISTRATION_OPEN']:
        return render_template('register.html')
    else:
        return render_template('regclosed.html')