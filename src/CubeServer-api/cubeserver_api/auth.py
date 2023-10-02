""" CubeServer-api Auth

All requests to this api will include an `HTTP Basic Auth <https://en.wikipedia.org/wiki/Basic_access_authentication>`_ header-
The username will be the team name (including if the "team" is an internal team, such as the beacon or a reference station)
The password will be the team secret.

All of this is encrypted by way of SSL/TLS encryption, so the plaintext secret should not be an issue.

Additionally, to verify the location of a cube, particularly with the API endpoints exposed to the internet,
the X-API-SECRET header must be added to the request by the `access point / proxy <https://github.com/Windham-High-School/nginx-reverse-proxy>`_.
This secret will be shared via environment variables to both the proxy and to CubeServer and will be checked to verify that requests indeed go through
the localized access point / proxy if enabled by the config.

"""

from typing import Callable

from flask import request
from flask_httpauth import HTTPBasicAuth
from loguru import logger

from cubeserver_common.models.team import Team, TeamStatus
from cubeserver_common.config import EnvConfig, DynamicConfig


auth = HTTPBasicAuth()


@auth.get_password
def get_team_secret(team_name: str) -> str | None:
    """Returns the secret code of a team by name
    (The HTTP basic auth username is the team name, password is secret)"""
    team = Team.find_by_name(team_name)
    logger.debug(f"Request from {team_name}")
    if team and team.status.is_active:
        return team.secret
    return None


def internal(func: Callable) -> Callable:
    """A decorator for internal resource functions"""

    def wrapper(*args, **kwargs):
        team: Team = Team.find_by_name(auth.username())
        if team.status != TeamStatus.INTERNAL:
            # Abort due to unauthorized access
            logger.info(
                f"Unauthorized access attempt to internal resource by {team.name}"
            )
            return None, 401
        return func(*args, **kwargs)

    return wrapper


def check_secret_header(func: Callable) -> Callable:
    """A decorator for all resource functions to be checked for the location-based api secret"""

    def wrapper(*args, **kwargs):
        API_SECRET = EnvConfig.CS_API_LOCATION_SECRET
        if (
            API_SECRET
            and request.headers.get("X-API-Secret") != API_SECRET
            and not DynamicConfig["System"]["AP Secret Check Disable"]
        ):
            team: Team = Team.find_by_name(auth.username())
            logger.info(
                f"Unauthorized access attempt without API SECRET by {team.name}"
            )
            return None, 401
        return func(*args, **kwargs)

    return wrapper
