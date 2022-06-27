"""A web application for software to manage, store, score,
and publish data received from Wifi-equipped microcontrollers for a school contest"""

import os
from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap

from .gensecret import check_secrets
from . import config

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

# Load configuration:
app.config['CONSTANTS'] = config
app.config['REGISTRATION_OPEN'] = True  # TODO: Load config from database

# Load SECRET_KEY:
check_secrets() # Double-check that the secret_file is actually there...
with open(config.SECRET_KEY_FILE, "r", encoding=config.SECRET_KEY_FILE_ENCODING) as secret_file:
    app.config['SECRET_KEY'] = secret_file.read()
