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

# Import after TeamLevel 
from cubeserver_common.models.multiplier import Multiplier, DEFAULT_MULTIPLIER

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

    @property
    def is_active(self) -> bool:
        """Returns true if this team can upload data"""
        return self == TeamStatus.PARTICIPATING


class TeamHealth(Encodable):
    """Encapsulates the elements of the game that relate to a
    team's "health" and rank
    
    Elements of "health" include...
        * score - The score of the team as last calculated
        * last_score - The score of the team before the most recently
            added points
        * strikes - Generally unused; exists for compatibility
        * multiplier - Per-team value to scale every added point value
    """

    def __init__(self, score: int = 0, strikes: int = 0, multiplier: float = 1.0):
        self.score = score
        self.last_score = 0
        self.strikes = strikes
        self.multiplier = multiplier
        super().__init__()

    def __eq__(self, other):
        if isinstance(other, TeamHealth):
            return self.encode() == other.encode()
        return False

    def reward(self, points = 1):
        """Rewards a given number of points (default is 1)"""
        if points < 0:  # Separate reward/penalize methods for expandability
            raise ValueError("Use penalize for removing points.")
        self.last_score = self.score
        self.score += points

    def penalize(self, points = 1):
        """Removes a given number of points (default is 1)"""
        if points < 0:  # "
            raise ValueError("Use reward for adding points.")
        self.last_score = self.score
        self.score -= points

    def strike(self):
        """Doles out a strike!"""
        self.strikes += 1

    def encode(self) -> dict:  # TODO: Replaced by AutoEncodable when written
        return {
            "score": self.score,
            "strikes": self.strikes,
            "lastScore": self.last_score,
            "multiplier": self.multiplier
        }

    @classmethod
    def decode(cls, value: dict):
        health = cls()
        health.score = value["score"]
        health.strikes = value["strikes"]
        health.last_score = value["lastScore"]
        health.multiplier = value["multiplier"]
        return health


class Team(PyMongoModel):
    """Models a team"""

    @classmethod
    def _gen_secret(cls) -> str:
        """Generates a crypto-safe secret of the length defined by
        config.TEAM_SECRET_LENGTH"""
        return secrets.token_hex(ceil(config.TEAM_SECRET_LENGTH / 2)) \
            [:config.TEAM_SECRET_LENGTH]

    def __init__(self, name: str = "",
                 weight_class: Optional[TeamLevel] = TeamLevel.PSYCHO_KILLER,
                 health: TeamHealth = TeamHealth(),
                 status: TeamStatus = TeamStatus.UNAPPROVED,
                 multiplier: Multiplier = DEFAULT_MULTIPLIER):
        super().__init__()
        self.name = name
        self.weight_class = weight_class
        self._members = []
        self.status = status
        self.health = health
        self.secret = Team._gen_secret()
        self.multiplier = multiplier

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

    @classmethod
    def find_by_name(cls, name):
        """Returns the first known team with that name"""
        return super().find_one({"name": name})
