"""Models users, teams, and privilege data"""

from enum import Enum, unique
from typing import Optional, cast
from secrets import token_urlsafe
from hmac import HMAC, compare_digest
from bcrypt import hashpw, gensalt, checkpw
from flask_login import UserMixin

from cubeserver_common.models.utils import PyMongoModel
from cubeserver_common import config
from cubeserver_common import gensecret

__all__ = ['UserLevel', 'User']

@unique
class UserLevel(Enum):
    """Enumerates site-wide permission levels"""

    SUSPENDED = "Suspended"
    SPECTATOR = "Spectator"
    PARTICIPANT = "Participant"
    ADMIN = "Admin"


@unique
class UserActivation(Enum):
    """Enumerates options for user activation/deactivation"""

    ACTIVATED = "Activated"
    DEACTIVATED = "Deactivated"

class User(PyMongoModel, UserMixin):
    """Models a user"""

    collection = PyMongoModel.mongo.db.users

    def __init__(self, name: str = "", level: UserLevel = UserLevel.SUSPENDED,
        email: Optional[str] = None, pwd: bytes = b""):
        """Creates a User object.

        The email is optional.
        If no password hash is provided in pwd,
        then the user will not be able to log in.
        """

        super().__init__()

        self.name = name
        self.email = email
        self.pwd = pwd
        self.level = level
        self.activated = UserActivation.DEACTIVATED

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
        """Runs the bcrypt hash algorithm on the given string."""
        return hashpw(pwd.encode('utf-8'), gensalt())
        #return HMAC(gensecret.check_secrets().encode(config.ENCODING),
        #    msg=pwd.encode(config.ENCODING), digestmod=config.CRYPTO_HASH_ALGORITHM).digest()

    def __str__(self) -> str:
        return (
            self.name +
            (f" ({self.email})" if self.email else "")
        )
    
    @property
    def is_active(self):
        return ( self.activated == UserActivation.ACTIVATED and
                 self.level != UserLevel.SUSPENDED )

    def activate(self, name: str, email: str, password: str):
        """Activates this user account for login"""
        self.name = name
        self.email = email
        self.pwd = User._hashpwd(password)
        self.activated = UserActivation.ACTIVATED

    def verify_pwd(self, pwd) -> bool:
        """Checks the supplied password against the stored hash"""
        return checkpw(pwd.encode('utf-8'), self.pwd)
        #return compare_digest(self._hashpwd(pwd), self.pwd)

    @classmethod
    def find_by_username(cls, name):
        """Returns the first known user with that username"""
        return cast(User, super().find_one({"name": name}))
