"""This package contains the resource classes for the api used by teams
"""

from datetime import datetime
from time import time

from flask import request
from flask_restful import Resource
from json import loads
from base64 import encodebytes
from loguru import logger

from cubeserver_common.models.config.rules import Rules
from cubeserver_common.config import DynamicConfig, EnvConfig
from cubeserver_common.models.team import Team
from cubeserver_common.models.datapoint import DataClass, DataPoint
from cubeserver_common import config

from ..auth import auth, check_secret_header


__all__ = ["Data", "Email", "Status", "CodeUpdate"]


class Data(Resource):
    """A POST-only resource for datapoints"""

    decorators = [auth.login_required, check_secret_header]

    def post(self):
        logger.debug(f"Data post req from {auth.username()}")
        team = Team.find_by_name(auth.username())
        logger.info(f"Data submission de {team.name}")
        # Get DataClass and cast the value:
        data_str = request.get_json()
        logger.debug(f"Request: {data_str}")
        if data_str is None:
            data_str = loads(request.form["data"])
        data_class = DataClass(data_str["type"])
        if (
            DynamicConfig["Competition"]["Competition Freeze"]
            and data_class in DataClass.measurable
        ):
            logger.info("Data submission rejected; competition is frozen.")
            return request.form, 423
        if data_class in DataClass.manual:
            logger.debug("Manually-determined- Rejecting")
            return (
                request.form,
                400,
            )  # If this should be manually-determined and not submitted directly..
        data_value = data_class.datatype(data_str["value"])
        logger.debug(f"Value: {data_value}")
        # Create the DataPoint object:
        point = DataPoint(
            team_identifier=team.id, category=data_class, value=data_value
        )
        logger.debug(f"DataPoint object: {point}")
        logger.info("Posting data")
        if Rules.retrieve_instance().post_data(point):
            logger.info("Success!")
            return request.form, 201
        logger.info("Something happened suboptimally.")
        return request.form, 400


class Email(Resource):
    """A POST-only resource for datapoints"""

    decorators = [auth.login_required, check_secret_header]

    def post(self):
        logger.debug(f"Email send req from {auth.username()}")
        team = Team.find_by_name(auth.username())
        logger.info(f"Email submission from: {team.name}")
        # Get DataClass and cast the value:
        data_str = request.get_json()
        subject = data_str["subject"]
        message = data_str["message"]
        logger.debug(f"Subject: {subject}")
        logger.debug(message)
        logger.info("Sending...")

        def send_team_email():
            if team.emails_sent >= DynamicConfig["Email"]["Team Quota"]:
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
            logger.info("Success!")
            return request.form, 201
        logger.warning("Failed to send email.")
        return request.form, 400


class Status(Resource):
    """A resource with some basic info"""

    decorators = [auth.login_required, check_secret_header]

    def get(self):
        logger.debug(f"Status get req de {auth.username()}")
        team = Team.find_by_name(auth.username())
        logger.info(f"Status req de {team.name}")
        return {
            "datetime": datetime.now().isoformat(),
            "unix_time": int(time()),
            "2020_time": int(time() - 1577836800),
            "status": {"score": team.score},
        }, 200


class CodeUpdate(Resource):
    """A resource for teams to update code.py on their circuitpython cubes"""

    decorators = [auth.login_required, check_secret_header]

    def get(self):
        team = Team.find_by_name(auth.username())
        logger.info(f"Code update req de {team.name}")
        return {
            "datetime": datetime.now().isoformat(),
            "unix_time": int(time()),
            "encoding": "base64",
            "new": not team.code_update_taken,
            "code": encodebytes(team.get_code_update()).decode(EnvConfig.CS_STR_ENCODING),
        }, 200
