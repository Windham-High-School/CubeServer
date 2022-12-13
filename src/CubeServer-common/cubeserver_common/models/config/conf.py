"""Models the game configuration

See app.models.config.rules for information regarding the rules of the game"""

from cubeserver_common.config import DEFAULT_HOME_DESCRIPTION
from cubeserver_common.models import PyMongoModel


class Conf(PyMongoModel):
    """Defines the exact rules for a game.

    There will be a separate Rules object for JV and Varsity teams
    """

    def __init__(
        self,
        registration_open: bool = False,
        home_description: str = DEFAULT_HOME_DESCRIPTION
    ):
        super().__init__()
        self.registration_open = registration_open
        self.home_description = home_description

    # The initial instance is created in cubeserver_common/__init__.py
    @staticmethod
    def retrieve_instance() -> PyMongoModel:
        """Retrieves the current config"""
        return Conf.find_one()
