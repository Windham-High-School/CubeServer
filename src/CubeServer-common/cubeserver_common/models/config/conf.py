"""Models the game configuration

See app.models.config.rules for information regarding the rules of the game"""

from typing import Optional

from cubeserver_common.config import DEFAULT_HOME_DESCRIPTION
from cubeserver_common.models import PyMongoModel


class Conf(PyMongoModel):
    """Defines the exact rules for a game.

    There will be a separate Rules object for JV and Varsity teams
    """

    def __init__(
        self,
        registration_open: bool = False,
        home_description: str = DEFAULT_HOME_DESCRIPTION,
        smtp_server: str = "localhost",
        smtp_user: Optional[str] = None,
        smtp_pass: Optional[str] = None
    ):
        super().__init__()
        self.registration_open = registration_open
        self.home_description = home_description
        self.smtp_server = smtp_server
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass

    # The initial instance is created in cubeserver_common/__init__.py
    @staticmethod
    def retrieve_instance() -> PyMongoModel:
        """Retrieves the current ruleset"""
        return Conf.find_one()
