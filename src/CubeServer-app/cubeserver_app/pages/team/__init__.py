"""Flask blueprint to handle team-related actions"""

from flask import Blueprint, session, redirect, render_template, url_for
from flask import request, abort, flash
from better_profanity import profanity
from flask_login import current_user
from hmac import compare_digest

from cubeserver_common import config
from cubeserver_common.models.mail import Message
from cubeserver_common.models.team import Team, TeamLevel, TeamStatus
from cubeserver_common.models.user import User, UserLevel
from ...errorviews import server_error
from . import registration_form

bp = Blueprint("team", __name__, url_prefix="/team", template_folder="templates")


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Renders the team registration page"""
    if config.DynamicConfig['Competition']['Registration Open']:
        form = registration_form.RegistrationForm()

        if form.validate_on_submit():
            # Deal with bad words:
            if config.DynamicConfig['Profanity']['Censor Names'] and (
                profanity.contains_profanity(form.team_name.data)
                or profanity.contains_profanity(form.member1.data)
                or profanity.contains_profanity(form.member2.data)
                or profanity.contains_profanity(form.member3.data)
            ):
                return redirect(url_for(".profanity_found"))
            if form.team_name.data in Team.RESERVED_NAMES:
                server_error(
                    ValueError(f"Cannot use reserved name {form.team_name.data}"),
                    message=(
                        "You tried to use a reserved name for your team. "
                        "Certain names are reserved for internal uses of the api and teams database, "
                        "interference with which could compromise the competition."
                    ),
                )
            # Create a Team object:
            try:
                level = TeamLevel(form.classification.data)
            except ValueError as exception:
                return server_error(
                    exception, message="An invalid classification value was given."
                )
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
            session["team_secret"] = team.secret
            session["team_name"] = team.name
            flash("Submitted!")

            return redirect(url_for(".success"))
        return render_template("register.html.jinja2", form=form)
    # Registration is not open:
    return render_template("regclosed.html.jinja2")


@bp.route("/confirm_email/<team_name>/<name>/<token>/<team_secret>")
def verify(team_name: str, name: str, token: str, team_secret: str):
    """Allows users to confirm email and intent to join a team"""
    team: Team = Team.find_by_name(team_name)
    if team.all_verified:
        return redirect(url_for(".success"))
    user = User.find_by_username(name)
    if user is not None and user.verify(token):
        user.save()
        flash("Email successfully verified!")
        session["team_secret"] = team_secret
        session["team_name"] = team_name
        if team.all_verified:
            send_success_email(team)
            flash("All users have verified their emails.")
        return redirect(url_for(".success"))
    return abort(403)


def send_verification_email(user: User, team: Team) -> None:
    """Emails a user asking them to verify their intent to join a team"""
    if user.email is None:
        raise TypeError(
            "Team users must have emails for verification"
        )
    Message(
        config.DynamicConfig['Email']['Automated Sender Name'],
        config.DynamicConfig['Email']['Automated Sender Address'],
        [user.email],
        "Please verify your email",
        (
            f"Hello {user.name},\n"
            f"You have been registered for {config.DynamicConfig['Strings']['Long Title']} team {team.name}!\n\n"
            f"{team.name}:\n" + "\n".join(f" - {member.name}" for member in team.members) + "\n\n"
            f"Please confirm that you consent to being on this team by clicking the link below:\n"
            f"{url_for('.verify', team_secret=team.secret, team_name=team.name, name=user.name, token=user.verification_token, _external=True)}"
        ),
    ).send()


def send_success_email(team):
    """Sends an email once ALL registered emails have been verified"""
    Message(
        config.FROM_NAME,
        config.FROM_ADDR,
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
        ),
    ).send()


@bp.route("/success")
def success():
    """Renders a message in the event of successful team registration"""
    if "team_secret" in request.args and "team_name" in request.args:
        # Allow session vars to be determined from a link from an auto registration confirmation email:
        session["team_secret"] = request.args.get("team_secret")
        session["team_name"] = request.args.get("team_name")

    if "team_secret" not in session:
        return redirect("/")

    actual_team = Team.find_by_name(session["team_name"])
    if actual_team is None:
        flash(
            f"Could not find registry for team {session['team_name']}",
            category="danger",
        )
        return redirect("/")
    if (
        actual_team.status == TeamStatus.INTERNAL
        or actual_team.weight_class == TeamLevel.REFERENCE
    ) and (current_user is None or current_user.level != UserLevel.ADMIN):
        flash(
            "You don't have permission to access this page for an internally reserved team."
        )
        return abort(403)

    return render_template(
        "success.html.jinja2",
        verified=Team.find_by_name(session["team_name"]).all_verified,
        secret=session["team_secret"],
        message=config.DynamicConfig["Strings"]["Registration Confirmation"],
    )


@bp.route("/update", methods=["GET", "POST"])
def update():
    """Allows teams to update the code on their cubes"""
    team: Team = Team.find_by_name(session["team_name"])
    if not compare_digest(session["team_secret"], team.secret):
        return abort(401)

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file uploaded.")
            return redirect(url_for(".update"))
        file = request.files["file"]
        if file.filename == "":
            flash("No file uploaded.")
            return redirect(url_for(".update"))
        if file and file.filename == "code.py":
            file_contents = file.stream.read()
            file.stream.close()
            file.close()
            if 0 < len(file_contents) <= config.EnvConfig.CS_MAX_UPLOAD_SIZE:
                team.update_code(file_contents)
                flash("Upload Successful.", category="success")
            else:
                flash("Bad file size.", category="danger")
                flash(
                    f"File size in bytes must satisfy the interval range (0, {config.EnvConfig.CS_MAX_UPLOAD_SIZE}]"
                )

        else:
            flash("File must be `code.py`.", category="danger")

    return render_template(
        "update_upload.html.jinja2", max_size=config.EnvConfig.CS_MAX_UPLOAD_SIZE
    )


@bp.route("/not-nice")
def profanity_found():
    """Renders a message in the event of profanity being input"""
    return render_template(
        "profanity_found.html.jinja2", message=config.DynamicConfig['Profanity']['Profanity Message']
    )
