"""Outlines the form used to register a new team"""

# TODO: Improve PEP-8 compatibility

from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, ValidationError, EmailField
from wtforms.validators import DataRequired, Length

from cubeserver_common import config
from cubeserver_common.models.team import TeamLevel
from cubeserver_common.models.config.conf import Conf
from cubeserver_common.models.user import User
from cubeserver_common.models.team import Team

class RegistrationForm(FlaskForm):
    """Defines the form used to register a team"""

    team_name = StringField('Team Name', validators=[Length(min=1, max=config.TEAM_MAX_CHARS, \
                            message=f"Please provide a team name under {config.TEAM_MAX_CHARS} characters.")])

    _members_message = f"Must have at least 2 members in a team."
    _emails_message = f"Who doesn't have an email? Come on. Pony up."
    # TODO: Find a more Pythonic way to do this:
    member1 = StringField('Member #1', validators=[DataRequired(message=_members_message)])
    email1 = EmailField('Email #1', validators=[DataRequired(message=_emails_message)])
    member2 = StringField('Member #2', validators=[DataRequired(message=_members_message)])
    email2 = EmailField('Email #2', validators=[DataRequired(message=_emails_message)])
    member3 = StringField('Member #3 (not recommended)')
    email3 = EmailField('Email #3')

    classification = RadioField('Class', validators=[DataRequired(message="Please select a weight class!")], choices=[TeamLevel.VARSITY.value, TeamLevel.JUNIOR_VARSITY.value])

    submit = SubmitField('Register!')

    @staticmethod
    def validate_name(_, field):
        """Validates the team name to ensure it isn't taken"""
        if Team.find_by_name(field.data) is not None:
            raise ValidationError(
                "This team name already exists in the database..."
                "Please choose a different one.")

    @staticmethod
    def validate_member1(_, field):
        """Validates the username to ensure that it isn't in the database"""
        if User.find_by_username(field.data) is not None:
            raise ValidationError(
                "This user already exists in the database..."
                "Contact an administrator for a solution.")

    @staticmethod
    def validate_email1(_, field):
        """Validates the email"""
        # Make sure it isn't taken already:
        if User.find_by_email(field.data) is not None:
            raise ValidationError(
                "This email already exists in the database..."
                "Contact an administrator for a solution."
            )
        # Make sure it has the right domain (if required by admin)
        if field.data and not field.data.endswith(Conf.retrieve_instance().email_domain):
            raise ValidationError(
                "All emails provided must be from "
                f"{Conf.retrieve_instance().email_domain}"
            )

    validate_member2 = validate_member1
    validate_member3 = validate_member1

    validate_email2 = validate_email1
    validate_email3 = validate_email1
