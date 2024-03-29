"""
This defines constants used throughout the code.

This defines values that cannot be set with the Admin panel but are
"hard-coded" into the software.
Code regarding values set by the Admin panel can be found in
app.app.models.config.
A rebuild of the docker container is
required to implement changes from this file.
"""

import logging

############################
# Configuration variables: #
############################


# Logging:

LOGGING_LEVEL: int = logging.DEBUG
"""The log level (DEBUG, INFO, WARN, ERROR, FATAL)"""

LOGGING_FORMAT: str = "%(asctime)s : %(levelname)s : %(process)d => %(message)s"
"""The format for logging stuff, see Python's `logging` library"""


# Default Credentials:

DEFAULT_ADMIN_USERNAME: str = "admin"
"""This is the default first user"""

DEFAULT_ADMIN_PASSWORD: str = "12345"
"""This is the default password for the admin user.
This can be changed after the first login."""


# User interface stuff:

DEFAULT_THEME: str = "dark"
"""The *default* theme to use (users can change this individually)"""


# Defaults changable by the admin panel:

DEFAULT_HOME_DESCRIPTION: str = (
    "Thunder. Time. Tech.<br>\nTeams compete with data to win."
)
"""A brief description of this whole thing which will appear on the home page
This can be changed by an admin user at any point during the competition!"""

DEFAULT_REG_CONFIRMATION: str = "Thank you for registering your team!<br>\nGood Luck!"
"""The screen that is shown when a team's registration is complete"""

DEFAULT_EMAIL_QUOTA: int = 2
"""The default maximum number of daily emails that can be sent by a team"""


# Scoring Scheme:
# For more config, check out the cubeserver_common.scoring package
#   and cubeserver_common.models.config.rules


# Emails:

FROM_NAME: str = "The Project CubeServer"
"""The name with which most emails will be sent"""

FROM_ADDR: str = "noreply@whsproject.club"
"""The address from which most emails will be sent"""


# Contest names:

SHORT_TITLE: str = "CubeServer"
"""A short name that describes this software more than the prize"""

LONG_TITLE: str = "The Project"
"""A longer name that describes the prize. This should still be succinct."""


# Beacon:

DEFAULT_BEACON_POLLING_PERIOD: int = 10
"""The default period of the BeaconMessage collection polling in seconds"""


# Teams:

TEAM_MAX_CHARS: int = 30
"""Maximum number of characters in a team name"""

CHECK_PROFANITY: bool = True
"""Whether to check names, etc. for profanity."""

PROFANITY_MESSAGE: str = (
    "Not Funny. \n"
    "We think you used some bad words in your input. \n"
    "Profanity is not allowed by the administrator."
)
"""The message to use if profanity is detected in the user's input"""

TEAM_SECRET_LENGTH: int = 16
"""Number of characters in teams' secret IDs"""

INTERNAL_SECRET_LENGTH: int = 32
"""Number of characters in internal teams' secret IDs"""

TEAM_MAX_UPDATE_LENGTH: int = 32768  # 32KiB
"""Maximum length of a team's code update"""


# Internal Teams (for extending api functionality for behind-the-scenes use):

BEACON_TEAM_NAME: str = "CubeServer-beacon"
"""The name of the "team" for the beacon"""

REFERENCE_TEAM_NAME: str = "CubeServer-reference-{}"
"""The naming pattern for reference "team"s"""

REFERENCE_PORT_RANGE: tuple[int] = (32770, 32870)
"""Ports allocated to the reference server"""

REFERENCE_COMMAND_PORT: int = 32769
"""The port to which reference commands are sent to be dispatched to stations"""


# Cubes:

COMMENT_FILTER_PROFANITY: bool = True
"""Whether to filter profanity from comments posted by the cubes"""


# Behind-the-scenes stuff - this could easily make stuff break -
# Kindly leave this alone unless you know what you're doing ;)

ENCODING: str = "utf-8"
"""The string encoding to use by default in cases where this matters

Please don't change this in an existing setup unless you understand
that it may render all user passwords and tokens invalidated. :)  """

SECRET_KEY_FILE: str = "/secret/secret_key.txt"
"""Where the value of flask's config variable SECRET_KEY is stored.
This should be in the .gitignore for good practice.
Also, this MUST correspond with the volume mounted in docker-compose.yml
so that the secret key can be persistent across rebuilds and not invalidate
everyone's passwords and connections, since that would be really bad in
a production environment."""

SECRET_KEY_FILE_ENCODING: str = ENCODING
"""The encoding to use for the file which will store flask's SECRET_KEY"""

PASSWORD_HASH_ALGORITHM: str = "sha3_512"
"""Which algorithm to use for user (admin) passwords and crypto purposes within the web app
This *MUST* be present in hashlib.algorithms_available or things will break!"""

CRYPTO_HASH_ALGORITHM: str = "sha3_512"
"""Which algorithm to use for crypto purposes as far as authenticating the teams' data.
This *MUST* be present in hashlib.algorithms_available or things will break!"""

TEMP_PATH: str = "/tmp/"
"""A path to a temporary directory that will not be persistent"""


########################
#      Generated       #
########################

# Contributors (loaded from AUTHORS.yaml):
CONTRIBUTORS_YAML: str = """
%YAML 1.2
---
Joseph R. Freeston:
  role: |-
    The Architect
  contributions: |-
    Primary CubeServer Developer
    Lead software developer 2022-present
  link: https://github.com/snorklerjoe
Heather Brayer:
  role: |-
    Contributor
  contributions: |-
    Graphic Design
  link: https://github.com/avocadoheather
Greg Kindrat:
  role: |-
    Contributor
  contributions: |-
    Graphic Design Assistant
  link: ''
Julia Miller:
  role: |-
    Contributor
  contributions: |-
    Graphic Design Assistant
  link: ''
Ryan Burbo:
  role: |-
    Contributor
  contributions: |-
    Graphic Design Assistant
  link: ''
Lucas Tousignant:
  role: |-
    Contributor
  contributions: |-
    Cube Guinea Pig
  link: ''
"""
