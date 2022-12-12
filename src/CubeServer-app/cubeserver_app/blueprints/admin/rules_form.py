"""Outlines the form used to change basic configuration"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea



class RulesForm(FlaskForm):
    """Defines the form used to edit the game rules"""

    json_str = StringField(
        "Game Rules (raw JSON Representation; USE PROPER SYNTAX and CAUTION)",
        validators=[DataRequired()],
        widget=TextArea())
    submit = SubmitField('Save')
