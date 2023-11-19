"""Outlines the form used to register a new user"""

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

from cubeserver_common.models.user import UserLevel


class InvitationForm(FlaskForm):
    """Defines the form used to register a new user
    from the admin panel"""

    level = SelectField(
        "Permission Level", choices=[level.value for level in UserLevel]
    )
    submit = SubmitField("Invite User")
