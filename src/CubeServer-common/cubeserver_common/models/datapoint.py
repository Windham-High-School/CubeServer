"""Models users, teams, and privilege data"""

import logging
from enum import Enum, unique
from typing import Any, Optional
from datetime import datetime
from better_profanity import profanity

from pymongo import DESCENDING
from bson.objectid import ObjectId
from cubeserver_common.models.utils import PyMongoModel
from cubeserver_common.models.team import Team


__all__ = ['DataPoint', 'DataClass']

@unique
class DataClass(Enum):
    """Enumerates the different data categories"""
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    COMMENT = "comment"
    SIGNAL_LIGHT = "signal"
    BATTERY_REMAINING = "remaining battery"
    BEACON_CHALLENGE = "beacon challenge"

    @property
    def datatype(self) -> type:
        """Returns the Python type for this category of data"""
        return {
            DataClass.TEMPERATURE: float,
            DataClass.PRESSURE: float,
            DataClass.COMMENT: str,
            DataClass.SIGNAL_LIGHT: bool,
            DataClass.BATTERY_REMAINING: int,
            DataClass.BEACON_CHALLENGE: str
        }[self]

    @property
    def unit(self) -> str:
        """Returns a string representation of the unit associated
        with this class of data"""
        return {  # These values align with those in the API wrapper libs:
            DataClass.TEMPERATURE: "\N{DEGREE SIGN}F",
            DataClass.PRESSURE: "inHg",
            DataClass.COMMENT: "",
            DataClass.BEACON_CHALLENGE: "",
            DataClass.SIGNAL_LIGHT: "",
            DataClass.BATTERY_REMAINING: "%"
        }[self]
    
    @classmethod
    @property
    def measurable(cls):
        """Returns all measurable types of data (not COMMENT, etc)"""
        m = []
        for dataclass in cls:
            if dataclass != cls.COMMENT:
                m.append(dataclass)
        return m

    @classmethod
    @property
    def manual(cls):
        """Returns all types of data that are determined manually"""
        return [cls.SIGNAL_LIGHT]

class DataPoint(PyMongoModel):
    """Models a datapoint"""

    def __init__(self, team_identifier: ObjectId = ObjectId(),
                 category: DataClass = DataClass.COMMENT,
                 value: Any = "",
                 date: Optional[datetime] = None,
                 is_reference: bool = False):
        """Creates a DataPoint object from a category and value
        Specify a team_identifier (the id of the team that posted these data)
        A date value of None or unspecified will result in the time at
            instantiation being used.
        """

        super().__init__()

        self.team_reference = team_identifier
        self.category = category
        self.value = value
        self.moment = date
        if self.moment is None:
            self.moment = datetime.now()
        self.is_reference = is_reference
        self.rawscore = 0.0
    
    @property
    def multiplier(self) -> float:
        return Team.find_by_id(self.team_reference).multiplier.amount

    @property
    def value_with_unit(self):
        """Returns a string with the value and unit"""
        return (
            f"{self.value:0.2f}{self.category.unit}"
        ) if isinstance(self.value, float) else (
            f"{self.value}{self.category.unit}"
        )

    def __str__(self) -> str:
        return self.value_with_unit

    @classmethod
    def find_by_team(cls, team: 'Team'):
        """Returns a list of datapoints by a team"""
        return cls.find({'team_reference': ObjectId(team.id)})

    @classmethod
    def find(cls, *args, **kwargs):
        return cls.find_sorted(*args, **kwargs, key="moment", order=DESCENDING)

    @property
    def team_str(self):
        return Team.find_by_id(self.team_reference).name

    @property
    def score(self):
        return self.rawscore * self.multiplier

    def recalculate_score(self, _init_contrib_score: Optional[float | int] = ...):
        from cubeserver_common.models.config.rules import Rules
        logging.debug("Recalculating points...")
        logging.debug(f"Original rawscore: {self.rawscore}")
        team: Team = Team.find_by_id(self.team_reference)
        if _init_contrib_score is ...:
            team.health.change(-1 * self.score)
        else:
            team.health.change(-1 * _init_contrib_score)
        team.save()
        Rules.retrieve_instance().post_data(self, _force=True)

    def censor(self):
        """Removes bad words.
        """
        if isinstance(self.value, str):
            self.value = profanity.censor(self.value)
