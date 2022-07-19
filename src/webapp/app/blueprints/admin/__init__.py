"""Flask blueprint managing the administration side of the application"""

from datetime import timedelta
from math import floor
from bson import ObjectId
from flask import abort, Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from uptime import uptime
from app.models.utils import EnumCodec
from app.models.team import Team
from app.models.user import User, UserLevel
from app.tables.team import AdminTeamTable
from app.tables.users import AdminUserTable

from .user_form import InvitationForm

bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin',
    template_folder='templates'
)

@bp.route('/')
@login_required
def admin_home():
    """Renders the admin console"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    # Fetch teams from database and populate a table:
    teams_table = AdminTeamTable(Team.find())
    # Render the template:
    return render_template(
        'console.html.jinja2',
        teams_table = teams_table.__html__(),
        user_form = InvitationForm()
    )

@bp.route('/users')
@login_required
def edit_users():
    """Renders a page where the user database can be edited"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    # Fetch users from database and populate a table:
    users_table = AdminUserTable(User.find())
    # Render the template:
    return render_template(
        'user_table.html.jinja2',
        users_table = users_table.__html__()
    )

# The team modification API endpoint:
# TODO (low priority): Implement a RESTful API instead of the hokey one I made
@bp.route('/table_endpoint/<table>/<identifier>/<field>', methods=['POST', 'DELETE'])
@login_required
def table_endpoint(table, identifier, field):
    """Endpoint for the team/user modification API
    -- Action for forms within the table of users/teams"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    model_class = {
        "Team":Team,
        "User":User
    }[table]
    if request.method == 'POST':
        model_obj = model_class.find_by_id(ObjectId(identifier))
        model_obj.set_attr_from_string(field, request.form.get('item'))
        model_obj.save()
        return render_template('redirect_back.html.jinja2')
    elif request.method == 'DELETE':
        model_obj = model_class.find_by_id(ObjectId(identifier))
        model_obj.remove()
        return "OK"  # Maybe a JSON response would actually be useful?
                     # Note that as of now the response text is ignored anyway

@bp.route('/useradd', methods=['POST'])
@login_required
def useradd():
    """Invites a user"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    form = InvitationForm()
    if form.validate_on_submit():
        user_level = EnumCodec(UserLevel, str).transform_bson(form.level.data)
        new_user, activation_pwd = User.invite(user_level)
        new_user.save()
        activation_link = url_for(
            'home.activation',
            user=new_user.name,
            token=activation_pwd,
            _external=True
        )
        return render_template(
            'user_invitation.html.jinja2',
            username = new_user.name,
            password = activation_pwd,
            link = activation_link
        )
    return abort(500)

@bp.route('/uptime')
def uptime_string():
    """Provides a GET action to retrive the uptime of the server"""
    time_delta = timedelta(seconds=uptime())
    return f"{time_delta.days}&nbsp;Days, {time_delta.seconds//3600}&nbsp;" \
        f"Hours, {(time_delta.seconds//60)%60}&nbsp;Minutes, " \
        f"{floor(time_delta.seconds%60)}&nbsp;Seconds"
