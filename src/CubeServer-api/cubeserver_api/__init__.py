"""An API for logging data into the database.
"""
from os import environ
import logging

from flask import Flask
from flask_restful import Api
from flask_apscheduler import APScheduler

from cubeserver_common import configure_db, config, init_logging
from cubeserver_common.gensecret import check_secrets
from ._version import *

# Init logger:
init_logging()

# Create app:
logging.debug("Initializing Flask app")
app = Flask(__name__)
app.config['CONSTANTS'] = config


if all(key in environ for key in [
    'MONGODB_USERNAME',
    'MONGODB_PASSWORD',
    'MONGODB_HOSTNAME',
    'MONGODB_DATABASE'
]): # If we aren't in the docker container or cannot see the db credentials...\
    app.config['SECRET_KEY'] = check_secrets()
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
    @scheduler.task('cron', id='email_cont_reset', hour=str(Conf.retrieve_instance().quota_reset_hour))
    def reset_email_count():
        logging.debug("Resetting sent_emails counters")
        Team.reset_sent_emails()
    logging.debug("Starting scheduler")
    scheduler.start()

    # Import after init'ing the db:
    logging.debug("Loading api resources")
    from cubeserver_api.resources import Data, Status, Email, CodeUpdate

    # Attach resources:
    logging.debug("Attaching api resources")
    api.add_resource(Data, '/data')  # TODO: Use as decorators?
    api.add_resource(Status, '/status')
    api.add_resource(Email, '/email')
    api.add_resource(CodeUpdate, '/update')
    #api.add_resource(BeaconMessages, '/test')  # A dummy api endpoint for db testing
else:
    logging.warn("API NOT INITIALIZED! (okay if this is a docs build)")
