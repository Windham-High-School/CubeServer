"""Flask blueprint managing the administration side of the application"""

from datetime import timedelta
from math import floor
from flask import Blueprint, render_template
from uptime import uptime

bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

@bp.route('/')
def admin_home():
    """Renders the admin console"""
    return render_template('console.html.jinja2')

@bp.route('/uptime')
def uptime_string():
    """Provides a GET action to retrive the uptime of the server"""
    time_delta = timedelta(seconds=uptime())
    return f"{time_delta.days}&nbsp;Days, {time_delta.seconds//3600}&nbsp;" \
        f"Hours, {(time_delta.seconds//60)%60}&nbsp;Minutes, " \
        f"{floor(time_delta.seconds%60)}&nbsp;Seconds"
