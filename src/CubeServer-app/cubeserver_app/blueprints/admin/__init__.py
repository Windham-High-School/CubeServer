"""Flask blueprint managing the administration side of the application"""

# TODO: Restructure blueprint files- This whole thing is an absolute mess!
# Arnold Schwarzenegger looked at this code and called it "one ugly motha*****".

from datetime import timedelta
from math import floor
from bson.objectid import ObjectId
from flask import abort, Blueprint, render_template, request, url_for, current_app, flash, session
from flask_login import current_user, login_required
from typing import cast
from uptime import uptime
import traceback
import base64
import jsonpickle

from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.datapoint import DataPoint, DataClass
from cubeserver_common.models.utils import EnumCodec
from cubeserver_common.models.config.rules import Rules
from cubeserver_common.models.team import Team, TeamLevel
from cubeserver_common.models.user import User, UserLevel
from cubeserver_common.models.multiplier import Multiplier, MassMultiplier, VolumeMultiplier, CostMultiplier, VolumeUnit
from cubeserver_common.mail import Message
from cubeserver_common.beacon import BeaconMessage, Beacon, BeaconMessageEncoding
from cubeserver_common.models.reference import ReferencePoint
from cubeserver_common.config import FROM_NAME, FROM_ADDR

from cubeserver_app.tables.team import AdminTeamTable
from cubeserver_app.tables.users import AdminUserTable
from cubeserver_app.tables.datapoints import AdminDataTable

from .user_form import InvitationForm
from .config_form import ConfigurationForm
from .rules_form import RulesForm
from .multiplier_form import MultiplierForm, SIZE_NAME_MAPPING
from .email_form import EmailForm
from .beacon_form import ImmediateBeaconForm

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

    # Populate configuration form:
    conf_form = ConfigurationForm()
    db_conf = Conf.retrieve_instance()
    conf_form.registration_open.data = db_conf.registration_open
    conf_form.home_description.data = db_conf.home_description
    conf_form.smtp_credentials.data = f"{db_conf.smtp_user}:{db_conf.smtp_pass}"
    conf_form.smtp_server.data = db_conf.smtp_server
    conf_form.email_domain.data = db_conf.email_domain
    conf_form.reg_confirmation.data = db_conf.reg_confirmation
    conf_form.notify_teams.data = db_conf.notify_teams

    # Render the template:
    return render_template(
        'console.html.jinja2',
        teams_table = teams_table.__html__(),
        user_form = InvitationForm(),
        config_form = conf_form,
        beacon_form = ImmediateBeaconForm(),
        email_groups = {
            TeamLevel.JUNIOR_VARSITY.value: base64.urlsafe_b64encode(',  '.join([
                ', '.join(team.emails) for team in
                    Team.find_by_division(TeamLevel.JUNIOR_VARSITY)
            ]).encode()),
            TeamLevel.VARSITY.value: base64.urlsafe_b64encode(',  '.join([
                ', '.join(team.emails) for team in
                    Team.find_by_division(TeamLevel.VARSITY)
            ]).encode()),
            'All Teams': base64.urlsafe_b64encode(',  '.join([
                ', '.join(team.emails) for team in
                    Team.find()
            ]).encode())
        }.items()
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

@bp.route('/manually_score/<teamid>/<dataclass_str>', methods=['POST'])
@login_required
def manual_scoring(teamid, dataclass_str):
    """Endpoint for the manual scoring api
    -- Action for forms within the table of users/teams"""
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    team = Team.find_by_id(ObjectId(teamid))
    if team is None:
        return abort(500, message="Bro, you're trying to submit data for a team that doesn't exist, man!")
    dataclass = DataClass(dataclass_str)
    if dataclass.datatype == bool:
        value = request.form.get('item') == "true"
    else:
        value = dataclass.datatype(request.form.get('item'))
    data_point = DataPoint(
        ObjectId(teamid),
        dataclass,
        value
    )
    if Rules.retrieve_instance().post_data(team, data_point):
        return "OK"
    return abort(500, message="Something went wrong.")


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
        "User":User,
        "DataPoint":DataPoint
    }[table]
    model_obj = model_class.find_by_id(ObjectId(identifier))
    if model_class == Team and Conf.retrieve_instance().notify_teams:  # Notify the team of changes:
        desc_str = "deleted" if request.method == 'DELETE' else f"given a {field} of {request.form.get('item')}"
        Message(
            FROM_NAME,
            FROM_ADDR,
            cast(Team, model_obj).emails,
            "Admin Change to Your Team",
            (
               f"Your team was {desc_str}.\n"
               "For more info, check your status on the leaderboard: "
               f"{url_for('home.leaderboard', _external=True)}"
            ) + 
            ((
                f"\n\nComment: {request.form.get('comment')}"
            ) if request.form.get('comment') is not None else "") 
        ).send()
    if request.method == 'POST':
        if field == "score_increment" and model_class == Team:
            cast(Team, model_obj).health.change(float(request.form.get('item')))
        else:
            model_obj.set_attr_from_string(field, request.form.get('item'))
        model_obj.save()
        return render_template('redirect_back.html.jinja2')
    elif request.method == 'DELETE':
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

@bp.route('/configchange', methods=['POST'])
@login_required
def conf_change():
    """Modifies the configuration"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    form = ConfigurationForm()
    if form.validate_on_submit():
        db_conf: Conf = Conf.retrieve_instance()
        db_conf.registration_open = form.registration_open.data
        db_conf.home_description = form.home_description.data
        db_conf.smtp_server = form.smtp_server.data
        db_conf.reg_confirmation = form.reg_confirmation.data
        db_conf.email_domain = form.email_domain.data
        db_conf.notify_teams = form.notify_teams.data
        credentials = form.smtp_credentials.data.strip().split(':')
        if len(credentials) > 1:
            db_conf.smtp_user = credentials[0]
            db_conf.smtp_pass = credentials[1]
        db_conf.save()
        current_app.config['CONFIGURABLE'] = db_conf
        return render_template('redirect_back.html.jinja2')
    return abort(500)

@bp.route('/uptime')
def uptime_string():
    """Provides a GET action to retrive the uptime of the server"""
    time_delta = timedelta(seconds=uptime())
    return f"{time_delta.days}&nbsp;Days, {time_delta.seconds//3600}&nbsp;" \
        f"Hours, {(time_delta.seconds//60)%60}&nbsp;Minutes, " \
        f"{floor(time_delta.seconds%60)}&nbsp;Seconds"

@bp.route('/data')
@login_required
def data_table():
    """Shows all of the data in a big table"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    table = AdminDataTable(DataPoint.find())
    # Render the template:
    return render_template(
        'data_table.html.jinja2',
        table = table.__html__()
    )

@bp.route('/refdata')
@login_required
def reference_data_table():
    """Shows all of the reference data in a big table"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    table = AdminDataTable(ReferencePoint.find())
    # Render the template:
    return render_template(
        'data_table.html.jinja2',
        table = table.__html__()
    )

@bp.route('/settings')
@login_required
def game_settings():
    """Allows the admin user to edit game parameters
    that have to do with scoring and stuff"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    form = RulesForm()
    form.json_str.data = Rules.retrieve_instance().to_json()
    # Render the template:
    return render_template(
        'game_settings.html.jinja2',
        config_form = form
    )

@bp.route('/settingschange', methods=['POST'])
@login_required
def settings_change():
    """Modifies the game settings"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    form = RulesForm()
    if form.validate_on_submit():
#        db_conf = Rules.retrieve_instance()
        try:
            db_conf = Rules.from_json(form.json_str.data)
            db_conf.save()
        except:  # TODO: Is this poor practice?
            tb = traceback.format_exc()
            print(tb)
            return render_template('errorpages/500.html.jinja2', message=tb)
        return render_template('redirect_back.html.jinja2')
    return abort(500)

@bp.route('/team/<team_name>')
@login_required
def team_info(team_name: str = ""):
    """A page showing team info & score tally"""
    # Look-up the team:
    team = Team.find_by_name(team_name)
    if team is None:
        return abort(400)
    # Generate data table:
    data_table = AdminDataTable(DataPoint.find_by_team(team))
    # Multiplier editing form:
    form = MultiplierForm()
    form.team_id.data = str(team._id)
    form.size.data = team.multiplier.vol_mult.amt
    form.cost.data = team.multiplier.cost_mult.amt
    form.mass.data = team.multiplier.mass_mult.amt
    # Render the template
    return render_template(
        'team_edit.html.jinja2',
        team=team,
        table=data_table.__html__(),
        mult_form=form,
        emails=base64.urlsafe_b64encode(
            ', '.join(team.emails).encode()
        )
    )

@bp.route('/multiplier', methods=['POST'])
@login_required
def multiplier_change():
    """Modifies a team's multiplier"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    form = MultiplierForm()
    if form.validate_on_submit():
#        db_conf = Rules.retrieve_instance()
        try:
            team = Team.find_by_id(form.team_id.data)
            team.multiplier = Multiplier(
                CostMultiplier(team.weight_class, form.cost.data),
                MassMultiplier(team.weight_class, form.mass.data),
                VolumeMultiplier(team.weight_class,
                    VolumeUnit(SIZE_NAME_MAPPING[form.size.data])
                )
            )
            team.save()
        except:  # TODO: Is this poor practice?
            tb = traceback.format_exc()
            print(tb)
            return render_template('errorpages/500.html.jinja2', message=tb)
        return render_template('redirect_back.html.jinja2')
    return abort(500)


@bp.route('/mail', methods=['GET', 'POST'],
    defaults={'recipients': base64.urlsafe_b64encode(b'')})
@bp.route('/mail/<recipients>', methods=['GET', 'POST'])
@login_required
def email(recipients):
    """Sends an email.
    Optionally:
    Autofill the form with a base64-encoded comma-separated list of recipients
    """
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    form = EmailForm()
    if form.validate_on_submit():
        msg = Message(
            form.name.data,
            form.addr.data,
            form.to.data.replace(' ', '').split(','),
            form.subject.data,
            form.message.data
        )
        if msg.send():
            flash("Email Sent!")
        else:
            flash("Sending failed.", category="error")
        return render_template('redirect_back.html.jinja2')
    form.to.data = base64.urlsafe_b64decode(recipients).decode()
    return render_template(
        'sendmail.html.jinja2',
        mail_form = form
    )


@bp.route('/beaconnow', methods=['POST'])
@login_required
def beacon_tx():
    """Preps an immediate message from the beacon for transmission"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    form = ImmediateBeaconForm()
    if form.validate_on_submit():
        try:
            msg = BeaconMessage(
                str(form.message.data),
                BeaconMessageEncoding(form.msg_format.data)
            )
            session["beacon-tx"] = jsonpickle.encode(msg)
        except:  # TODO: Is this poor practice?
            tb = traceback.format_exc()
            print(tb)
            return render_template('errorpages/500.html.jinja2', message=tb)
        return render_template(
            'beacon_txing.html.jinja2',
            message_bytes_as_str=str(msg.message_bytes)
        )
    return abort(500)


@bp.route('/beacontx')
@login_required
def beacon_txing():
    """Actually transmits the prepared message and waits..."""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)

    msg = jsonpickle.decode(session.pop('beacon-tx'))
    msg.transmit()

    return render_template(
        'beacon_tx_done.html.jinja2'
    )
