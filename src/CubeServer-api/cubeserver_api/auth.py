import logging
import os

from flask import request
from flask_httpauth import HTTPBasicAuth

from cubeserver_common.models.team import Team, TeamStatus


auth = HTTPBasicAuth()


@auth.get_password
def get_team_secret(team_name: str) -> str:
    """Returns the secret code of a team by name
    (The digest username is the team name)"""
    team = Team.find_by_name(team_name)
    logging.debug(f"Request from {team_name}")
    if team and team.status.is_active:
        return team.secret
    return None


def internal(func: callable) -> callable:
    """A decorator for internal resource functions"""

    def wrapper(*args, **kwargs):
        team: Team = Team.find_by_name(auth.username())
        if team.status != TeamStatus.INTERNAL:
            # Abort due to unauthorized access
            logging.info(
                f"Unauthorized access attempt to internal resource by {team.name}"
            )
            return "Unauthorized access attempt to internal resource", 403
        return func(*args, **kwargs)

    return wrapper


def check_secret_header(func: callable) -> callable:
    """A decorator for internal resource functions"""

    def wrapper(*args, **kwargs):
        API_SECRET = os.environ.get(
            "API_SECRET"
        )  # TODO: Joe look this upf from the new config location
        if API_SECRET and request.headers.get("X-API-Secret") != API_SECRET:
            team: Team = Team.find_by_name(auth.username())
            logging.info(
                f"Unauthorized access attempt without API SECRET by {team.name}"
            )
            return "Unauthorized access attempt without API SECRET", 403
        return func(*args, **kwargs)

    return wrapper
