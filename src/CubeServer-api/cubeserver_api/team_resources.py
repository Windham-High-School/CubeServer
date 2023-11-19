"""This package contains the resource classes for the api used by teams
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
from cubeserver_common.models.team import Team, TeamLevel
from cubeserver_common.models.beaconmessage import BeaconMessage
from cubeserver_common.models.datapoint import DataClass, DataPoint
from cubeserver_common import config
from cubeserver_common.metadata import VERSION

from .auth import auth, check_secret_header


class Data(Resource):
    """A POST-only resource for datapoints"""

    decorators = [check_secret_header, auth.login_required]

    def post(self):
        logging.debug(f"Data post req from {auth.username()}")
        team = Team.find_by_name(auth.username())
        logging.info(f"Data submission de {team.name}")
        # Get DataClass and cast the value:
        data_str = request.get_json()
        logging.debug(f"Request: {data_str}")
        if data_str is None:
            data_str = loads(request.form["data"])
        data_class = DataClass(data_str["type"])
        if (
            not Conf.retrieve_instance().competition_on
            and data_class in DataClass.measurable
        ):
            logging.info("Data submission rejected; competition is not running.")
            return request.form, 423
        if data_class in DataClass.manual:
            logging.debug("Manually-determined- Rejecting")
            return request.form, 400  # If this should be manually-determined..
        data_value = data_class.datatype(data_str["value"])
        logging.debug(f"Value: {data_value}")
        # Create the DataPoint object:
        point = DataPoint(
            team_identifier=team.id,
            category=data_class,
            value=data_value,
            is_reference=team.is_reference,
        )
        logging.debug(f"DataPoint object: {point}")
        logging.info("Posting data")
        if Rules.retrieve_instance().post_data(point):
            logging.info("Success!")
            return request.form, 201
        logging.info("Something happened suboptimally.")
        return request.form, 400  # TODO: Support better response codes?


class Email(Resource):
    """A POST-only resource for datapoints"""

    decorators = [check_secret_header, auth.login_required]

    def post(self):
        logging.debug(f"Email send req from {auth.username()}")
        team = Team.find_by_name(auth.username())
        logging.info(f"Email submission from: {team.name}")
        # Get DataClass and cast the value:
        data_str = request.get_json()
        subject = data_str["subject"]
        message = data_str["message"]
        logging.debug(f"Subject: {subject}")
        logging.debug(message)
        logging.info("Sending...")

        def send_team_email():
            if team.emails_sent >= Conf.retrieve_instance().team_email_quota:
                return False
            import cubeserver_common.models.mail

            msg = cubeserver_common.models.mail.Message(
                config.FROM_NAME,
                config.FROM_ADDR,
                team.emails,
                subject,
                message,
                team.id,
            )
            if msg.send():
                team.emails_sent += 1
                team.save()
                return True
            return False

        if send_team_email():
            logging.info("Success!")
            return request.form, 201
        logging.warning("Failed to send email.")
        return request.form, 400  # TODO: Support better response codes?


class Status(Resource):
    """A resource with some basic info"""

    decorators = [check_secret_header, auth.login_required]

    def get(self):
        logging.debug(f"Status get req de {auth.username()}")
        team = Team.find_by_name(auth.username())
        logging.info(f"Status req de {team.name}")
        return {
            "datetime": datetime.now().isoformat(),
            "unix_time": int(time()),
            "2020_time": int(time() - 1577836800),
            "status": {"score": team.score},
            "CubeServer_version": VERSION,
        }, 200


class CodeUpdate(Resource):
    """A resource for teams to update code.py on their circuitpython cubes"""

    decorators = [check_secret_header, auth.login_required]

    def get(self):
        team = Team.find_by_name(auth.username())
        logging.info(f"Code update req de {team.name}")
        return {
            "datetime": datetime.now().isoformat(),
            "unix_time": int(time()),
            "encoding": "base64",
            "new": not team.code_update_taken,
            "code": encodebytes(team.get_code_update()).decode("utf-8"),
        }, 200
