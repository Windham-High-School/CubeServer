"""Models teams of participants"""

from enum import Enum, unique
from typing import List, Optional
from math import ceil
import secrets

from cubeserver_common.models.utils import Encodable, PyMongoModel
from cubeserver_common.models.user import User
from cubeserver_common import config

__all__ = ['TeamLevel', 'TeamStatus', 'TeamHealth', 'Team']

@unique
class TeamLevel(Enum):
    """Enumerates the "weight classes" that a team can participate in"""

    JUNIOR_VARSITY = "Junior Varsity"
    VARSITY = "Varsity"
    PSYCHO_KILLER = "Talking Head"   # Qu'est-ce que c'est, better run run run run...

    def __repr__(self):
        """Forms a string representation of a TeamLevel value"""
        return self.value


@unique
class TeamStatus(Enum):
    """Handles states of approval, participation, disqualification, & elimination"""

    UNAPPROVED = "Awaiting Approval"
    PARTICIPATING = "Participating"
    DISQUALIFIED = "Disqualified"
    ELIMINATED = "Eliminated"

    def __repr__(self):
        """Forms a string representation of a TeamStatus value"""
        return self.value


class TeamHealth(Encodable):
    """Encapsulates the elements of the game that relate to a
    team's health and rank
    i.e. score and strike counts, etc."""

    def __init__(self, score: int = 0, strikes: int = 0):
        self.score = score
        self.strikes = strikes
        super().__init__()

    def __eq__(self, other):
        if isinstance(other, TeamHealth):
            return self.score == other.score and self.strikes == other.strikes
        return False

    def reward(self, points = 1):
        """Rewards a given number of points (default is 1)"""
        self.score += points

    def strike(self):
        """Doles out a strike!"""
        self.strikes += 1

    def encode(self) -> dict:
        return {"score": self.score, "strikes": self.strikes}

    @classmethod
    def decode(cls, value: dict):
        health = cls()
        health.score = value["score"]
        health.strikes = value["strikes"]
        return health


class Team(PyMongoModel):
    """Models a team"""

    collection = PyMongoModel.mongo.db.get_collection('teams')

    @classmethod
    def _gen_secret(cls) -> str:
        """Generates a crypto-safe secret of the length defined by
        config.TEAM_SECRET_LENGTH"""
        return secrets.token_hex(ceil(config.TEAM_SECRET_LENGTH / 2)) \
            [:config.TEAM_SECRET_LENGTH]

    def __init__(self, name: str = "",
                 weight_class: Optional[TeamLevel] = TeamLevel.PSYCHO_KILLER,
                 health: TeamHealth = TeamHealth(),
                 status: TeamStatus = TeamStatus.UNAPPROVED):
        super().__init__()
        self.name = name
        self.weight_class = weight_class
        self._members = []
        self.status = status
        self.health = health
        self.secret = Team._gen_secret()

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
        return [User.find_by_id(member_id) for member_id in self._members]

    @property
    def members_str(self) -> str:
        """Returns a human-readable string listing representations
        of the members"""
        return ', '.join(str(member) for member in self.members)

    @property
    def members_names_str(self) -> str:
        """Returns a human-readable string listing representations
        of the members"""
        return ', '.join(member.name for member in self.members)

    @property
    def strikes(self) -> int:
        """Returns the number of strikes from the TeamHealth object"""
        return self.health.strikes

    @property
    def score(self) -> int:
        """Returns the number of points from the TeamHealth object"""
        return self.health.score
