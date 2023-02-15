"""Flask blueprint to handle team-related actions"""

from flask import Blueprint, session, redirect, render_template, url_for
from flask import current_app, request, abort, flash
from better_profanity import profanity

from cubeserver_common import config
from cubeserver_common.mail import Message
from cubeserver_common.models.team import Team, TeamLevel
from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.user import User, UserLevel
from cubeserver_app.errorviews import server_error
from . import registration_form

bp = Blueprint('team', __name__, url_prefix='/team', template_folder='templates')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Renders the team registration page"""
    if current_app.config['CONFIGURABLE'].registration_open:
        form = registration_form.RegistrationForm()

        if form.validate_on_submit():
            # Deal with bad words:
            if config.CHECK_PROFANITY \
               and (profanity.contains_profanity(form.team_name.data) \
               or profanity.contains_profanity(form.member1.data) \
               or profanity.contains_profanity(form.member2.data) \
               or profanity.contains_profanity(form.member3.data)):
                return redirect(url_for('.profanity_found'))
            # Create a Team object:
            try:
                level = TeamLevel(form.classification.data)
            except ValueError as exception:
                return server_error(exception, message="An invalid classification value was given.")
            members = [form.member1, form.member2, form.member3]
            emails = [form.email1, form.email2, form.email3]
            team = Team(form.team_name.data, level)
            for member, email in zip(members, emails):
                if member is not None and len(member.data) > 0:
                    user = User(member.data, UserLevel.PARTICIPANT, email.data)
                    user.save()
                    send_verification_email(user, team)
                    team.add_member(user)
            team.save()
            session['team_secret'] = team.secret
            session['team_name'] = team.name
            flash("Submitted!")

            return redirect(url_for('.success'))
        return render_template('register.html.jinja2', form=form)
    return render_template('regclosed.html.jinja2')

@bp.route('/confirm_email/<team_name>/<name>/<token>/<team_secret>')
def verify(team_name, name, token, team_secret):
    """Allows users to confirm email and intent to join a team"""
    team: Team = Team.find_by_name(team_name)
    if team.all_verified:
        return redirect(url_for('.success'))
    user = User.find_by_username(name)
    if user is not None and user.verify(token):
        user.save()
        flash("Email successfully verified!")
        session['team_secret'] = team_secret
        session['team_name'] = team_name
        if team.all_verified:
            send_success_email(team)
            flash("All users have verified their emails.")
        return redirect(url_for('.success'))
    return abort(403)

def send_verification_email(user, team):
    """Emails a user asking them to verify their intent to join a team"""
    Message(
        config.FROM_NAME,
        config.FROM_ADDR,
        [user.email],
        "Please verify your email",
        (
            f"Hello {user.name},\n"
            f"You have been registered for {config.LONG_TITLE} team {team.name}!\n"
            f"Please confirm that this was you by clicking the link below:\n"
            f"{url_for('.verify', team_secret=team.secret, team_name=team.name, name=user.name, token=user.verification_token, _external=True)}"
        )
    ).send()

def send_success_email(team):
    """Sends an email once ALL registered emails have been verified"""
    Message(
                config.FROM_NAME, config.FROM_ADDR,
                team.emails,
                # TODO: Make email text configurable:
                "THE PROJECT- Registration Info",
                (
                    f"Thank you for registering your team, {team.name}!\n\n"
                    "Please verify that all of the following information is correct:\n"
                    f"\tTeam name: {team.name}\n"
                    f"\tTeam division: {team.weight_class.value}\n"
                    f"\tTeam members: {team.members_str}\n\n"
                    "Your team will appear on the leaderboard as soon as you are approved by an admin.\n"
                    "Once approved, you will also be able to submit data to the server-\n"
                    "To get started with programming your microcontroller, see here:\n"
                    f"{url_for('.success', team_secret=team.secret, team_name=team.name, _external=True)}\n"
                    "DO NOT SHARE THIS EMAIL OR LINK WITH ANYONE!\n"
                    "Doing so would allow them to impersonate your team's cube!\n"
                    "\n\nYou should save this email for reference.\n\n"
                    "Good Luck!"
                )
            ).send()

@bp.route('/success')
def success():
    """Renders a message in the event of successful team registration"""
    if 'team_secret' in request.args and 'team_name' in request.args:
        # Allow session vars to be determined from a link from an auto registration confirmation email:
        session['team_secret'] = request.args.get('team_secret')
        session['team_name'] = request.args.get('team_name')

    if 'team_secret' not in session:
        return redirect('/')

    return render_template(
        'success.html.jinja2',
        verified = Team.find_by_name(session['team_name']).all_verified,
        secret = session['team_secret'],
        message = Conf.retrieve_instance().reg_confirmation
    )

@bp.route('/update', methods=['GET', 'POST'])
def update():
    """Allows teams to update the code on their cubes"""
    team: Team = Team.find_by_name(session['team_name'])
    if session['team_secret'] != team.secret:
        return abort(401)
    
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file uploaded.")
            return redirect(url_for('.update'))
        file = request.files['file']
        if file.filename == '':
            flash('No file uploaded.')
            return redirect(url_for('.update'))
        if file and file.filename == "code.py":
            file_contents = file.stream.read()
            file.stream.close()
            file.close()
            if 0 < len(file_contents) <= config.TEAM_MAX_UPDATE_LENGTH:
                team.update_code(file_contents)
                flash("Upload Successful.", category='success')
            else:
                flash("Bad file size.", category='danger')
                flash(
                    f"File size must satisfy the range interval (0, {config.TEAM_MAX_UPDATE_LENGTH}]"
                )

        else:
            flash('File must be `code.py`.', category='danger')

    
    return render_template(
        'update_upload.html.jinja2',
        max_size=config.TEAM_MAX_UPDATE_LENGTH
    )

@bp.route('/not-nice')
def profanity_found():
    """Renders a message in the event of profanity being input"""
    return render_template('profanity_found.html.jinja2', message=config.PROFANITY_MESSAGE)
