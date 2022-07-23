"""Outlines the form used to register a new team"""

# TODO: Improve PEP-8 compatibility

from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length

from cubeserver_common import config
from cubeserver_common.models.team import TeamLevel
from cubeserver_common.models.user import User

class RegistrationForm(FlaskForm):
    """Defines the form used to register a team"""

    team_name = StringField('Team Name', validators=[Length(min=1, max=config.TEAM_MAX_CHARS, \
                            message=f"Please provide a team name under {config.TEAM_MAX_CHARS} characters.")])

    _members_message = f"Must have at least {config.TEAM_MIN_MEMBERS} members in a team."
    # TODO: Find a more Pythonic way to do this:
    member1 = StringField('Member #1', validators=[DataRequired(message=_members_message)])
    member2 = StringField('Member #2', validators=[DataRequired(message=_members_message)] if config.TEAM_MIN_MEMBERS > 1 else [])
    member3 = StringField('Member #3', validators=[DataRequired(message=_members_message)] if config.TEAM_MIN_MEMBERS > 2 else [])
    member4 = StringField('Member #4', validators=[DataRequired(message=_members_message)] if config.TEAM_MIN_MEMBERS > 3 else [])

    classification = RadioField('Class', validators=[DataRequired(message="Please select either Varsity or J.V.")], choices=[TeamLevel.VARSITY.value, TeamLevel.JUNIOR_VARSITY.value])

    submit = SubmitField('Register!')

    @staticmethod
    def validate_member1(_, field):
        """Validates the username to ensure that it exists in the database"""
        if User.find_by_username(field.data) is not None:
            raise ValidationError(
                "This user already exists in the database..."
                "Contact an administrator for a solution.")
    
    validate_member2 = validate_member1
    validate_member3 = validate_member1
    validate_member4 = validate_member1
