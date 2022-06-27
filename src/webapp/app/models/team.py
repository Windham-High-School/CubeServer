"""Models teams of participants"""

from enum import Enum, unique
from math import ceil
import secrets
from typing import List
from model.pymongo_model import SimpleModel
from flask import url_for
from flask_table import Table, Col

from app.models.user import User
from app import mongo, config

@unique
class TeamLevel(Enum):
    """Enumerates the "weight classes" that a team can participate in"""

    JUNIOR_VARSITY = 1
    VARSITY = 2
    PSYCHO_KILLER = 3   # Qu'est-ce que c'est, better run run run run...

    def __repr__(self):
        """Forms a string representation of a TeamLevel value"""
        return ['', 'Junior Varsity', 'Varsity', 'Talking Head'][self.value]

@unique
class TeamStatus(Enum):
    """Handles states of approval, participation, disqualification, & elimination"""

    UNAPPROVED = 0
    DISQUALIFIED = 1
    ELIMINATED = 2
    PARTICIPATING = 3

    def __repr__(self):
        """Forms a string representation of a TeamStatus value"""
        return ['Awaiting Approval', 'Disqualified', 'Eliminated', 'Participating'][self.value]

class TeamHealth:
    """Encapsulates the elements of the game that relate to a team's health and rank
    i.e. score and strike counts, etc."""

    def __init__(self, score: int = 0, strikes: int = 0):
        self.score = score
        self.strikes = strikes

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

class Team(SimpleModel):
    """Models a team"""

    collection = mongo.db.teams

    @classmethod
    def _gen_secret(cls) -> str:
        """Generates a crypto-safe secret of the length defined by config.TEAM_SECRET_LENGTH"""
        return secrets.token_hex(ceil(config.TEAM_SECRET_LENGTH / 2))[:config.TEAM_SECRET_LENGTH]

    def __init__(self, name: str, weight_class: TeamLevel, health: TeamHealth = TeamHealth(),
                    status: TeamStatus = TeamStatus.UNAPPROVED):
        super().__init__()
        self.name = name
        self.weight_class = weight_class
        self.members = []
        self.status = status
        self._health = health
        self._secret = Team._gen_secret()

    def add_member(self, member: User):
        """Adds a member (a User object) to the team"""
        if not member in self.members:
            self.members += [member]

    def drop_member(self, member: User) -> bool:
        """Drops a member (a User object) from the team"""
        if not member in self.members:
            return False
        self.members.remove(member)
        return True

    @property
    def health(self):
        """Returns the current health of this team"""
        return self._health

    @property
    def score(self):
        """Returns the current score for this team"""
        return self._health.score

    @property
    def strikes(self):
        """Returns the current number of strikes for this team"""
        return self._health.strikes

class TeamTable(Table):
    """Allows a group of Team objects to be displayed in an HTML table"""

    allow_sort = True

    name            = Col('Team Name')
    weight_class    = Col('Division')
    status          = Col('Status')
    strikes         = Col('Strikes')
    score           = Col('Score')

    def __init__(self, items: List[Team], endpoint: str, **kwargs):
        self._endpoint = endpoint
        super().__init__(items, **kwargs)

    def sort_url(self, col_id, reverse=False):
        return url_for(self._endpoint, sort=col_id, direction='desc' if reverse else 'asc')
