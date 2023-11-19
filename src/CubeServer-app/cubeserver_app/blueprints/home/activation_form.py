"""Outlines the form used to activate a new user"""

from flask import session
from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import InputRequired, EqualTo, Length, Email

from cubeserver_common.models.user import User


class UserActivationForm(FlaskForm):
    """Defines the form used to activate a new user
    from a shared link"""

    email = EmailField(
        "Email",
        validators=[
            InputRequired("Email has been around since 1969. You should have one."),
            Email("What kind of email address is that?"),
        ],
    )
    username = StringField(
        "Name", validators=[InputRequired("Please put in some kind of name.")]
    )
    password = PasswordField(
        "Secret Password",
        validators=[
            InputRequired(
                "Now, how do you intend to be able to log in without a password?"
            ),
            Length(
                min=5, message="What kind of password is fewer than 5 characters long?"
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            EqualTo(
                "password",
                message="Looks like you had trouble typing the same password twice.",
            )
        ],
    )
    submit = SubmitField("Register!")

    @staticmethod
    def validate_username(_, field):
        """Validates the username to ensure that it is unique"""
        if "username" not in session and User.find_by_username(field.data) is not None:
            raise ValidationError("That username is already taken.")
