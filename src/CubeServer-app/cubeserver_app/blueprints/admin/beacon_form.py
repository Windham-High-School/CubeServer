"""Outlines the forms used for beacon operations"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.beaconmessage import BeaconMessageEncoding


class ImmediateBeaconForm(FlaskForm):
    """Defines the form used to send a beacon message now"""

    message = StringField("Message")
    msg_format = SelectField("Format",
        choices=[
            (option.value, option.value)
                for option in BeaconMessageEncoding
        ]
    )
    submit = SubmitField('Transmit')
