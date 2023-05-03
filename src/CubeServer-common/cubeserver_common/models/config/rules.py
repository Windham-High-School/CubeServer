"""Models the game rules

See app.models.team for more information regarding the game aspect"""

import logging
from typing import Optional, Mapping, List
from datetime import datetime
import json
from bson import ObjectId

from cubeserver_common.config import COMMENT_FILTER_PROFANITY
from cubeserver_common.models import PyMongoModel, Encodable
from cubeserver_common.models.team import Team, TeamLevel
from cubeserver_common.models.datapoint import DataPoint, DataClass
from cubeserver_common.models.reference import ReferencePoint, Reference
from cubeserver_common.models.utils import ComplexDictCodec, EnumCodec, EncodableCodec, DummyCodec


class RegularOccurrence(Encodable):
    """Defines a patterned occurrence
    
    This entails datetimes occuring at a set of offsets from the hour in seconds
    """

    def __init__(
        self,
        offsets: List[int] = [],
        interval: Optional[int] = None,
        tolerance: int = 0
    ):
        """Provide a tolerance in seconds AND either:
         a list of offsets from the hour or an interval from the hour,
         both in seconds"""
        self.tolerance = tolerance
        if interval is None:
            self.offsets = offsets
        else:
            self.offsets = list(range(0, 60*60, interval))

    def follows(self, moment: datetime) -> bool:
        """Determines if a given datetime follows this pattern
        (tolerance is in seconds)"""
        seconds_since_hour = moment.minute * 60 + moment.second
        return any(
            (abs(seconds_since_hour - offset) <= self.tolerance)
            for offset in self.offsets
        ) or any(
            (abs((seconds_since_hour - 60) - offset) <= self.tolerance)
            for offset in self.offsets
        )

    def encode(self) -> dict:
        """Encodes an Encodable object into a plain old, bson-able
        dictionary"""
        return {"offsets": self.offsets}

    @classmethod
    def decode(cls, value: dict) -> Encodable:
        """Decodes a dictionary into an Encodable object"""
        return cls(value['offsets'])

class Rules(PyMongoModel):
    """Defines the exact rules for a game.

    There will be a separate Rules object for JV and Varsity teams
    All integer time values are in seconds unless otherwise noted.
    """

    class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return json.JSONEncoder.default(self, o)

    def __init__(  # Default gameplay parameters:
        self,
        point_menu: Mapping[TeamLevel, Mapping[DataClass, int]] = {
            TeamLevel.JUNIOR_VARSITY: {
                DataClass.COMMENT: 0,
                DataClass.PRESSURE: 1,
                DataClass.SIGNAL_LIGHT: 25,
                DataClass.TEMPERATURE: 1
            },
            TeamLevel.VARSITY: {
                DataClass.COMMENT: 0,
                DataClass.PRESSURE: 1,
                DataClass.SIGNAL_LIGHT: 25,
                DataClass.TEMPERATURE: 1,
                DataClass.BEACON_CHALLENGE: 10,
            }
        },
        # Times data should be posted, measured in offsets from the hour in seconds:
        post_times: Mapping[TeamLevel, Mapping[DataClass, RegularOccurrence]] = {
            TeamLevel.JUNIOR_VARSITY: {
                DataClass.PRESSURE: RegularOccurrence(
                    offsets=[30*60],
                    tolerance=3*60
                ),
                DataClass.TEMPERATURE: RegularOccurrence(
                    offsets=[0],
                    tolerance=3*60
                )
            },
            TeamLevel.VARSITY: {
                DataClass.PRESSURE: RegularOccurrence(
                    interval=6*60,
                    tolerance=60
                ),
                DataClass.TEMPERATURE: RegularOccurrence(
                    interval=15*60,
                    tolerance=60
                )
            }
        },
        # % error expressed as a decimal, no longer absolute error
        accuracy_tolerance: Mapping[TeamLevel, Mapping[DataClass, float]] = {
            TeamLevel.JUNIOR_VARSITY: {
                DataClass.PRESSURE: 0.10,
                DataClass.TEMPERATURE: 0.10
            },
            TeamLevel.VARSITY: {
                DataClass.PRESSURE: 0.10,
                DataClass.TEMPERATURE: 0.10
            }
        },
        reference_window: int = 30,
        selected: bool = True
    ):
        """
            reference_window is the number of seconds old a reference point can be for it to be used in scoring.
        """
        super().__init__()

        # TODO: Autogen recursive codec trees?
        # primitive bson types so codecs are auto selected as DummyCodec:
        self.selected: bool = selected
        self.reference_window: int = reference_window
        # Manually spell out how to deal with these fields:
        super().register_field(
            'point_menu',
            value=point_menu,
            custom_codec=ComplexDictCodec(
                EnumCodec(TeamLevel),
                ComplexDictCodec(
                    EnumCodec(DataClass),
                    DummyCodec(float)
                )
            )
        )
        super().register_field(
            'times',
            value=post_times,
            custom_codec=ComplexDictCodec(
                EnumCodec(TeamLevel),
                ComplexDictCodec(
                    EnumCodec(DataClass),
                    EncodableCodec(RegularOccurrence)
                )
            )
        )
        super().register_field(
            'accuracy_tolerance',
            value=accuracy_tolerance,
            custom_codec=ComplexDictCodec(
                EnumCodec(TeamLevel),
                ComplexDictCodec(
                    EnumCodec(DataClass),
                    DummyCodec(float)
                )
            )
        )

    def post_data(self, datapoint: DataPoint, _force: bool = False) -> bool:
        """This is executed whenever a team sends in some data
        If this returns true, it sends an OK response to the client"""

        # Prevent double-dipping on points:
        if not _force and datapoint.rawscore > 0.0:
            raise ValueError("This datapoint has already been scored!")

        team = Team.find_by_id(datapoint.team_reference)

        # Profanity check:
        if COMMENT_FILTER_PROFANITY:
            datapoint.censor()

        # TODO: Make this more Pythonic
        if datapoint.category in DataClass.manual \
           and datapoint.category in DataClass.measurable:
            if bool(datapoint.value):
                datapoint.rawscore = self.point_menu[team.weight_class][datapoint.category]
            else:
                datapoint.rawscore = 0.0
        else:
            try:
                # If they didn't miss the window, give 'em some points:
                window = self.times[team.weight_class][datapoint.category]
                logging.debug(f"Window: {window}")
                if window.follows(datapoint.moment):
                    # Get some reference data:
                    self._score(team, datapoint)
                    logging.debug("Window met.")
                else:
                    logging.debug("Window missed.")
            except KeyError:  # If this type of datapoint doesn't get scored:
                logging.debug("Not a scored data category for this weight class.")
                datapoint.rawscore = 0
        
        # Score the datapoint:
        team.health.change(datapoint.score)
        team.save()
        # Now log the data:
        datapoint.save()
        return True

    def _score(
        self,
        team: Team,
        datapoint: DataPoint,
        force=False
    ):
        """Scores the datapoint, storing the score in the datapoint.
        Set force to True to recalculate an already-scored datapoint
        THIS MAKES THE *ASS*UMPTION* THAT THE TIME WINDOW IS VALID!"""
        # Make sure the point is scoreable:
        if datapoint.rawscore != 0 and not force or \
           datapoint.category in DataClass.manual or \
           datapoint.category not in DataClass.measurable:
            return
        datapoint.multiplier = team.multiplier.amount
        try:
            tol = self.accuracy_tolerance[team, datapoint.category]
            points_possible = self.point_menu[team.weight_class][datapoint.category]
            reference = Reference.get_window_point(self.reference_window)
            reference_val = reference.of(datapoint.category).value
            if abs((reference_val - datapoint.value) / reference_val) <= tol:
                datapoint.rawscore = points_possible
            else:
                datapoint.rawscore = 0.0
        except IndexError:
            pass

    # The initial instance is created in cubeserver_common/__init__.py
    @staticmethod
    def retrieve_instance() -> 'Rules':
        """Retrieves the current ruleset"""
        return Rules.find_one({'selected': True})

    def to_json(self) -> str:
        """Turns this document into a json string"""
        # TODO: Is there a better way to pretty-print?
        ugly: str = self.JSONEncoder().encode(self.encode())
        return json.dumps(json.loads(ugly), indent=4)

    @classmethod
    def from_json(cls, json_str: str):
        """Turns a JSON string into a rules object"""
        obj = cls.decode(json.loads(json_str))
        obj._id = ObjectId(obj._id)
        return obj

    @property
    def json_str(self) -> str:
        """Remapping of to_json() as a property for the rules_form"""
        return self.to_json()
