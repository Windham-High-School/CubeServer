"""
This defines constants used throughout the code.

This defines values that cannot be set with the Admin panel but are
"hard-coded" into the software.
Code regarding values set by the Admin panel can be found in
app.app.models.config.
A restart (or a recompile in some configurations) of the docker container is
required to implement changes from this file.
"""

from hashlib import algorithms_available

############################
# Configuration variables: #
############################

# User interface stuff:
CREDITS: str = ""
"""The development credits to be shown in the about page
    (Add your own name here if you contributed!!!) """

DEFAULT_THEME: str = "quartz"
"""The *default* theme to use (users can change this individually)"""



# Contest names:

SHORT_TITLE: str = "CubeServer"
"""A short name that describes this software more than the prize"""

LONG_TITLE: str = "The JagSat Prize"
"""A longer name that describes the prize. This should still be succinct."""

HOME_DESCRIPTION: str = "Thunder. Time. Tech.\nTeams compete with data to win."
"""A brief description of this whole thing which will appear on the home page"""



# Teams:

TEAM_MIN_MEMBERS: int = 2
"""Minimum number of members to make a team"""

TEAM_MAX_CHARS: int = 30
"""Maximum number of characters in a team name"""

TEAM_FILTER_PROFANITY: bool = True
"""Whether or not to filter the team name input with the Python library better-profanity"""

NAME_FILTER_PROFANITY: bool = True
"""Whether or not to filter the user name inputs with the Python library better-profanity"""

TEAM_SECRET_LENGTH: int = 5
"""Number of characters in the team's secret ID"""



# Boxes:

COMMENT_FILTER_PROFANITY: bool = True
"""Whether or not to filter profanity from comments posted by the boxes"""



# Admin Users:

ADMIN_INVITE_TIMEOUT: int = 96
"""Hours before an admin sign-up invitation expires"""



# Behind-the-scenes stuff- Kindly leave alone unless you know what you're doing ;)

ENCODING: str = "utf-8"
"""The string encoding to use by default in cases where this matters

Please don't change this in an existing setup unless you understand
that it may render all user passwords and tokens invalidated. :)  """

SECRET_KEY_FILE: str = "/app/secret_key.txt"
"""Where the value of flask's config variable SECRET_KEY is stored.
This should be in the .gitignore!"""

SECRET_KEY_FILE_ENCODING: str = ENCODING
"""The encoding to use for the file which will store flask's SECRET_KEY"""

PASSWORD_HASH_ALGORITHM: str = "sha3_512"
"""Which algorithm to use for user (admin) passwords and crypto purposes within the web app
This *MUST* be present in hashlib.algorithms_available or things will break!"""

CRYPTO_HASH_ALGORITHM: str = "sha3_512"
"""Which algorithm to use for crypto purposes as far as authenticating the teams' data.
This *MUST* be present in hashlib.algorithms_available or things will break!"""



########################
# Configuration checks #
########################

# Check that the selected hash algorithms exist:
assert PASSWORD_HASH_ALGORITHM in algorithms_available, \
    "Selected password hash must be available on this system."
assert CRYPTO_HASH_ALGORITHM in algorithms_available, \
    "Selected crypto hash must be available on this system."
