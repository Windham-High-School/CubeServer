import os
from flask import Flask
from flask_pymongo import PyMongo

import config

# Configure application:
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder="templates")

# Configure MongoDB:
app.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']
mongo = PyMongo(app)

# Load configuration:
app.config['CONSTANTS'] = config
app.config['REGISTRATION_OPEN'] = False  # TODO: Load config from database

# Configure blueprints:
from .blueprints import home, admin, team
app.register_blueprint(home.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(team.bp)

from app import views