"""This package contains the resource classes for the api used by the beacon
"""

from datetime import datetime
from time import time
import logging

from flask import request
from flask_restful import Resource
from flask_httpauth import HTTPBasicAuth
from json import dumps, loads, decoder
from base64 import encodebytes

from cubeserver_common.models.config.rules import Rules
from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.team import Team, TeamStatus
from cubeserver_common.models.beaconmessage import BeaconMessage, SentStatus
from cubeserver_common.models.datapoint import DataClass, DataPoint
from cubeserver_common import config
from cubeserver_common.metadata import VERSION

auth = HTTPBasicAuth()

def internal(func: callable) -> callable:
    """A decorator for internal resource functions
    """
    def wrapper(*args, **kwargs):
        team: Team = Team.find_by_name(auth.username())
        if team.status != TeamStatus.INTERNAL:
            # Abort due to unauthorized access
            logging.info(f"Unauthorized access attempt to internal resource by {team.name}")
            return None, 401
        return func(*args, **kwargs)
    return wrapper

@auth.get_password
def get_team_secret(team_name: str) -> str:
    """Returns the secret code of a team by name
    (The digest username is the team name)"""
    team = Team.find_by_name(team_name)
    logging.debug(f"Request from {team_name}")
    if team and team.status.is_active:
        return team.secret
    return None



class NextMessage(Resource):
    """
    For the beacon API, a GET request to /beacon/message/next_queued with proper credentials should yield a json response along the lines of
    {"id": <hex string representing the object id>, "timestamp": <epoch timestamp as a decimal>, "offset": <seconds from request until instant>, "destination": <"Infrared"|"Visible">, "intensity": <8-bit integer>, "message": <the message as a UTF-8 str>}
    I think the message for the purposes of simplicity in the short term can be conveyed as a string but this might be changed in the long term for sending other data over the beacon.
    Other than the timestamp and offset, the other items are the same values as what would be transferred by the command system.
    The response will only have information for the next soonest beacon message that has the status of "queued" in the database. 
    """

    decorators = [auth.login_required]

    @internal
    def get(self):
        logging.debug(f"Next message get req from {auth.username()}")
        team: Team = Team.find_by_name(auth.username())
        # data_str = request.get_json()
        # logging.debug(f"Request: {data_str}")
        # if data_str is None:
        #     data_str = loads(request.form['data'])

        message: BeaconMessage = BeaconMessage.find_one_queued()
        if message is None:
            return None, 404

        return {
            "id": str(message.id),
            "timestamp": message.send_at.timestamp(),
            "offset": (datetime.now() - message.send_at).total_seconds(),
            "destination": message.destination.value,
            "intensity": message.intensity,
            "message": message.full_message_bytes.decode('utf-8'),
            "status": message.status.value
        }, 200

class Message(Resource):
    """
    For the beacon API, a POST request to /beacon/message with proper credentials should yield a json response along the lines of
    {"id": <hex string representing the object id>, "timestamp": <epoch timestamp as a decimal>, "offset": <seconds from request until instant>, "destination": <"Infrared"|"Visible">, "intensity": <8-bit integer>, "message": <the message as a UTF-8 str>}
    I think the message for the purposes of simplicity in the short term can be conveyed as a string but this might be changed in the long term for sending other data over the beacon.
    Other than the timestamp and offset, the other items are the same values as what would be transferred by the command system.
    The response will only have information for the next soonest beacon message that has the status of "queued" in the database. 

    A particular message (endpoint /beacon/message/<id>) can be updated with a PUT request with proper credentials. The request should have a json body with the following format:
    {"status": <"Queued"|"Scheduled"|"Transmitting..."|"Transmitted"|"Failed">}
    The response will be a json object with the same format as the GET request.
    """

    decorators = [auth.login_required]

    @internal
    def put(self, message_id: str):
        logging.debug(f"Message put req from {auth.username()}")
        data_str = request.get_json()
        logging.debug(f"Request: {data_str}")
        if data_str is None:
            data_str = loads(request.form['data'])
        message: BeaconMessage = BeaconMessage.find_by_id(message_id)
        try:
            message.status = SentStatus(data_str['status'])  # TODO: Support other fields
        except ValueError:
            logging.debug("Attempted to set invalid status")
            return None, 400
        message.save()
        return {
            "id": str(message.id),
            "timestamp": message.send_at.timestamp(),
            "offset": (datetime.now() - message.send_at).total_seconds(),
            "destination": message.destination.value,
            "intensity": message.intensity,
            "message": message.full_message_bytes.decode('utf-8'),
            "status": message.status.value
        }, 200

    @internal
    def get(self, message_id: str):
        logging.debug(f"Message get req from {auth.username()}")
        message: BeaconMessage = BeaconMessage.find_by_id(message_id)
        return {
            "id": str(message.id),
            "timestamp": message.send_at.timestamp(),
            "offset": (message.send_at - datetime.now()).total_seconds(),
            "destination": message.destination.value,
            "intensity": message.intensity,
            "message": message.full_message_bytes.decode('utf-8'),
            "status": message.status.value
        }, 200
