"""An API for logging data into the database.
"""
from os import environ

from flask import Flask
from flask_restful import Api
from flask_apscheduler import APScheduler

from cubeserver_common import configure_db, config
from cubeserver_common.gensecret import check_secrets
from ._version import *

# Create app:
app = Flask(__name__)
app.config['CONSTANTS'] = config


if all(key in environ for key in [
    'MONGODB_USERNAME',
    'MONGODB_PASSWORD',
    'MONGODB_HOSTNAME',
    'MONGODB_DATABASE'
]): # If we aren't in the docker container or cannot see the db credentials...\
    app.config['SECRET_KEY'] = check_secrets()
    api = Api(app)

    configure_db(app)

    # Email quota counting:
    from cubeserver_common.models.team import Team
    from cubeserver_common.models.config.conf import Conf
    scheduler = APScheduler()
    scheduler.add_job(
        Team.reset_sent_emails,
        'cron', hour=Conf.retrieve_instance().quota_reset_hour
    )
    scheduler.start()

    # Attach resources:
    from cubeserver_api.resources import Data, Status, Email  # Import after init'ing the db
    api.add_resource(Data, '/data')
    api.add_resource(Status, '/status')
    api.add_resource(Email, '/email')
