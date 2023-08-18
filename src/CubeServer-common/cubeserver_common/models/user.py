"""Models users, teams, and privilege data"""

from enum import Enum, unique
from typing import Optional, cast
from secrets import token_urlsafe
from bcrypt import hashpw, gensalt, checkpw
from flask_login import UserMixin
from secrets import token_urlsafe

from cubeserver_common.models.utils import PyMongoModel

__all__ = ["UserLevel", "User"]


recent_bad_login_attempts = {}


def clear_bad_attempts():
    global recent_bad_login_attempts
    recent_bad_login_attempts.clear()


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

    def __init__(
        self,
        name: str = "",
        level: UserLevel = UserLevel.SUSPENDED,
        email: Optional[str] = None,
        pwd: bytes = b"",
    ):
        """Creates a User object.

        The email is optional.
        If no password hash is provided in pwd,
        then the user will not be able to log in.
        """

        super().__init__()

        self.name = name
        self.email = email
        if email is None:
            self.email = ""
        # If an email is provided, they will need to verify it:
        self.verified = self.email is None
        self._verification_token_raw = token_urlsafe(16)
        self.pwd = pwd
        self.level = level
        self.activated = UserActivation.DEACTIVATED

    @classmethod
    def invite(cls, level: UserLevel, email: str = "") -> tuple:
        """Creates a blank user to serve as an invitation to create a login

        returns a tuple of the User object created alongside a string of
        the key stored as their default password."""

        key = token_urlsafe(16)
        user = User(token_urlsafe(8), level, email=email, pwd=User._hashpwd(key))
        return user, key

    @staticmethod
    def _hashpwd(pwd: str) -> bytes:
        """Runs the bcrypt hash algorithm on the given string."""
        return hashpw(pwd.encode("utf-8"), gensalt())
        # return HMAC(gensecret.check_secrets().encode(config.ENCODING),
        #    msg=pwd.encode(config.ENCODING), digestmod=config.CRYPTO_HASH_ALGORITHM).digest()

    def __str__(self) -> str:
        return self.name + (f" ({self.email})" if self.email else "")

    @property
    def is_active(self):
        return (
            self.activated == UserActivation.ACTIVATED
            and self.level != UserLevel.SUSPENDED
        )

    def activate(self, name: str, email: str, password: str):
        """Activates this user account for login"""
        self.name = name
        self.email = email
        self.pwd = User._hashpwd(password)
        self.activated = UserActivation.ACTIVATED

    def verify_pwd(self, pwd) -> bool:
        """Checks the supplied password against the stored hash"""
        result = checkpw(pwd.encode("utf-8"), self.pwd)
        if not result:
            if self.name not in recent_bad_login_attempts:
                recent_bad_login_attempts[self.name] = 0
            recent_bad_login_attempts[self.name] += 1
        if (
            self.name in recent_bad_login_attempts
            and recent_bad_login_attempts[self.name] > 100
        ):
            return False
        return result
        # return compare_digest(self._hashpwd(pwd), self.pwd)

    @property
    def verification_token(self) -> str:
        """A bcrypt token for email verification"""
        # Why use bcrypt for a one-time token?
        # return urlsafe_b64encode(
        #    User._hashpwd(self._verification_token_raw)
        # )
        return self._verification_token_raw

    def verify(self, token: str) -> bool:
        """Verifies this user's email, returning True on success"""
        # Why use bcrypt for a one-time token?
        # if checkpw(
        #    urlsafe_b64decode(token),
        #    self._verification_token_raw.encode('utf-8')
        # ):
        if token == self._verification_token_raw:
            self.verified = True
        return self.verified

    @classmethod
    def find_by_username(cls, name):
        """Returns the first known user with that username"""
        return cast(User, super().find_one({"name": name}))

    @classmethod
    def find_by_email(cls, email):
        """Returns the first known user with that email"""
        if len(email) < 1:
            return None
        return cast(User, super().find_one({"email": email}))
