"""Classes common to both the API and the app"""

import os
import logging

from flask_pymongo import PyMongo
from pymongo import MongoClient
from cubeserver_common.models import PyMongoModel
from . import config

from cubeserver_common.config import EnvConfig

# Init environ.py and run validation
EnvConfig.validate()


def init_logging():
    """Init logger"""
    logging.basicConfig(format=config.LOGGING_FORMAT, level=config.LOGGING_LEVEL)
    logging.log(
        100, f"CubeServer loglevel is {logging.getLevelName(config.LOGGING_LEVEL)}"
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
    from cubeserver_common.models.config.conf import Conf
    from cubeserver_common.models.config.rules import Rules

    if Rules.retrieve_instance() is None:
        default_ruleset = Rules()
        default_ruleset.save()
    if Conf.retrieve_instance() is None:
        default_confset = Conf()
        default_confset.save()
