"""An API for logging data into the database.
"""

from flask import Flask
from flask_restful import Api

from cubeserver_common import configure_db, config
from cubeserver_common.gensecret import check_secrets
from ._version import *

# Create app:
app = Flask(__name__)
app.config['SECRET_KEY'] = check_secrets()
app.config['CONSTANTS'] = config

api = Api(app)

configure_db(app)

# Attach resources:

from cubeserver_api.resources import Data, Status  # Import after init'ing the db
api.add_resource(Data, '/data')
api.add_resource(Status, '/status')
