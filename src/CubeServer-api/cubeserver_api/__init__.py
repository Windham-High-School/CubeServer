"""An API for logging data into the database.

This module is also the uWSGI endpoint for the api
"""

from flask import Flask
from flask_restful import Api
from flask_apscheduler import APScheduler
from loguru import logger

from cubeserver_common.config import EnvConfig, DynamicConfig
from cubeserver_common import configure_db, init_logging

# Init logger:
init_logging()

# Create app:
logger.info("Initializing Flask")
app = Flask(__name__)

app.config["SECRET_KEY"] = EnvConfig.CS_FLASK_SECRET
logger.info("Initializing Flask-Restful Api")
api = Api(app)

logger.info("Initializing db connection")
configure_db(app)

# Email quota counting:
from cubeserver_common.models.team import Team

logger.info("Initializing APScheduler")
scheduler = APScheduler()
scheduler.init_app(app)


@scheduler.task(
    "cron",
    id="email_cont_reset",
    hour=str(DynamicConfig["Email"]["Team Quota Reset Hour"]),
)
def reset_email_count():
    logger.debug("Resetting sent_emails counters")
    Team.reset_sent_emails()


logger.info("Starting scheduler")
scheduler.start()

# Import AFTER init'ing the db:
logger.info("Loading api resources")
logger.debug("Loading team api resources")
from cubeserver_api.resources.team_resources import *

logger.debug("Loading beacon api resources")
from cubeserver_api.resources.beacon_resources import *

# Attach resources:
logger.debug("Attaching team api resources")
api.add_resource(Data, "/data")  # TODO: Use as decorators?
api.add_resource(Status, "/status")
api.add_resource(Email, "/email")
api.add_resource(CodeUpdate, "/update")
# api.add_resource(BeaconMessages, '/test')  # A dummy api endpoint for db testing

logger.debug("Attaching beacon api resources")
api.add_resource(NextMessage, "/beacon/message/next_queued")
api.add_resource(Message, "/beacon/message/<string:message_id>")
