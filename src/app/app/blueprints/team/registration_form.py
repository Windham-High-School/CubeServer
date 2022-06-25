"""Outlines the form used to register a new team"""

import flask_wtf
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length

from app import config

class RegistrationForm(flask_wtf.FlaskForm):
    """Defines the form used to register a team"""

    team_name = StringField('Team Name', validators=[Length(min=1, max=config.TEAM_MAX_CHARS,
                            message=f"Please provide a team name under {config.TEAM_MAX_CHARS} characters.")])

    _members_message = f"Must have at least {config.TEAM_MIN_MEMBERS} members in a team."
    # TODO: Find a more Pythonic way to do this:
    member1 = StringField('Member #1', validators=[DataRequired(message=_members_message)])
    member2 = StringField('Member #2', validators=[DataRequired(message=_members_message)] if config.TEAM_MIN_MEMBERS > 1 else [])
    member3 = StringField('Member #3', validators=[DataRequired(message=_members_message)] if config.TEAM_MIN_MEMBERS > 2 else [])
    member4 = StringField('Member #4', validators=[DataRequired(message=_members_message)] if config.TEAM_MIN_MEMBERS > 3 else [])

    classification = RadioField('Class', validators=[DataRequired(message="Please select either Varsity or J.V.")], choices = ["Varsity", "J.V."])

    submit = SubmitField('Register!')
