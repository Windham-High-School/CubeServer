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
    home_description = StringField(
        "Home page description:",
        validators=[DataRequired()],
        widget=TextArea())
    submit = SubmitField('Update')
