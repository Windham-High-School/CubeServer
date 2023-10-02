"""Classes common to both the API and the app"""

from flask_pymongo import PyMongo
import mongomock
from pymongo import MongoClient
from cubeserver_common.models import PyMongoModel
from loguru import logger

from cubeserver_common.config import EnvConfig, EnvConfigError
from .log import *

logger.debug("Initializing cubeserver_common")
init_logging()

# Init environ.py and run validation
try:
    EnvConfig.validate()
    logger.debug("Environment variable configuration is valid")
except EnvConfigError:
    logger.error("Environment variable configuration is invalid")
    raise


def configure_db(app=None):
    """Configures the database"""
    # Configure MongoDB:

    driver = EnvConfig.CS_MONGODB_DRIVER
    port_num = EnvConfig.CS_MONGODB_PORT
    port = "/" if port_num is None else f":{port_num}/"
    extra = "" if "+srv" in driver else ""
    options = EnvConfig.CS_MONGODB_OPTIONS

    uri = (
        driver
        + "://"
        + EnvConfig.CS_MONGODB_USERNAME
        + ":"
        + EnvConfig.CS_MONGODB_PASSWORD
        + "@"
        + EnvConfig.CS_MONGODB_HOST
        + port
        + EnvConfig.CS_MONGODB_DATABASE
        + extra
        + "?"
        + options
    )
    if "mock" in driver:
        logger.debug(f"Mocking database with MongoMock")
        mongo = mongomock.MongoClient()
    elif app is not None:
        logger.debug(f"Connecting to database {uri} with Flask-PyMongo")
        app.config["MONGO_URI"] = uri
        mongo = PyMongo(app, uri=uri)
    else:
        logger.debug(f"Connecting to database {uri} with PyMongo")
        mongo = PyMongo(uri=uri)
        mongo.cx = MongoClient(uri)
        mongo.db = mongo.cx[EnvConfig.CS_MONGODB_DATABASE]

    logger.debug("Installing static reference to mongo client")
    PyMongoModel.update_mongo_client(mongo)

    # Don't let the model classes load until after the db is init'd:
    from cubeserver_common.models.config.rules import Rules
    from cubeserver_common.models.user import User, UserLevel

    # TODO: Get rid of Rules class and rewrite scoring, etc
    if Rules.retrieve_instance() is None:
        default_ruleset = Rules()
        default_ruleset.save()
        logger.info("Hardcoded-default ruleset saved")

    # Make sure there is a default admin user if the database is empty:
    if len(User.find()) == 0:  # The database is newly initialized:
        default_user = User(level=UserLevel.ADMIN)
        default_user.activate(
            EnvConfig.CS_DEFAULT_ADMIN_USER, "", EnvConfig.CS_DEFAULT_ADMIN_PASS
        )
        default_user.save()
        logger.warn("Admin user with default credentials created in the database")
