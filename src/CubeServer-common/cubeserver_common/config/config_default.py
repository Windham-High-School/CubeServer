"""The default categories, descriptions, and values for the db-stored config"""

from ..models.grouped_config import (
    GroupedConfig,
    GroupedConfigCategory,
    GroupedConfigField,
    FieldInputType,
)

DEFAULT_CONFIG = GroupedConfig(name="Default Configuration", selected=False)

# Competition
# ===========
DEFAULT_CONFIG.add_category(
    GroupedConfigCategory(
        name="Competition", description="Basic competition information"
    )
)

DEFAULT_CONFIG["Competition"].add_field(
    GroupedConfigField(
        name="Registration Open",
        description="Are new teams allowed to register?",
        default_value=True,
        input_type=FieldInputType.CHECKBOX,
    )
)

DEFAULT_CONFIG["Competition"].add_field(
    GroupedConfigField(
        name="Registration Email Domain",
        description="All email addresses being registered MUST end with this value, blank means any email may be used",
        default_value="",
    )
)

DEFAULT_CONFIG["Competition"].add_field(
    GroupedConfigField(
        name="Competition Freeze",
        description="Freeze the competition, denying further data submissions",
        default_value=False,
        input_type=FieldInputType.CHECKBOX,
    )
)


# Strings
# ===========
DEFAULT_CONFIG.add_category(
    GroupedConfigCategory(
        name="Strings", description="String values that can be configured"
    )
)

DEFAULT_CONFIG["Strings"].add_field(
    GroupedConfigField(
        name="Short Title",
        description="Short name, appears very publicly",
        default_value="CubeServer",
    )
)

DEFAULT_CONFIG["Strings"].add_field(
    GroupedConfigField(
        name="Long Title",
        description="Slightly longer title, appears very publicly",
        default_value="The Project",
    )
)

DEFAULT_CONFIG["Strings"].add_field(
    GroupedConfigField(
        name="Home Description",
        description="A description of the competition or other info for the home page, unsanitized (can contain raw HTML)",
        default_value="<i>Hmmmmmmm</i>, the admin user has not configured stuff yet.<br><br>Peace out.",
        input_type=FieldInputType.TEXTAREA,
    )
)

DEFAULT_CONFIG["Strings"].add_field(
    GroupedConfigField(
        name="Registration Confirmation",
        description="What shows up to a team upon registration, unsanitized (can contain raw HTML)",
        default_value="<i>Hmmmmmmm</i>, the admin user has not configured stuff yet.<br><br>Peace out.",
        input_type=FieldInputType.TEXTAREA,
    )
)


# Website alert
# ===========
DEFAULT_CONFIG.add_category(
    GroupedConfigCategory(
        name="Banner Alert",
        description="Allows for a notification banner to persist at the top of the website",
    )
)

DEFAULT_CONFIG["Banner Alert"].add_field(
    GroupedConfigField(
        name="Show",
        description="Whether to display the banner alert",
        default_value=False,
        input_type=FieldInputType.CHECKBOX,
    )
)

DEFAULT_CONFIG["Banner Alert"].add_field(
    GroupedConfigField(
        name="Text Content",
        description="The content of the banner alert.",
        default_value="",
    )
)


# Email
# ===========
DEFAULT_CONFIG.add_category(
    GroupedConfigCategory(
        name="Email", description="Things pertaining to SMTP and server-sent emails"
    )
)

DEFAULT_CONFIG["Email"].add_field(
    GroupedConfigField(
        name="SMTP Server",
        description="The address of the server used for sending emails. Blank means emails will not be sent, but still stored to the database.",
        default_value="",
    )
)

DEFAULT_CONFIG["Email"].add_field(
    GroupedConfigField(
        name="SMTP Username",
        description="The username to use for outgoing SMTP",
        default_value="",
    )
)

DEFAULT_CONFIG["Email"].add_field(
    GroupedConfigField(
        name="SMTP Password",
        description="The password to use for outgoing SMTP",
        default_value="",
    )
)

DEFAULT_CONFIG["Email"].add_field(
    GroupedConfigField(
        name="Automated Sender Name",
        description="The name used for automated emails",
        default_value="The Project CubeServer",
    )
)

DEFAULT_CONFIG["Email"].add_field(
    GroupedConfigField(
        name="Automated Sender Address",
        description="The address used for automated emails",
        default_value="noreply@whsproject.club",
    )
)

DEFAULT_CONFIG["Email"].add_field(
    GroupedConfigField(
        name="Team Quota",
        description="The maximum number of daily emails any team can send",
        default_value=5,
        input_type=FieldInputType.INTEGER,
    )
)

DEFAULT_CONFIG["Email"].add_field(
    GroupedConfigField(
        name="Team Quota Reset Hour",
        description="The number of the hour upon which the quota tallies are reset daily",
        default_value=0,
        input_type=FieldInputType.INTEGER,
    )
)

DEFAULT_CONFIG["Email"].add_field(
    GroupedConfigField(
        name="Notify Teams",
        description="Notify teams of changes made that affect them directly",
        default_value=True,
        input_type=FieldInputType.CHECKBOX,
    )
)


# System
# ===========
DEFAULT_CONFIG.add_category(
    GroupedConfigCategory(name="System", description="Lower-level system things")
)

DEFAULT_CONFIG["System"].add_field(
    GroupedConfigField(
        name="Max Team Length",
        description="The maximum length of a team name, in characters",
        default_value=30,
        input_type=FieldInputType.INTEGER,
    )
)

DEFAULT_CONFIG["System"].add_field(
    GroupedConfigField(
        name="Team Secret Length",
        description="The length of a team's authorization secret, in chars (higher is more secure)",
        default_value=16,
        input_type=FieldInputType.INTEGER,
    )
)

DEFAULT_CONFIG["System"].add_field(
    GroupedConfigField(
        name="Internal Secret Length",
        description="The length of an internal team's authorization secret, in chars (higher is more secure)",
        default_value=32,
        input_type=FieldInputType.INTEGER,
    )
)

DEFAULT_CONFIG["System"].add_field(
    GroupedConfigField(
        name="Beacon Team Name",
        description="The name of the internal beacon team",
        default_value="CubeServer-beacon",
    )
)

DEFAULT_CONFIG["System"].add_field(
    GroupedConfigField(
        name="Reference Team Prefix",
        description="The prefix of the internal reference teams, which will be followed by an integer index",
        default_value="CubeServer-reference-",
    )
)


# Profanity
# ===========
DEFAULT_CONFIG.add_category(
    GroupedConfigCategory(
        name="Profanity",
        description='Checking for "bad-words" and attempting to censor them automatically',
    )
)

DEFAULT_CONFIG["Profanity"].add_field(
    GroupedConfigField(
        name="Profanity Message",
        description="Appears when a user's, erm, colorful response is rejected",
        default_value="Profanity was detected in your input.\nThis stuff is public... So don't swear, bud.",
        input_type=FieldInputType.TEXTAREA,
    )
)

DEFAULT_CONFIG["Profanity"].add_field(
    GroupedConfigField(
        name="Censor comments",
        description="Whether or not to censor profanity in cube-posted comments to the server",
        default_value=True,
        input_type=FieldInputType.CHECKBOX,
    )
)

DEFAULT_CONFIG["Profanity"].add_field(
    GroupedConfigField(
        name="Censor names",
        description="Whether or not to censor profanity in team names during registration",
        default_value=True,
        input_type=FieldInputType.CHECKBOX,
    )
)
