"""A web application for software to manage, store, score,
and publish data received from Wifi-equipped microcontrollers for a school contest"""

import logging

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_apscheduler import APScheduler

from cubeserver_common.environ import EnvConfig
from cubeserver_common import config, init_logging, configure_db
from cubeserver_common.models import PyMongoModel
from cubeserver_common.gensecret import check_secrets
from cubeserver_common.config import LOGGING_LEVEL

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


logging.debug("Initializing APScheduler")
scheduler = APScheduler()
# Make APScheduler a little quieter:
logging.getLogger("apscheduler.executors.default").setLevel(LOGGING_LEVEL + 10)

scheduler.add_job(
    func=_update_conf, args=[app], trigger="interval", id="configsync", seconds=30
)
scheduler.add_job(
    func=clear_bad_attempts, trigger="interval", id="clearbadattempts", seconds=30
)
scheduler.start()
logging.debug("Starting scheduler")

_update_conf(app)

# Load SECRET_KEY:
app.config["SECRET_KEY"] = EnvConfig.CS_FLASK_SECRET

# Login Manager:
logging.debug("Initializing login manager")
login_manager = LoginManager()
login_manager.init_app(app)
