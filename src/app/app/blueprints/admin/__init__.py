from flask import Blueprint, render_template

bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

@bp.route('/')
def admin_home():
    return render_template('errorpages/unimplemented.html')