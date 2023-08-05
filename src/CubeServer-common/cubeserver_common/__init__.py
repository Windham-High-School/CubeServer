"""Classes common to both the API and the app"""

import os
from flask_pymongo import PyMongo
from pymongo import MongoClient
from cubeserver_common.models import PyMongoModel
import logging
from . import config

def init_logging():
    """Init logger"""
    logging.basicConfig(format=config.LOGGING_FORMAT, level=config.LOGGING_LEVEL)
    logging.log(100, f"CubeServer loglevel is {logging.getLevelName(config.LOGGING_LEVEL)}")

def configure_db(app=None):
    """Configures the database"""
    # Configure MongoDB:

    driver = os.environ.get('MONGODB_DRIVER', 'mongodb')
    port = '' if '+srv' in driver else ':27017/' 

    uri = driver + '://' + os.environ['MONGODB_USERNAME'] \
        + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] \
            + port + os.environ['MONGODB_DATABASE'] + '?authSource=admin'
    if app is not None:
        app.config["MONGO_URI"] = uri
        mongo = PyMongo(app, uri=uri)
    else:
        mongo = PyMongo(uri=uri)
        mongo.cx = MongoClient(uri)
        mongo.db = mongo.cx[os.environ['MONGODB_DATABASE']]
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
