"""Classes common to both the API and the app"""

import logging

from flask_pymongo import PyMongo
from pymongo import MongoClient
from cubeserver_common.models import PyMongoModel

from cubeserver_common.config import EnvConfig, DynamicConfig

# Init environ.py and run validation
EnvConfig.validate()


def init_logging():
    """Init logger"""
    logging.basicConfig(format=EnvConfig.CS_LOGFORMAT, level=EnvConfig.CS_LOGLEVEL)
    logging.log(
        100, f"CubeServer loglevel is {logging.getLevelName(EnvConfig.CS_LOGLEVEL)}"
    )


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
    if app is not None:
        app.config["MONGO_URI"] = uri
        mongo = PyMongo(app, uri=uri)
    else:
        mongo = PyMongo(uri=uri)
        mongo.cx = MongoClient(uri)
        mongo.db = mongo.cx[EnvConfig.CS_MONGODB_DATABASE]
    PyMongoModel.update_mongo_client(mongo)

    # Don't let the model classes load until after the db is init'd:
    from cubeserver_common.models.config.rules import Rules
    from cubeserver_common.models.user import User, UserLevel

    # TODO: Get rid of Rules class and rewrite scoring, etc
    if Rules.retrieve_instance() is None:
        default_ruleset = Rules()
        default_ruleset.save()

    # Make sure there is a default admin user if the database is empty:
    if len(User.find()) == 0:  # The database is newly initialized:
        default_user = User(level=UserLevel.ADMIN)
        default_user.activate(
            EnvConfig.CS_DEFAULT_ADMIN_USER, "", EnvConfig.CS_DEFAULT_ADMIN_PASS
        )
        default_user.save()
