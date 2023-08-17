"""An API for logging data into the database.
"""
import logging

from flask import Flask
from flask_restful import Api
from flask_apscheduler import APScheduler

from cubeserver_common.config import EnvConfig
from cubeserver_common import configure_db, init_logging

# Init logger:
init_logging()

# Create app:
logging.debug("Initializing Flask app")
app = Flask(__name__)

app.config["SECRET_KEY"] = EnvConfig.CS_FLASK_SECRET
logging.debug("Initializing Flask-Restful Api")
api = Api(app)

logging.debug("Initializing db connection")
configure_db(app)

# Email quota counting:
from cubeserver_common.models.team import Team
from cubeserver_common.models.config.conf import Conf

logging.debug("Initializing APScheduler")
scheduler = APScheduler()
scheduler.init_app(app)


@scheduler.task(
    "cron",
    id="email_cont_reset",
    hour=str(Conf.retrieve_instance().quota_reset_hour),
)
def reset_email_count():
    logging.debug("Resetting sent_emails counters")
    Team.reset_sent_emails()


logging.debug("Starting scheduler")
scheduler.start()

# Import after init'ing the db:
logging.debug("Loading team api resources")
from cubeserver_api.team_resources import Data, Status, Email, CodeUpdate

logging.debug("Loading beacon api resources")
from cubeserver_api.beacon_resources import NextMessage, Message

# Attach resources:
logging.debug("Attaching team api resources")
api.add_resource(Data, "/data")  # TODO: Use as decorators?
api.add_resource(Status, "/status")
api.add_resource(Email, "/email")
api.add_resource(CodeUpdate, "/update")
# api.add_resource(BeaconMessages, '/test')  # A dummy api endpoint for db testing

logging.debug("Attaching beacon api resources")
api.add_resource(NextMessage, "/beacon/message/next_queued")
api.add_resource(Message, "/beacon/message/<string:message_id>")
