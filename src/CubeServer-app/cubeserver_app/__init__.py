"""A web application for software to manage, store, score,
and publish data received from Wifi-equipped microcontrollers for a school contest"""

from os import environ

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_apscheduler import APScheduler

from cubeserver_common import config
from cubeserver_common.models import PyMongoModel
from cubeserver_common.gensecret import check_secrets
from cubeserver_common import configure_db

from ._version import *

# Configure application:
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder="templates")

# Load configuration:
app.config['CONSTANTS'] = config

# Bootstrap:
Bootstrap(app)

if not all(key in environ for key in [
    'MONGODB_USERNAME',
    'MONGODB_PASSWORD',
    'MONGODB_HOSTNAME',
    'MONGODB_DATABASE'
]): # If we aren't in the docker container or cannot see the db credentials...
    # Put a non-None placeholder ... in for the client:
    PyMongoModel.update_mongo_client(...)
else:
    # Configure MongoDB:
    configure_db(app)

    # Import models ONLY AFTER the db is configured:
    from cubeserver_common.models.user import clear_bad_attempts
    from cubeserver_common.models.config.conf import Conf

    def _update_conf(app):
        """An update job scheduled to run every 30 seconds
        This retrieves the latest configuration to ensure that any changes
        are synced between server threads."""
        app.config['CONFIGURABLE'] = Conf.retrieve_instance()

    scheduler = APScheduler()
    scheduler.add_job(func=_update_conf, args=[app], trigger='interval', id='configsync', seconds=30)
    scheduler.add_job(func=clear_bad_attempts, trigger='interval', id='clearbadattempts', seconds=30)
    scheduler.start()

    _update_conf(app)

    # Load SECRET_KEY:
    # Double-check that the secret_file is actually there...
    app.config['SECRET_KEY'] = check_secrets()

# Login Manager:
login_manager = LoginManager()
login_manager.init_app(app)
