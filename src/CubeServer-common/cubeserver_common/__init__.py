"""Classes common to both the API and the app"""

import os
from flask_pymongo import PyMongo
from pymongo import MongoClient
from cubeserver_common.models import PyMongoModel


def configure_db(app=None):
    """Configures the database"""
    # Configure MongoDB:
    uri = 'mongodb://' + os.environ['MONGODB_USERNAME'] \
        + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] \
            + ':27017/' + os.environ['MONGODB_DATABASE'] + '?authSource=admin'
    if app is not None:
        app.config["MONGO_URI"] = uri
        mongo = PyMongo(app, uri=uri)
    else:
        mongo = PyMongo(uri=uri)
        mongo.cx = MongoClient(uri)
        mongo.db = mongo.cx[os.environ['MONGODB_DATABASE']]
    print(f"\n\n\tMONGO: {mongo}\n\n")
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
