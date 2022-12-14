"""Flask blueprint to handle team-related actions"""

from flask import Blueprint, session, redirect, render_template, url_for
from flask import current_app, request
from better_profanity import profanity

from cubeserver_common import config
from cubeserver_common.mail import Message
from cubeserver_common.models.team import Team, TeamLevel
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
               or profanity.contains_profanity(form.member3.data) \
               or profanity.contains_profanity(form.member4.data)):
                return redirect('/team/not-nice')
            # Create a Team object:
            try:
                level = TeamLevel(form.classification.data)
            except ValueError as exception:
                return server_error(exception, message="An invalid classification value was given.")
            members = [form.member1, form.member2, form.member3, form.member4]
            team = Team(form.team_name.data, level)
            for member in members:
                if member is not None and len(member.data) > 0:
                    user = User(member.data, UserLevel.PARTICIPANT, email.data)
                    user.save()
                    team.add_member(user)
            team.save()
            session['team_secret'] = team.secret
            session['team_name'] = team.name

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
                    f"{url_for('.success', team_secret=team.secret, team_name=team.name, _external=True)}"
                    "\n\nYou should save this email for reference.\n\n"
                    "Good Luck!"
                )
            ).send()

            return redirect('/team/success')
        return render_template('register.html.jinja2', form=form)
    return render_template('regclosed.html.jinja2')

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
        secret = session['team_secret']
    )

@bp.route('/not-nice')
def profanity_found():
    """Renders a message in the event of profanity being input"""
    return render_template('profanity_found.html.jinja2', message=config.PROFANITY_MESSAGE)
