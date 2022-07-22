"""An API for logging data into the database.
"""

from flask import Flask
from flask_restful import Resource, Api

from cubeserver_api.resources import Data
from ._version import *

# Create app:
app = Flask(__name__)
api = Api(app)

# Attach resources:
api.add_resource(Data, '/data')
