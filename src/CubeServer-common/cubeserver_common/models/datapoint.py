"""Models users, teams, and privilege data"""

from enum import Enum, unique
from typing import Any, Optional
from datetime import datetime

from pymongo import DESCENDING
from bson import ObjectId
from cubeserver_common.models.utils import PyMongoModel
from cubeserver_common.models.team import Team


__all__ = ['DataPoint', 'DataClass']

@unique
class DataClass(Enum):
    """Enumerates the different data categories"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    LIGHT_INTENSITY = "light intensity"
    COMMENT = "comment"

    @property
    def datatype(self) -> type:
        """Returns the Python type for this category of data"""
        return {
            DataClass.TEMPERATURE: float,
            DataClass.HUMIDITY: float,
            DataClass.PRESSURE: float,
            DataClass.LIGHT_INTENSITY: float,
            DataClass.COMMENT: str
        }[self]

    @property
    def unit(self) -> str:
        """Returns a string representation of the unit associated
        with this class of data"""
        return {  # These values align with those in the API wrapper libs:
            DataClass.TEMPERATURE: "\N{DEGREE SIGN}F",
            DataClass.HUMIDITY: "%",
            DataClass.PRESSURE: "inHg",
            DataClass.LIGHT_INTENSITY: "lux",
            DataClass.COMMENT: ""
        }[self]


class DataPoint(PyMongoModel):
    """Models a datapoint"""

    collection = PyMongoModel.mongo.db.datapoints

    def __init__(self, team_identifier: Optional[ObjectId] = None,
                 category: Optional[DataClass] = DataClass.COMMENT,
                 value: Optional[Any] = None,
                 date: Optional[datetime] = None):
        """Creates a DataPoint object from a category and value
        Specify a team_identifier (the id of the team that posted these data)
        """

        super().__init__()

        self.team_reference = team_identifier
        self.category = category
        self.value = value
        self.moment = date
        if self.moment is None:
            self.moment = datetime.now()

    @property
    def value_with_unit(self):
        """Returns a string with the value and unit"""
        return str(self.value) + self.category.unit

    def __str__(self) -> str:
        return self.value_with_unit

    @classmethod
    def find_by_team(cls, team):
        """Returns a list of datapoints by a team id"""
        return cls.find({'team_reference': ObjectId(team.id)})

    @classmethod
    def find(cls, *args, **kwargs):
        return cls.find_sorted(*args, **kwargs, key="moment", order=DESCENDING)

    @property
    def team_str(self):
        return Team.find_by_id(self.team_reference).name
