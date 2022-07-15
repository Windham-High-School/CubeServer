"""Models users, teams, and privilege data"""

from enum import Enum, unique
from typing import Optional
from secrets import token_urlsafe
from hmac import HMAC

from app.models.utils import PyMongoModel

from app import mongo
from app import app, config


__all__ = ['UserLevel', 'User']

@unique
class UserLevel(Enum):
    """Enumerates site-wide permission levels"""

    SUSPENDED = "Suspended"
    SPECTATOR = "Spectator"
    PARTICIPANT = "Participant"
    ADMIN = "Admin"


class User(PyMongoModel):
    """Models a user"""

    collection = mongo.db.users

    def __init__(self, name: str = "", level: UserLevel = UserLevel.SUSPENDED,
        email: Optional[str] = None, pwd: bytes = b""):
        """Creates a User object.

        If uid is left None, one is generated.
        The email is optional.
        If no password hash is provided in pwd,
        then the user will not be able to log in.
        """

        super().__init__()

        self.name = name
        self.email = email
        self.pwd = pwd
        self.level = level

    @classmethod
    def invite(cls, level : UserLevel, email: str = "") -> tuple:
        """Creates a blank user to serve as an invitation to create a login

        returns a tuple of the User object created alongside a string of
        the key stored as their default password."""

        key = token_urlsafe(16)
        user = User(token_urlsafe(8), level, email=email, pwd=User._hashpwd(key))
        return user, key

    @staticmethod
    def _hashpwd(pwd: str) -> bytes:
        """Runs the known HMAC hash algorithm on the given string."""
        return HMAC(app.config["SECRET_KEY"].encode(config.ENCODING),
            msg=pwd.encode(config.ENCODING), digestmod=config.CRYPTO_HASH_ALGORITHM).digest()

    def __str__(self) -> str:
        return (
            self.name +
            (f" ({self.email})" if self.email else "")
        )
