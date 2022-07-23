"""A web application for software to manage, store, score,
and publish data received from Wifi-equipped microcontrollers for a school contest"""

import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from cubeserver_common import config
from cubeserver_common.models import PyMongoModel
from cubeserver_common.gensecret import check_secrets

from ._version import *

# Configure application:
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder="templates")

# Bootstrap:
Bootstrap(app)

# Configure MongoDB:
app.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] \
    + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] \
        + ':27017/' + os.environ['MONGODB_DATABASE'] + '?authSource=admin'
mongo = PyMongo(app)
PyMongoModel.update_mongo_client(mongo)

# Load configuration:
app.config['CONSTANTS'] = config
app.config['REGISTRATION_OPEN'] = True  # TODO: Load config from database

# Load SECRET_KEY:
# Double-check that the secret_file is actually there...
app.config['SECRET_KEY'] = check_secrets()

# Login Manager:
login_manager = LoginManager()
login_manager.init_app(app)
