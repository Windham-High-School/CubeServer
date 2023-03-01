"""Models the game configuration

See app.models.config.rules for information regarding the rules of the game"""

from typing import Optional

# TODO: Just import config and use the package name throughout
from cubeserver_common.config import DEFAULT_HOME_DESCRIPTION, DEFAULT_REG_CONFIRMATION, DEFAULT_EMAIL_QUOTA, DEFAULT_BEACON_POLLING_PERIOD
from cubeserver_common.models import PyMongoModel

# TODO: Rewrite to use a mapping (key:value) scheme instead of individual variables. Read the defaults in from a file or something?
# TODO: Consider DataClass?
class Conf(PyMongoModel):
    """Defines the exact rules for a game.

    There will be a separate Rules object for JV and Varsity teams
    """

    def __init__(
        self,
        registration_open: bool = False,
        home_description: str = DEFAULT_HOME_DESCRIPTION,
        reg_confirmation: str = DEFAULT_REG_CONFIRMATION,
        email_domain: str = "",  # to require emails to be of a certain domain
        notify_teams: bool = True, # Notify teams of changes to 
        smtp_server: str = "localhost",
        smtp_user: Optional[str] = None,
        smtp_pass: Optional[str] = None,
        team_email_quota: int = DEFAULT_EMAIL_QUOTA,
        quota_reset_hour: int = 10,
        banner_message: str = "",
        beacon_polling_period: int = DEFAULT_BEACON_POLLING_PERIOD
    ):
        super().__init__()
        self.notify_teams = notify_teams
        self.registration_open = registration_open
        self.home_description = home_description
        self.reg_confirmation = reg_confirmation
        self.email_domain = email_domain
        self.smtp_server = smtp_server
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.team_email_quota = team_email_quota
        self.quota_reset_hour = quota_reset_hour
        self.banner_message = banner_message,
        self.beacon_polling_period = beacon_polling_period

    # The initial instance is created in cubeserver_common/__init__.py
    @staticmethod
    def retrieve_instance() -> PyMongoModel:
        """Retrieves the current config"""
        return Conf.find_one()
