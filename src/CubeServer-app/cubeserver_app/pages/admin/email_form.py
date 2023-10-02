"""Outlines the form used to send an email"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, ValidationError
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

from cubeserver_common import config


class EmailForm(FlaskForm):
    """Defines the form used to send an email
    from the admin panel"""

    name = StringField(
        "From 'name'", default=config.DynamicConfig["Email"]["Automated Sender Name"]
    )
    addr = EmailField(
        "From address",
        default=config.DynamicConfig["Email"]["Automated Sender Address"],
    )

    to = StringField("Recipients (comma-separated)", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired()])
    message = StringField("Message", validators=[DataRequired()], widget=TextArea())

    submit = SubmitField("SEND!")

    @staticmethod
    def validate_to(_, field):  # TODO: This code is UGLY (like the Predator)!
        """Validates the recipient list"""
        txt = field.data
        if not "," in txt:
            if not ("@" in txt and "." in txt):
                raise ValidationError("What kind of recipient email address is that?")
        try:
            ltxt = txt.replace(" ", "").split(",")
            for email in ltxt:
                if not ("@" in email and "." in email):
                    raise ValidationError("Check your recipient list for typos.")
        except Exception as exception:
            raise ValidationError(
                f"There was an issue with your recipient list: {exception}"
            )
