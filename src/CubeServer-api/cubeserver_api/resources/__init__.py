"""This package contains the resource classes for the api
"""

from flask import request
from flask_restful import Resource

class Data(Resource):
    """A POST-only resource for datapoints"""

    DATA_TYPES = {  # TODO: Update data types for any possible datapoints
        "temperature": float,
        "humidity": float,
        "pressure": float,
        "light_intensity": float,
        "comment": str
    }
    """Defines the types of parameters used to post data"""

    def post(self):
        print(f"POSTing data {request.form}.")
        return request.form, 201

