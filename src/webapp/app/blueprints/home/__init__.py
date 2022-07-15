"""Flask blueprint to manage the home page"""

from flask import Blueprint, render_template

from app.models.team import Team, TeamStatus
from app.tables.team import LeaderboardTeamTable

bp = Blueprint('home', __name__, url_prefix='/', template_folder='templates')

@bp.route('/')
def home():
    """Renders the home page"""
    return render_template('home.html.jinja2')

@bp.route('/stats')
def admin_home():
    """Renders the leaderboard/stats"""
    # Fetch teams from database and populate a table:
    team_objects = [Team.decode(team) for team in Team.collection.find(
        {"status": {"$nin":[TeamStatus.UNAPPROVED.value]}}
    )]
    teams_table = LeaderboardTeamTable(team_objects)
    # Render the template:
    return render_template(
        'leaderboard.html.jinja2',
        teams_table = teams_table.__html__()
    )