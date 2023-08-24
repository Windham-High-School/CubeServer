"""A web application for software to manage, store, score,
and publish data received from Wifi-equipped microcontrollers for a school contest

This module is also the uWSGI endpoint for the web app
"""

import logging

from loguru import logger
from flask import Flask, redirect, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_url
from flask_apscheduler import APScheduler

from cubeserver_common.config import EnvConfig
from cubeserver_common import init_logging, configure_db

# Init logger:
init_logging()

# Configure application:
logger.info("Initializing Flask app")
app = Flask(
    __name__,
    static_url_path="",
    static_folder="static",
    template_folder="root_templates",
)

# Load SECRET_KEY:
app.config["SECRET_KEY"] = EnvConfig.CS_FLASK_SECRET

# Bootstrap:
Bootstrap(app)

# Configure MongoDB:
logger.info("Initializing db connection")
configure_db(app)

# Import models ONLY AFTER the db is configured:
from cubeserver_common.models.user import User, clear_bad_attempts
from cubeserver_common.config import DynamicConfig

from .pages import register_all as register_blueprints
from .errorviews import register_all as register_errorviews


def _update_conf(app):
    """An update job scheduled to run every 30 seconds
    This retrieves the latest configuration to ensure that any changes
    are synced between server threads."""
    logger.debug("Updating configuration variables from db")
    DynamicConfig.reload()
    app.config["CONFIGURABLE"] = DynamicConfig.copy()

# Scheduler
logger.info("Initializing APScheduler")
scheduler = APScheduler()
logging.getLogger("apscheduler.executors.default").setLevel(EnvConfig.CS_LOGLEVEL)

scheduler.add_job(
    func=_update_conf, args=[app], trigger="interval", id="configsync", seconds=30
)
scheduler.add_job(
    func=clear_bad_attempts, trigger="interval", id="clearbadattempts", seconds=30
)
scheduler.start()
logger.info("Started scheduler")

logger.debug("Initial dynamic config load...")
_update_conf(app)

# Login Manager:
logger.info("Initializing login manager")
login_manager = LoginManager()
login_manager.session_protection = (
    "strong"  # Invalidate session on user agent or ip change
)
login_manager.user_loader(User.loader)
login_manager.init_app(app)

@login_manager.unauthorized_handler
def login_unauthorized():
    """Redirects the user to a login screen"""
    logger.debug(f"Unauthorized request to {request.url}; redirecting to login")
    return redirect(login_url("home.login", next_url=request.url))

# Error handlers:
# TODO: Setup with something like Sentry
logger.info("Registering error handlers")
register_errorviews(app)

# Blueprints:
logger.info("Registering blueprints")
register_blueprints(app)
