"""Flask blueprint managing the administration side of the application"""

from datetime import timedelta
from math import floor
from bson import ObjectId
from flask import Blueprint, redirect, render_template, request, url_for
from uptime import uptime
from app.models.team import Team
from app.tables.team import AdminTeamTable

bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin',
    template_folder='templates'
)

@bp.route('/')
def admin_home():
    """Renders the admin console"""
    # Fetch teams from database and populate a table:
    team_objects = [Team.decode(team) for team in Team.collection.find()]
    print(team_objects)
    for team in team_objects:
        print(vars(team))
    teams_table = AdminTeamTable(team_objects)
    # Render the template:
    return render_template(
        'console.html.jinja2',
        teams_table = teams_table.__html__()
    )

# The team modification API endpoint:
# TODO (low priority): Implement a RESTful API instead of the hokey one I made
@bp.route('/table_endpoint/<identifier>/<field>', methods = ['POST', 'DELETE'])
def team_change_endpoint(identifier, field):
    """Endpoint for the team modification API
    -- Action for forms within the table of teams"""
    # TODO: Check for authentication
    if request.method == 'POST':
        team = Team.find_by_id(ObjectId(identifier))
        print(Team.encode(team))
        team.set_attr_from_string(field, request.form.get('item'))
        team.save()
        return redirect(url_for('.admin_home'))
    if request.method == 'DELETE':
        team = Team.find_by_id(ObjectId(identifier))
        team.remove()
    return render_template("/errorpages/unimplemented.html.jinja2")

@bp.route('/uptime')
def uptime_string():
    """Provides a GET action to retrive the uptime of the server"""
    time_delta = timedelta(seconds=uptime())
    return f"{time_delta.days}&nbsp;Days, {time_delta.seconds//3600}&nbsp;" \
        f"Hours, {(time_delta.seconds//60)%60}&nbsp;Minutes, " \
        f"{floor(time_delta.seconds%60)}&nbsp;Seconds"
