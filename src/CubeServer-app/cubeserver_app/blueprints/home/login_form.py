"""Outlines the form used to activate a new user"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField
from wtforms.validators import InputRequired

from cubeserver_common.models.user import User

class LoginForm(FlaskForm):
    """Defines the form used to log in"""

    username = StringField('Name', validators=[
        InputRequired("You need a username in order to log in.")
    ])
    password = PasswordField('Secret Password', validators=[
        InputRequired("Now, how do you intend to log in without a password?")
    ])

    submit = SubmitField('Log In')

    @staticmethod
    def validate_username(_, field):
        """Validates the username to ensure that it exists in the database"""
        if User.find_by_username(field.data) is None:
            raise ValidationError(
                "Try again- that username doesn't exist in the database.")

    @staticmethod
    def validate_password(form, field):
        """Validates the password-
        this way, the form will show a message if the password is wrong."""
        user = User.find_by_username(form.username.data)
        if user is not None:
            if not user.verify_pwd(field.data):
                raise ValidationError(
                    "Wrong password.")
