"""Models users, teams, and privilege data"""

import uuid
from enum import Enum, unique
from model.pymongo_model import SimpleModel

from app import mongo

@unique
class UserLevel(Enum):
    """Enumerates site-wide permission levels"""

    SUSPENDED = 0
    SPECTATOR = 1
    PARTICIPANT = 2
    ADMIN = 3


class User(SimpleModel):
    """Models a user"""

    collection = mongo.db.users

    def __init__(self, name: str, level: UserLevel, uid: str = None, email: str = None, pwd: str = None):
        """Creates a User object.
        
        If uid is left None, one is generated.
        The email is optional.
        If no password hash is provided in pwd, then the user will not be able to log in.
        """

        self.name = name
        self.email = email
        self.pwd = pwd
        self.level = level
        if uid == None:
            self.uid = uuid.uuid1()
        else:
            self.uid = uid