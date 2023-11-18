"""Flask blueprint managing the administration side of the application"""

# TODO: Restructure blueprint files- This whole thing is an absolute mess!
# Arnold Schwarzenegger looked at this code and called it "one ugly motha*****".

import logging
import csv
import shutil
import os
from datetime import timedelta
from math import floor
from random import randint
import subprocess
from cubeserver_common.models.reference import Reference
from bson.objectid import ObjectId
from flask import (
    abort,
    Blueprint,
    make_response,
    render_template,
    request,
    url_for,
    current_app,
    flash,
    session,
    send_file,
    redirect,
    request,
)
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from typing import cast, List
from uptime import uptime
import traceback
import base64
import jsonpickle
from json import loads, dumps
from pprint import pformat
from datetime import datetime
import re

from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.datapoint import DataPoint, DataClass
from cubeserver_common.models.utils import EnumCodec, Encodable
from bson import _BUILT_IN_TYPES as BSON_TYPES
from cubeserver_common.models.config.rules import Rules
from cubeserver_common.models.team import Team, TeamLevel, TeamStatus
from cubeserver_common.models.user import User, UserLevel
from cubeserver_common.models.beaconmessage import OutputDestination
from cubeserver_common.models.multiplier import (
    Multiplier,
    MassMultiplier,
    VolumeMultiplier,
    CostMultiplier,
    VolumeUnit,
)
from cubeserver_common.models.mail import Message
from cubeserver_common.models.beaconmessage import (
    BeaconMessage,
    BeaconMessageEncoding,
    SentStatus,
)
from cubeserver_common.models.reference import ReferencePoint
from cubeserver_common.config import (
    FROM_NAME,
    FROM_ADDR,
    INTERNAL_SECRET_LENGTH,
    TEMP_PATH,
)

from flask_table import Table
import pymongo
from cubeserver_app import settings
from cubeserver_app.tables.columns import PreCol, OptionsCol

from cubeserver_app.tables.team import AdminTeamTable
from cubeserver_app.tables.users import AdminUserTable
from cubeserver_app.tables.datapoints import AdminDataTable
from cubeserver_app.tables.beaconmessages import BeaconMessageTable
from cubeserver_app.tables.email import AdminEmailTable

from .user_form import InvitationForm
from .config_form import ConfigurationForm
from .rules_form import RulesForm
from .multiplier_form import MultiplierForm, SIZE_NAME_MAPPING
from .email_form import EmailForm
from .beacon_form import ImmediateBeaconForm


__STR_COLLECTION_MAPPING = {
    "Team": Team,
    "User": User,
    "DataPoint": DataPoint,
    "BeaconMessage": BeaconMessage,
}

bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")

order_re = re.compile("^order\[(?P<index>[0-9]+)\]\[(?P<name>.*)\]$")

ORDER_MAPPING = {"asc": pymongo.ASCENDING, "desc": pymongo.DESCENDING}


def parse_query(cls, cols, args, filter=None):
    # order[0][column]=0&order[0][dir]=desc&start=0&length=5
    order = [
        (int(a[0].groups()[0]), a[0].groups()[1], a[1])
        for a in [(order_re.match(x[0]), x[1]) for x in args.items()]
        if a[0]
    ]
    order.sort(key=lambda x: x[0])
    order = [{x[1]: x[2] for x in order}]
    col_keys = list(cols.keys())
    sort = [(col_keys[int(x["column"])], ORDER_MAPPING[x["dir"]]) for x in order]

    limit = int(args.get("length", 5))
    if limit == -1:
        limit = 0
    return cls.find(
        filter=filter, skip=int(args.get("start", 0)), limit=limit, sort=sort
    )


@bp.route("/")
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
    conf_form.competition_on.data = db_conf.competition_on
    conf_form.registration_open.data = db_conf.registration_open
    conf_form.home_description.data = db_conf.home_description
    conf_form.smtp_credentials.data = f"{db_conf.smtp_user}:{db_conf.smtp_pass}"
    conf_form.smtp_server.data = db_conf.smtp_server
    conf_form.email_domain.data = db_conf.email_domain
    conf_form.reg_confirmation.data = db_conf.reg_confirmation
    conf_form.notify_teams.data = db_conf.notify_teams
    conf_form.team_email_quota.data = db_conf.team_email_quota
    conf_form.quota_reset_hour.data = db_conf.quota_reset_hour
    conf_form.banner_message.data = db_conf.banner_message
    conf_form.beacon_polling_period.data = db_conf.beacon_polling_period

    # Reserved / internal team handling:
    reserved_links = []
    for name in Team.RESERVED_NAMES:
        team = Team.find_by_name(name)
        if team is not None:
            reserved_links += [
                (
                    name,
                    None,
                    url_for(".referencetest", station_id=team.reference_id)
                    if team.is_reference
                    else None,
                )
            ]
        else:
            reserved_links += [(name, url_for(".gen_reserved", name=name), None)]

    # Beacon Status:
    txd = 0
    sched = 0
    missed = 0
    for msg in BeaconMessage.find_since(timedelta(days=1)):
        if msg.status == SentStatus.TRANSMITTED:
            txd += 1
        elif msg.status == SentStatus.MISSED:
            missed += 1
        elif msg.status == SentStatus.SCHEDULED:
            sched += 1
    beacon_status = {
        "transmitted_today": txd,
        "missed_today": missed,
        "scheduled_today": sched,
        "queued": len(BeaconMessage.find_by_status(SentStatus.QUEUED)),
        "transmitted": len(BeaconMessage.find_by_status(SentStatus.TRANSMITTED)),
        "missed": len(BeaconMessage.find_by_status(SentStatus.MISSED)),
    }

    # Render the template:
    return render_template(
        "console.html.jinja2",
        teams_table=teams_table.__html__(),
        user_form=InvitationForm(),
        config_form=conf_form,
        email_groups={
            TeamLevel.JUNIOR_VARSITY.value: base64.urlsafe_b64encode(
                ",  ".join(
                    [
                        ", ".join(team.emails)
                        for team in Team.find_by_division(TeamLevel.JUNIOR_VARSITY)
                    ]
                ).encode()
            ),
            TeamLevel.VARSITY.value: base64.urlsafe_b64encode(
                ",  ".join(
                    [
                        ", ".join(team.emails)
                        for team in Team.find_by_division(TeamLevel.VARSITY)
                    ]
                ).encode()
            ),
            "All Teams": base64.urlsafe_b64encode(
                ",  ".join([", ".join(team.emails) for team in Team.find()]).encode()
            ),
        }.items(),
        beacon_stats=beacon_status,
        reserved_names=reserved_links,
        rand=randint(0, 1000000),
    )


@bp.route("/csv-endpoint", methods=["POST"])
@login_required
def beacon_csv():
    """CSV beacon packet bulk-upload"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    if "file" not in request.files:
        flash("No file uploaded.")
        return redirect(url_for(".admin_home"))
    file = request.files["file"]
    if file.filename == "":
        flash("No file uploaded.")
        return redirect(url_for(".admin_home"))
    if file and file.filename.lower().endswith(".csv"):
        logging.debug("Reading CSV of BeaconMessage objects")
        file_path = os.path.join(TEMP_PATH, secure_filename(file.filename))
        file.save(file_path)
        file.close()
        reopened = open(file_path, "r")
        try:
            csv_reader = csv.DictReader(reopened)
            for row in csv_reader:
                if (
                    row["time"] == ""
                    or row["body"] == ""
                    or row["output"] == ""
                    or row["encoding"] == ""
                    or row["misfire grace time"] == ""
                    or row["intensity"] == ""
                ):
                    continue
                BeaconMessage(
                    instant=datetime.fromisoformat(row["time"]),
                    division=TeamLevel(row["division"]),
                    message=row["body"],
                    destination=OutputDestination(row["output"]),
                    encoding=BeaconMessageEncoding(row["encoding"]),
                    misfire_grace=int(row["misfire grace time"]),
                    intensity=int(row["intensity"]),
                ).save()
        except:
            flash("There was a problem processing your CSV")
            tb = traceback.format_exc()
            logging.error(tb)  # TODO: Allow the finally clause to run!
            return render_template("errorpages/500.html.jinja2", message=tb)
        finally:
            reopened.close()
        return redirect(url_for(".beacon_table"))
    else:
        flash("You didn't upload a CSV file, bro!")
        return redirect(url_for(".admin_home"))


@bp.route("/users")
@login_required
def edit_users():
    """Renders a page where the user database can be edited"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    # Fetch users from database and populate a table:
    users_table = AdminUserTable(User.find())
    # Render the template:
    return render_template("user_table.html.jinja2", users_table=users_table.__html__())


# The team modification API endpoint:


@bp.route("/manually_score/<teamid>/<dataclass_str>", methods=["POST"])
@login_required
def manual_scoring(teamid, dataclass_str):
    """Endpoint for the manual scoring api
    -- Action for forms within the table of users/teams"""
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    team = Team.find_by_id(ObjectId(teamid))
    if team is None:
        return abort(
            500,
            message="Bro, you're trying to submit data for a team that doesn't exist, man!",
        )
    dataclass = DataClass(dataclass_str)
    if dataclass.datatype == bool:
        value = request.form.get("item") == "true"
    else:
        value = dataclass.datatype(request.form.get("item"))
    data_point = DataPoint(ObjectId(teamid), dataclass, value)
    if Rules.retrieve_instance().post_data(data_point):
        return "OK"
    return abort(500, message="Something went wrong.")


# TODO (low priority): Implement a RESTful API instead of the hokey one I made
@bp.route("/table_endpoint/<table>/<identifier>/<field>", methods=["POST", "DELETE"])
@login_required
def table_endpoint(table, identifier, field):
    """Endpoint for the team/user modification API
    -- Action for forms within the table of users/teams"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    model_class = __STR_COLLECTION_MAPPING[table]
    model_obj = model_class.find_by_id(ObjectId(identifier))
    if (
        model_class == Team and Conf.retrieve_instance().notify_teams
    ):  # Notify the team of changes:
        desc_str = (
            "deleted"
            if request.method == "DELETE"
            else f"given a {field} of {request.form.get('item')}"
        )
        if Message(
            FROM_NAME,
            FROM_ADDR,
            cast(Team, model_obj).emails,
            "Admin Change to Your Team",
            (
                f"Your team was {desc_str}.\n"
                "For more info, check your status on the leaderboard: "
                f"{url_for('home.leaderboard', _external=True)}"
            )
            + (
                (f"\n\nComment: {request.form.get('comment')}")
                if request.form.get("comment") is not None
                else ""
            ),
        ).send():
            flash(f"Notified {cast(Team, model_obj).name} of change", category="info")
        else:
            flash(
                f"Failed to notify the team {cast(Team, model_obj).name}.",
                category="danger",
            )
    if request.method == "POST":
        if field == "score_increment" and model_class == Team:
            cast(Team, model_obj).health.change(float(request.form.get("item")))
        elif field == "score_recomputation" and model_class == Team:
            cast(Team, model_obj).recompute_score()
            return render_template("redirect_back.html.jinja2")
        elif field == "score_recomputation" and model_class == DataPoint:
            cast(DataPoint, model_obj).recalculate_score()
            return render_template("redirect_back.html.jinja2")
        else:
            if (
                field == "rawscore" and model_class == DataPoint
            ):  # Manually setting dp point value
                team = Team.find_by_id(cast(DataPoint, model_obj).team_reference)
                init_rawscore = cast(DataPoint, model_obj).rawscore

            # Change that Make!
            model_obj.set_attr_from_string(field, request.form.get("item"))

            if (
                field == "rawscore" and model_class == DataPoint
            ):  # Manually setting dp point value
                team.health.change(
                    cast(DataPoint, model_obj).multiplier
                    * (cast(DataPoint, model_obj).rawscore - init_rawscore)
                )
                team.save()
        model_obj.save()
        return render_template("redirect_back.html.jinja2")
    elif request.method == "DELETE":
        model_obj.remove()
        return "OK"  # Maybe a JSON response would actually be useful?
        # Note that as of now the response text is ignored anyway


@bp.route("/useradd", methods=["POST"])
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
            "home.activation", user=new_user.name, token=activation_pwd, _external=True
        )
        return render_template(
            "user_invitation.html.jinja2",
            username=new_user.name,
            password=activation_pwd,
            link=activation_link,
        )
    return abort(500)


@bp.route("/configchange", methods=["POST"])
@login_required
def conf_change():
    """Modifies the configuration"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    form = ConfigurationForm()
    if form.validate_on_submit():
        # Update database from form:
        db_conf: Conf = Conf.retrieve_instance()
        db_conf.competition_on = form.competition_on.data
        db_conf.registration_open = form.registration_open.data
        db_conf.home_description = form.home_description.data
        db_conf.smtp_server = form.smtp_server.data
        db_conf.reg_confirmation = form.reg_confirmation.data
        db_conf.email_domain = form.email_domain.data
        db_conf.notify_teams = form.notify_teams.data
        db_conf.team_email_quota = form.team_email_quota.data
        db_conf.quota_reset_hour = form.quota_reset_hour.data
        db_conf.banner_message = form.banner_message.data
        db_conf.beacon_polling_period = form.beacon_polling_period.data
        credentials = form.smtp_credentials.data.strip().split(":")
        if len(credentials) > 1:
            db_conf.smtp_user = credentials[0]
            db_conf.smtp_pass = credentials[1]
        db_conf.save()
        current_app.config["CONFIGURABLE"] = db_conf
        return render_template("redirect_back.html.jinja2")
    return abort(500)


@bp.route("/uptime")
def uptime_string():
    """Provides a GET action to retrive the uptime of the server"""
    time_delta = timedelta(seconds=uptime())
    return (
        f"{time_delta.days}&nbsp;Days, {time_delta.seconds//3600}&nbsp;"
        f"Hours, {(time_delta.seconds//60)%60}&nbsp;Minutes, "
        f"{floor(time_delta.seconds%60)}&nbsp;Seconds"
    )


@bp.route("/data")
@login_required
def data_table():
    """Shows all of the data in a big table"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    table = AdminDataTable([])
    if request.args.get("ajax") == "true":
        results = parse_query(DataPoint, table._cols, request.args)
        data = [
            [c.td_contents(item, [attr]) for attr, c in table._cols.items() if c.show]
            for item in results
        ]
        count = len(DataPoint.find())
        return {
            "draw": int(request.args.get("draw", 0)) + 1,
            "recordsTotal": count,
            "recordsFiltered": count,
            "data": data,
        }
    else:
        # Render the template:
        return render_template("data_table.html.jinja2", table=table.__html__())


@bp.route("/settings")
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
    return render_template("game_settings.html.jinja2", config_form=form)


@bp.route("/settingschange", methods=["POST"])
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
        except:
            tb = traceback.format_exc()
            logging.error(tb)
            return render_template("errorpages/500.html.jinja2", message=tb)
        return render_template("redirect_back.html.jinja2")
    return abort(500)


@bp.route("/team/<team_name>")
@login_required
def team_info(team_name: str = ""):
    """A page showing team info & score tally"""
    # Look-up the team:
    team = Team.find_by_name(team_name)
    if team is None:
        return abort(400)
    # Generate data table:
    table = AdminDataTable([])
    if request.args.get("ajax") == "true":
        # order[0][column]=0&order[0][dir]=desc&start=0&length=5
        results = parse_query(
            DataPoint,
            table._cols,
            request.args,
            filter={"team_reference": ObjectId(team.id)},
        )
        data = [
            [c.td_contents(item, [attr]) for attr, c in table._cols.items() if c.show]
            for item in results
        ]
        count = len(DataPoint.find())
        return {
            "draw": int(request.args.get("draw", 0)) + 1,
            "recordsTotal": count,
            "recordsFiltered": count,
            "data": data,
        }
    else:
        # Multiplier editing form:
        form = MultiplierForm()
        form.team_id.data = str(team._id)
        # form.size.data = team.multiplier.vol_mult.amt
        # form.cost.data = team.multiplier.cost_mult.amt
        form.mass.data = team.multiplier.mass_mult.amt
        # Render the template
        return render_template(
            "team_edit.html.jinja2",
            team=team,
            table=table.__html__(),
            mult_form=form,
            emails=base64.urlsafe_b64encode(", ".join(team.emails).encode()),
        )


@bp.route("/multiplier", methods=["POST"])
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
                # CostMultiplier(team.weight_class, form.cost.data),
                MassMultiplier(team.weight_class, form.mass.data)
                # VolumeMultiplier(team.weight_class,
                #    VolumeUnit(SIZE_NAME_MAPPING[form.size.data])
                # )
            )
            team.save()
        except:
            tb = traceback.format_exc()
            logging.error(tb)
            return render_template("errorpages/500.html.jinja2", message=tb)
        return render_template("redirect_back.html.jinja2")
    return abort(500)


@bp.route(
    "/mail",
    methods=["GET", "POST"],
    defaults={"recipients": base64.urlsafe_b64encode(b"")},
)
@bp.route("/mail/<recipients>", methods=["GET", "POST"])
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
            form.to.data.replace(" ", "").split(","),
            form.subject.data,
            form.message.data,
        )
        if msg.send():
            flash("Email Sent!")
        else:
            flash("Sending failed.", category="error")
        return render_template("redirect_back.html.jinja2")
    form.to.data = base64.urlsafe_b64decode(recipients).decode()
    return render_template("sendmail.html.jinja2", mail_form=form)


@bp.route("/sent-messages", defaults={"teamid": None})
@bp.route("/sent-messages/<teamid>")
@login_required
def sent_email(teamid):
    """Shows a page with all sent emails"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    messages = Message.find() if teamid is None else Message.find_by_team(teamid)
    table = AdminEmailTable(messages)
    # Render the template:
    return render_template("email_table.html.jinja2", table=table.__html__())


@bp.route("/beaconnow", methods=["POST"])
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
                instant=form.instant.data,
                division=TeamLevel(form.division.data),
                message=form.message.data,
                destination=OutputDestination(form.destination.data),
                encoding=BeaconMessageEncoding(form.msg_format.data),
                misfire_grace=form.misfire_grace.data,
                intensity=form.intensity.data,
            )
            msg.save()
        except:
            tb = traceback.format_exc()
            logging.error(tb)
            return render_template("errorpages/500.html.jinja2", message=tb)
        return render_template("beacon_tx_done.html.jinja2")
    flash("Invalid input.", category="danger")
    return abort(500)


@bp.route("/beacontable")
@login_required
def beacon_table():
    """Renders a table with all beacon messages"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    table = BeaconMessageTable(BeaconMessage.find())

    beacon_form = ImmediateBeaconForm()
    beacon_form.instant.data = datetime.now()

    return render_template(
        "beacon_table.html.jinja2",
        beacon_table=table.__html__(),
        beacon_form=beacon_form,
        current_time=str(datetime.now()),
    )


@bp.route("/db-repair/<mode>/<collection_name>/<query>", methods=["GET", "POST"])
@login_required
def database_repair(mode="", collection_name="", query="{}"):
    """Allows repairing a database with some broken stuff in it"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    if mode not in ["all", "broken", "safe"]:
        flash("Valid modes are `all`, `safe`, or `broken`.")
        return abort(500)
    if collection_name not in __STR_COLLECTION_MAPPING:
        flash(f'Invalid Collection Name "{collection}".')
        return abort(500)
    logging.warn("Opening Database Repair Tool.")

    collection = __STR_COLLECTION_MAPPING[collection_name]

    class BrokenDocId:
        """Represents a broken document to be put into the table"""

        def __init__(self, id: str, repr_str: str):
            self.id = id
            self.id_secondary = id
            self.repr_str = repr_str

    class BrokenDocTable(Table):
        """Allows a group of BeaconMessage objects to be displayed in an HTML table"""

        def __init_subclass__(cls, model_type: str = "") -> None:
            cls.id_secondary = OptionsCol("Delete", model_type=model_type)
            return super().__init_subclass__()

        allow_sort = False  # Let's avoid flask-table's built-in sorting
        classes = ["table", "table-striped", "datatable", "display"]
        thead_classes = ["thead-dark"]
        border = True

        id = PreCol("Document ID")
        repr_str = PreCol("Representation")
        id_secondary = OptionsCol("Delete", model_type=collection_name)

        def __init__(self, items: List[Encodable], **kwargs):
            """Initializes the table"""
            super().__init__(items, **kwargs)

        def sort_url(self, col_id, reverse=False):
            pass
            # return url_for(self._endpoint, sort=col_id,
            #               direction='desc' if reverse else 'asc')

    # Define an exemplary object, based on the default kwargs of the constructor
    good_doc = collection()

    # Load up anything that matches the query
    all_docs = collection.find(loads(query))

    broken: List[BrokenDocId] = []
    # Iterate through and figure out which ones are broken
    #     What counts as broken?
    #         If the type of a field does not match that of the same field
    #         in the exemplary `good_doc`, something is wrong, likely remnants
    #         from a previous, database-incompatible version of CubeServer.
    for doc in all_docs:
        logging.debug(f"Opening Document ID {doc.id}...")
        if mode == "all":
            broken.append(BrokenDocId(doc.id, pformat(doc.encode(), indent=4)))
            continue
        elif mode == "safe":
            broken.append(BrokenDocId(doc.id, "[OPENED IN SAFE MODE; NO DATA SHOWN]"))
            continue
        for field_name in doc._fields:
            example = good_doc.__getattribute__(field_name)
            experiment = doc.__getattribute__(field_name)
            logging.debug(field_name, example, experiment)
            if type(example) != type(experiment):
                broken.append(BrokenDocId(doc.id, pformat(doc.encode(), indent=4)))
                logging.warn(f"Document {doc.id} is broken-")
                logging.info(
                    f"\tField {field_name} is type {type(experiment)} instead of {type(example)}"
                )
                break

    table = BrokenDocTable(broken)

    return render_template(
        "db_repair_tool.html.jinja2",
        displaymode=mode.title(),
        collection=collection_name,
        brokendoc_table=table.__html__(),
        exampledoc=pformat(good_doc.encode(), indent=4),
    )


@bp.route("/db-gen-reserved/<name>", methods=["GET"])
@login_required
def gen_reserved(name: str = ""):
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    if name == "":
        flash("No team specified")
        return abort(500)
    if Team.find_by_name(name) is not None:
        flash(f"Please delete `{name}` before regenerating.")
        return render_template("redirect_back.html.jinja2")

    team = Team(
        name=name,
        weight_class=TeamLevel.REFERENCE,
        status=TeamStatus.INTERNAL,
        _secret_length=INTERNAL_SECRET_LENGTH,
    )
    team.save()
    flash(f"Successfully created reserved team {name} ({team.id})", category="success")
    return render_template("redirect_back.html.jinja2")


@bp.route("/referencetest/<station_id>")
@login_required
def referencetest(station_id: str | int = ""):
    """Tests reference stations"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    try:
        # request = ref_protocol.ReferenceRequest(
        #     id = int(station_id).to_bytes(1, 'big'),
        #     signal=ref_protocol.ReferenceSignal.ENQ,
        #     command=ref_protocol.ReferenceCommand.MEAS,
        #     param=ref_protocol.MeasurementType.TEMP.value
        # )
        # with DispatcherClient() as client:
        #     response = client.request(request)
        # if response is None:
        return render_template(
            "errorpages/500.html.jinja2", message="No response received"
        )
        # return render_template(
        #     'reference_test.html.jinja2',
        #     request_pre = pformat(request.dump(), indent=4),
        #     response_pre = pformat(response.dump(), indent=4)
        # )
    except:
        tb = traceback.format_exc()
        logging.error(tb)
        return render_template("errorpages/500.html.jinja2", message=tb)


@bp.route("/referencepttest/<window>")
@login_required
def referencepttest(window: str | int = ""):
    """Tests reference stations"""
    # Check admin status:
    if current_user.level != UserLevel.ADMIN:
        return abort(403)
    try:
        refpt = Reference.get_window_point(int(window))
        if refpt is None:
            return render_template(
                "errorpages/500.html.jinja2", message="No response received"
            )
        return render_template(
            "reference_test.html.jinja2",
            request_pre="yah",
            response_pre=refpt.__str__(),
        )
    except:
        tb = traceback.format_exc()
        logging.error(tb)
        return render_template("errorpages/500.html.jinja2", message=tb)
