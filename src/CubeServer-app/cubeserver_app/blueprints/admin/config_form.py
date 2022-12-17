"""Outlines the form used to change basic configuration"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

from cubeserver_common.models.config.conf import Conf

class ConfigurationForm(FlaskForm):
    """Defines the form used to register a new user
    from the admin panel"""

    registration_open = BooleanField("Team registration open?")
    email_domain = StringField("Forced Email Domain")
    home_description = StringField(
        "Home page description (use standard HTML):",
        validators=[DataRequired()],
        widget=TextArea())
    reg_confirmation = StringField(
        "Registration confirmation screen (HTML):",
        validators=[DataRequired()],
        widget=TextArea())
    smtp_server = StringField("SMTP Server Address", validators=[DataRequired()])
    smtp_credentials = StringField("SMTP Credentials as user:pass")
    submit = SubmitField('Save')
