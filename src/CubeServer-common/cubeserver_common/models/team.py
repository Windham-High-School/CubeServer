"""Models teams of participants"""

import logging
import secrets
from enum import Enum, unique
from math import ceil
from typing import Any, List, Optional

from cubeserver_common import config
from cubeserver_common.models.user import User
from cubeserver_common.models.utils import Encodable, PyMongoModel

from .config.conf import Conf
from .mail import Message

__all__ = ["TeamLevel", "TeamStatus", "TeamHealth", "Team"]


def _filter_nonetype_from_list(l: list[Any]) -> list:
    return list(filter(lambda item: item is not None, l))


@unique
class TeamLevel(Enum):
    """Enumerates the "weight classes" that a team can participate in"""

    JUNIOR_VARSITY = "Nanometer"
    VARSITY = "Lumen"
    REFERENCE = "REFERENCE"
    PSYCHO_KILLER = "Talking Head"  # Qu'est-ce que c'est, better run run run run...

    def __repr__(self):
        """Forms a string representation of a TeamLevel value"""
        return self.value


# Import after TeamLevel
from cubeserver_common.models.multiplier import DEFAULT_MULTIPLIER, Multiplier


@unique
class TeamStatus(Enum):
    """Handles states of approval, participation, disqualification, & elimination"""

    UNAPPROVED = "Awaiting Approval"
    PARTICIPATING = "Participating"
    DISQUALIFIED = "Disqualified"
    ELIMINATED = "Eliminated"
    INTERNAL = "[Internal]"  # For the beacon & demo cubes

    def __repr__(self):
        """Forms a string representation of a TeamStatus value"""
        return self.value

    @property
    def is_active(self) -> bool:
        """Returns True if this team can upload data"""
        return self in [TeamStatus.PARTICIPATING, TeamStatus.INTERNAL]

    @property
    def is_public(self) -> bool:
        """Returns True if this team can be publicly visible"""
        return self in [TeamStatus.PARTICIPATING, TeamStatus.DISQUALIFIED]


class TeamHealth(Encodable):
    """Encapsulates the elements of the game that relate to a
    team's "health" and rank

    Elements of "health" include...
        * score - The score of the team as last calculated
        * last_score - The score of the team before the most recently
            added points
        * multiplier - Per-team value to scale every added point value
    """

    def __init__(self, score: int = 0, multiplier: float = 1.0):
        self.score = score
        self.last_score = 0
        self.multiplier = multiplier
        super().__init__()

    def __eq__(self, other):
        if isinstance(other, TeamHealth):
            return self.encode() == other.encode()
        return False

    #    def reward(self, points = 1):
    #        """Rewards a given number of points (default is 1)"""
    #        if points < 0:  # Separate reward/penalize methods for expandability
    #            raise ValueError("Use penalize for removing points.")
    #        self.last_score = self.score
    #        self.score += points
    #
    #    def penalize(self, points = 1):
    #        """Removes a given number of points (default is 1)"""
    #        if points < 0:  # "
    #            raise ValueError("Use reward for adding points.")
    #        self.last_score = self.score
    #        self.score -= points

    def change(self, amt):
        """Changes the score by a given amount"""
        self.last_score = self.score
        self.score += amt
        logging.debug(f"Set score from {self.last_score} to {self.score}")

    def reset(self):
        """Resets the score to 0"""
        logging.debug("Resetting score")
        self.change(-1 * self.score)

    def encode(self) -> dict:  # TODO: Replaced by AutoEncodable when written
        return {
            "score": self.score,
            "lastScore": self.last_score,
            "multiplier": self.multiplier,
        }

    @classmethod
    def decode(cls, value: dict):
        health = cls()
        health.score = value["score"]
        health.last_score = value["lastScore"]
        health.multiplier = value["multiplier"]
        return health


class Team(PyMongoModel):
    """Models a team"""

    RESERVED_NAMES = [config.BEACON_TEAM_NAME] + [
        config.REFERENCE_TEAM_NAME.format(i) for i in range(10)
    ]

    @classmethod
    def _gen_secret(cls, length: int) -> str:
        """Generates a crypto-safe secret of the length defined by
        config.TEAM_SECRET_LENGTH"""
        return secrets.token_hex(ceil(length / 2))[:length]

    def __init__(
        self,
        name: str = "",
        weight_class: Optional[TeamLevel] = TeamLevel.PSYCHO_KILLER,
        health: TeamHealth = TeamHealth(),
        status: TeamStatus = TeamStatus.UNAPPROVED,
        multiplier: Multiplier = DEFAULT_MULTIPLIER,
        emails_sent_today: int = 0,
        code_update: bytes = b"",
        code_update_taken: bool = True,
        _secret_length: int = config.TEAM_SECRET_LENGTH,
        _find_new_reference_port: bool = False,
    ):
        super().__init__()
        self.name = name
        self.weight_class = weight_class
        self._members = []
        self.status = status
        self.health = health
        self.secret = Team._gen_secret(_secret_length)
        self.multiplier = multiplier
        self.emails_sent = emails_sent_today
        self._code_update = code_update
        self.code_update_taken = code_update_taken
        if _find_new_reference_port:
            self.reference_port = self.find_unused_port()

    def add_member(self, member: User):
        """Adds a member (a User object) to the team"""
        if not member.id in self._members:
            self._members += [member.id]

    def drop_member(self, member: User) -> bool:
        """Drops a member (a User object) from the team"""
        if member.id not in self._members:
            return False
        self._members.remove(member.id)
        return True

    @property
    def members(self) -> List[User]:
        """Returns the User objects"""
        return _filter_nonetype_from_list(
            [User.find_by_id(member_id) for member_id in self._members]
        )

    @property
    def emails(self) -> List[str]:
        """Returns this team's email list"""
        return _filter_nonetype_from_list([user.email for user in self.members])

    @property
    def members_str(self) -> str:
        """Returns a human-readable string listing representations
        of the members"""
        return ", ".join(str(member) for member in self.members)

    @property
    def members_names_str(self) -> str:
        """Returns a human-readable string listing representations
        of the members"""
        return ", ".join(member.name for member in self.members)

    @property
    def score(self) -> float:
        """Returns the number of points from the TeamHealth object"""
        return self.health.score

    @property
    def score_delta(self) -> float:
        """Returns the point gain"""
        return self.score - self.health.last_score

    @property
    def all_verified(self) -> bool:
        """Returns True if every user from this team has verified
        their email and consent to join this team"""
        return all([user.verified for user in self.members])

    @classmethod
    def find_by_name(cls, name):
        """Returns the first known team with that name"""
        return super().find_one({"name": name})

    @classmethod
    def find_by_division(cls, division: TeamLevel):
        """Returns teams with a given division"""
        return super().find({"weight_class": division.value})

    @property
    def id_2(self):
        # TODO: Fix this (and AdminTeamsTable.id_2)
        # TODO: Replace all usages with id_secondary (property of PyMongoModel's)
        """Just to allow multiple columns in the adminteamstable to rely upon the id..."""
        return self._id

    @property
    def name_secondary(self):
        """Just to allow multiple columns in the adminteamstable to rely upon the name..."""
        return self.name

    def send_api_email(self, subject, message):
        """Send an email from their cube to them"""
        if self.emails_sent >= Conf.retrieve_instance().team_email_quota:
            return False
        msg = Message(config.FROM_NAME, config.FROM_ADDR, self.emails, subject, message)
        if msg.send():
            self.emails_sent += 1
            self.save()
            return True
        return False

    @classmethod
    def reset_sent_emails(cls):
        """Resets the email send counter for the day"""
        for team in cls.find():
            team.emails_sent = 0
            team.save()

    def update_code(self, code: bytes):
        """Uploads a string of python code to be transferred to the cube"""
        self.code_update_taken = False
        self._code_update = code
        self.save()

    def get_code_update(self) -> bytes:
        """Grabs the latest code update given by the team"""
        self.code_update_taken = True
        self.save()
        return self._code_update

    @classmethod
    def find_beacon(cls) -> "Team":
        """Finds the reserved team for the beacon.
        If it doesn't exist already, it will be created.
        """
        beacon = cls.find_by_name(config.BEACON_TEAM_NAME)
        if beacon is not None:
            return beacon
        beacon = Team(
            name=config.BEACON_TEAM_NAME,
            weight_class=TeamLevel.REFERENCE,
            status=TeamStatus.INTERNAL,
            multiplier=DEFAULT_MULTIPLIER,
        )
        beacon.save()
        return beacon

    @classmethod
    def find_references(cls) -> List["Team"]:
        """Lists all reference "Team"s"""
        return cls.find(
            {
                "status": TeamStatus.INTERNAL.value,
                "name": {"$nin": [config.BEACON_TEAM_NAME]},
            }
        )

    @property
    def is_reference(self) -> bool:
        """Returns True if this team is a reference team"""
        return (
            self.weight_class == TeamLevel.REFERENCE
            and self.name != config.BEACON_TEAM_NAME
        )

    # TODO: Document that reference names must end in -<int>
    @property
    def reference_id(self) -> int:
        if not self.is_reference:
            raise AttributeError("This team is not a reference team.")
        return int(self.name.split("-")[-1])

    @property
    def reference_port(self) -> int:
        """Returns the port that the appropriate reference server is listening on"""
        if self.weight_class != TeamLevel.REFERENCE:
            raise AttributeError("This team is not a reference team.")
        port: int = config.REFERENCE_PORT_RANGE[0] + self.reference_id
        if port > config.REFERENCE_PORT_RANGE[1]:
            raise ValueError("Reference port is out of range.")
        return port

    # TODO: Remove obsolete reference port stuff
    @classmethod
    def find_unused_port(cls) -> int:
        """Returns a port within the range specified in the configuration"""
        port_range = range(
            config.REFERENCE_PORT_RANGE[0], config.REFERENCE_PORT_RANGE[1] + 1
        )
        all_references = cls.find_references()
        for potential_port in port_range:
            unused = True
            for reference in all_references:
                if hasattr(reference, "reference_port"):
                    unused &= reference.reference_port != potential_port
            if unused:
                return potential_port
        raise ValueError(
            "The entire reserved port range for reference servers has already been assigned."
        )

    def recompute_score(self):
        """Completely recompute the score for this team.
        This can be risky.
        """
        from cubeserver_common.models.datapoint import DataPoint

        logging.debug("Re-evaluating team score.")
        self.health.reset()
        self.save()
        for data in DataPoint.find_by_team(self):
            data.recalculate_score(0)
