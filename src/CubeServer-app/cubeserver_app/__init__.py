"""A web application for software to manage, store, score,
and publish data received from Wifi-equipped microcontrollers for a school contest"""

from os import environ
import os.path
import logging

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_apscheduler import APScheduler

from cubeserver_common import config, init_logging, configure_db
from cubeserver_common.models import PyMongoModel
from cubeserver_common.gensecret import check_secrets
from cubeserver_common.config import LOGGING_LEVEL
from cubeserver_app.command import register_commands

from ._version import *

# Init logger:
init_logging()

# Configure application:
logging.debug("Initializing Flask app")
app = Flask(
    __name__, static_url_path="", static_folder="static", template_folder="templates"
)

# Load configuration:
app.config["CONSTANTS"] = config

# Bootstrap:
Bootstrap(app)

if not all(
    key in environ
    for key in [
        "MONGODB_USERNAME",
        "MONGODB_PASSWORD",
        "MONGODB_HOSTNAME",
        "MONGODB_DATABASE",
    ]
):  # If we aren't in the docker container or cannot see the db credentials...
    # Put a non-None placeholder ... in for the client:
    logging.warn("APP NOT INITIALIZED! (okay if this is a docs build)")
    PyMongoModel.update_mongo_client(...)
else:
    # Configure MongoDB:
    logging.debug("Initializing db connection")
    configure_db(app)

    # Import models ONLY AFTER the db is configured:
    from cubeserver_common.models.user import clear_bad_attempts
    from cubeserver_common.models.config.conf import Conf

    def _update_conf(app):
        """An update job scheduled to run every 30 seconds
        This retrieves the latest configuration to ensure that any changes
        are synced between server threads."""
        logging.debug("Updating configuration variables from db")
        app.config["CONFIGURABLE"] = Conf.retrieve_instance()

    if False:
        logging.debug("Initializing APScheduler")
        scheduler = APScheduler()
        # Make APScheduler a little quieter:
        logging.getLogger("apscheduler.executors.default").setLevel(LOGGING_LEVEL + 10)

        scheduler.add_job(
            func=_update_conf,
            args=[app],
            trigger="interval",
            id="configsync",
            seconds=30,
        )
        scheduler.add_job(
            func=clear_bad_attempts,
            trigger="interval",
            id="clearbadattempts",
            seconds=30,
        )
        scheduler.start()
        logging.debug("Starting scheduler")

    _update_conf(app)

    # Load SECRET_KEY:
    # Double-check that the secret_file is actually there...
    app.config["SECRET_KEY"] = check_secrets()

    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 86400 * 365
    app.config["STATIC_VERSION"] = environ.get("STATIC_VERSION")

    @app.url_defaults
    def static_cache_buster(endpoint, values):
        if "." in endpoint and "filename" in values:
            (bp_name, vf_name) = endpoint.rsplit(".", 1)
        else:
            (bp_name, vf_name) = (None, endpoint)

        if vf_name == "static":
            if values["filename"][0] == "/":
                values["filename"] = values["filename"][1:]

            if app.config["STATIC_VERSION"]:
                values["_"] = app.config["STATIC_VERSION"]
            else:
                if bp_name:
                    abs_filename = os.path.join(
                        app.blueprints[bp_name].static_folder, values["filename"]
                    )
                else:
                    abs_filename = os.path.join(app.static_folder, values["filename"])
                values["_"] = os.path.getmtime(abs_filename)

    register_commands(app)


# Login Manager:
logging.debug("Initializing login manager")
login_manager = LoginManager()
login_manager.init_app(app)
