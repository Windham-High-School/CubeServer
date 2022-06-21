"""
This defines constants used throughout the code.

This defines values that cannot be set with the Admin panel but are
"hard-coded" into the software.
Code regarding values set by the Admin panel can be found in
app.app.models.config.
A restart (or a recompile in some configurations) of the docker container is
required to implement changes from this file.
"""

# Contest names:

SHORT_TITLE = "CubeServer"
"""A short name that describes this software more than the prize"""

LONG_TITLE = "The JagSat Prize"
"""A longer name that describes the prize. This should still be succinct."""

HOME_DESCRIPTION = "Thunder. Time. Tech.\nTeams compete with data to win."
"""A brief description of this whole thing which will appear on the home page"""



# Teams:

TEAM_MIN_MEMBERS = 2
"""Minimum number of members to make a team"""

TEAM_MAX_CHARS = 30
"""Maximum number of characters in a team name"""

TEAM_FILTER_PROFANITY = True
"""Whether or not to filter the team name input with the Python library better-profanity"""

NAME_FILTER_PROFANITY = True
"""Whether or not to filter the user name inputs with the Python library better-profanity"""

TEAM_SECRET_LENGTH = 5
"""Number of characters in the team's secret ID"""



# Boxes:

COMMENT_FILTER_PROFANITY = True
"""Whether or not to filter profanity from comments posted by the boxes"""



# Admin Users:

ADMIN_INVITE_TIMEOUT = 96
"""Hours before an admin sign-up invitation expires"""



# Behind-the-scenes stuff (kindly leave alone unless you know what you're doing):

SECRET_KEY_FILE = "/app/secret_key.txt"
"""Where the value of flask's config variable SECRET_KEY is stored.
This should be in the .gitignore!"""



# END of hard-coded configuration.