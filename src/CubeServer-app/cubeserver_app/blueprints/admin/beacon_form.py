"""Outlines the forms used for beacon operations"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, IntegerField, ValidationError, DateTimeField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.beaconmessage import BeaconMessageEncoding, OutputDestination
from cubeserver_common.models.team import TeamLevel


class ImmediateBeaconForm(FlaskForm):
    """Defines the form used to send a beacon message now"""

    instant = DateTimeField("Scheduled Time (YYYY-MM-DD HH:MM:SS)")
    message = StringField("Message", widget=TextArea())
    division = SelectField(
        'Division', choices=[TeamLevel.JUNIOR_VARSITY.value, TeamLevel.VARSITY.value])
    destination = SelectField(
        'Output', choices=[level.value for level in OutputDestination])
    msg_format = SelectField("Message Encoding",
        choices=[
            (option.value, option.value)
                for option in BeaconMessageEncoding
        ]
    )
    intensity = IntegerField("Intensity")
    submit = SubmitField('Schedule Transmission')

    @staticmethod
    def validate_intensity(_, field):
        if 0 <= field.data <= 255:
            return
        raise ValidationError("Intensity must be an 8-bit integer!")
