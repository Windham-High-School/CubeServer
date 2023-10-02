"""Outlines the form used to change basic configuration"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets import TextArea


class ConfigurationForm(FlaskForm):
    """Defines the form used to register a new user
    from the admin panel"""

    competition_on = BooleanField("Competition begun?")
    registration_open = BooleanField("Team registration open?")
    notify_teams = BooleanField("Notify teams of changes to their status/score/etc?")
    email_domain = StringField("Forced Email Domain")
    home_description = StringField(
        "Home page description (use standard HTML):",
        validators=[DataRequired()],
        widget=TextArea(),
    )
    reg_confirmation = StringField(
        "Registration confirmation screen (HTML):",
        validators=[DataRequired()],
        widget=TextArea(),
    )
    smtp_server = StringField("SMTP Server Address", validators=[DataRequired()])
    smtp_credentials = StringField("SMTP Credentials as user:pass")
    team_email_quota = IntegerField(
        "The maximum number of daily emails a team can send from their cube"
    )
    quota_reset_hour = IntegerField(
        'The hour at which it becomes a "new day" for the email quota'
    )
    banner_message = StringField(
        "A message to be displayed to all web app users- Leave blank to turn off"
    )
    beacon_polling_period = IntegerField(
        "Maximum beacon message scheduling delay (seconds)*",
        validators=[NumberRange(min=1)],
    )
    submit = SubmitField("Save")
