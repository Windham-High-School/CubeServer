"""Outlines the form used to determine the multiplier for a team"""

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, FloatField, HiddenField

from cubeserver_common.models.user import UserLevel
from cubeserver_common.models.multiplier import VolumeUnit, Multiplier

SIZE_NAME_MAPPING = dict(
    zip(
        [f"{volUnit.name}: {volUnit.value}\" cube" for volUnit in VolumeUnit],
        VolumeUnit
    )
)

class MultiplierForm(FlaskForm):
    """Defines the form used to enter multiplier information"""

    team_id = HiddenField("Team _id")
    #cost   = FloatField('Additional Cost ($)')
    #size   = SelectField(
    #    'Size', choices=SIZE_NAME_MAPPING.keys())
    mass   = FloatField('Total Mass (g)')
    submit = SubmitField('Save changes')
