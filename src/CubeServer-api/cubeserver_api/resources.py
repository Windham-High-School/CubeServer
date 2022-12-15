"""This package contains the resource classes for the api
"""

from datetime import datetime
from time import time

from flask import request
from flask_restful import Resource
from flask_httpauth import HTTPBasicAuth
from json import dumps, loads, decoder

from cubeserver_common.models.config.rules import Rules
from cubeserver_common.models.team import Team
from cubeserver_common.models.datapoint import DataClass, DataPoint

auth = HTTPBasicAuth()

@auth.get_password
def get_team_secret(team_name: str) -> str:
    """Returns the secret code of a team by name
    (The digest username is the team name)"""
    team = Team.find_by_name(team_name)
    print(f"Request from {team_name}")
    if team and team.status.is_active:
        return team.secret
    return None

class Data(Resource):
    """A POST-only resource for datapoints"""

    decorators = [auth.login_required]

    def post(self):
        team = Team.find_by_name(auth.username())
        print(f"Data submission from: {team.name}")
        # Get DataClass and cast the value:
        data_str = request.get_json()
        if data_str is None:
            data_str = loads(request.form['data'])
        print(data_str)
        data_class = DataClass(data_str['type'])
        if data_class in DataClass.manual:
            return request.form, 400  # If this should be manually-determined..
        data_value = data_class.datatype(data_str['value'])
        # Create the DataPoint object:
        point = DataPoint(
            team_identifier=team.id,
            category=data_class,
            value=data_value
        )
        print(point)
        print("Posting data...")
        if Rules.retrieve_instance().post_data(team, point):
            return request.form, 201
        return request.form, 400  # TODO: Support better response codes?

class Status(Resource):
    """A resource with some basic info"""

    decorators = [auth.login_required]

    def get(self):
        team = Team.find_by_name(auth.username())
        return {
            "datetime": datetime.now().isoformat(),
            "unix_time": int(time()),
            "status": {"score": team.score, "strikes": team.strikes}
        }, 200
