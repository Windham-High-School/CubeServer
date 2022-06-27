"""Models users, teams, and privilege data"""

import uuid
from enum import Enum, unique
from secrets import token_urlsafe
from hmac import HMAC
from model.pymongo_model import SimpleModel

from app import mongo
from app import app, config

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

    @classmethod
    def invite(cls, level : UserLevel, email: str = "") -> tuple:
        """Creates a blank user to serve as an invitation to create a login

        returns a tuple of the User object created alongside a string of
        the key stored as their default password."""

        key = token_urlsafe(16)
        user = User(token_urlsafe(8), level, email=email, pwd=User._hashpwd(key))
        return user, key

    def __init__(self, name: str, level: UserLevel, uid: str = "",
        email: str = "", pwd: bytes = b""):
        """Creates a User object.

        If uid is left None, one is generated.
        The email is optional.
        If no password hash is provided in pwd, then the user will not be able to log in.
        """

        super().__init__()

        self.name = name
        self.email = email
        self.pwd = pwd
        self.level = level
        if uid is None:
            self.uid = uuid.uuid1()
        else:
            self.uid = uid

    @staticmethod
    def _hashpwd(pwd: str) -> bytes:
        """Runs the known HMAC hash algorithm on the given string."""
        return HMAC(app.config["SECRET_KEY"].encode(config.ENCODING),
            msg=pwd.encode(config.ENCODING), digestmod=config.CRYPTO_HASH_ALGORITHM).digest()
