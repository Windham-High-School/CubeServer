"""Structures and validates runtime config via environment variables"""

from os import environ, path
from typing import TypeVar, Optional

__all__ = ["EnvConfig", "EnvConfigError"]


T = TypeVar("T")


class EnvConfigError(ValueError):
    """Invalid environment variable configuration"""


class EnvConfig:
    """Runtime config all in one place"""

    @staticmethod
    def __bool_from_str(input_str: str) -> bool | None:
        if len(input_str) == 0:
            return None
        if input_str not in ["TRUE", "FALSE"]:
            raise EnvConfigError(
                f"Invalid boolean value {input_str}. \nMust be TRUE or FALSE."
            )
        return {"TRUE": True, "FALSE": False}[input_str]

    @staticmethod
    def __int_from_str(input_str: str) -> int | None:
        if len(input_str) == 0:
            return None
        if not input_str.isnumeric():
            raise EnvConfigError(
                f"Invalid integer value {input_str}. \nMust be numeric only."
            )
        return int(input_str)

    @staticmethod
    def __sad_if_none(value: Optional[T]) -> T:
        """Raises exception is value is None, else returns the value"""
        if value is not None:
            return value
        raise EnvConfigError("Value cannot be None / blank.")

    # Modifications to default values here should be mirrored in the following files:
    # /.devcontainer/.env.development

    CS_DEV: bool = __bool_from_str(environ.get("CS_DEV", "FALSE")) or False
    CS_RELEASE: str = environ.get("CS_RELEASE", "dev" if CS_DEV else "")
    CS_DEVCCONTAINER: bool = (
        __bool_from_str(environ.get("CS_DEVCONTAINER", "FALSE")) or False
    )
    CS_LOGLEVEL: str = environ.get("CS_LOGLEVEL", "info").upper()

    CS_DOMAIN: str = environ.get("CS_DOMAIN", "localhost")

    CS_FLASK_SECRET: str = environ.get("CS_FLASK_SECRET", "devsecret")

    # Default credentials
    CS_DEFAULT_ADMIN_USER: str = environ.get("CS_DEFAULT_ADMIN_USER", "admin")
    CS_DEFAULT_ADMIN_PASS: str = environ.get("CS_DEFAULT_ADMIN_PASS", "12345")

    # GUnicorn parameters
    CS_APP_WORKER_TIMEOUT: int = __sad_if_none(
        __int_from_str(environ.get("CS_APP_WORKER_TIMEOUT", "90"))
    )
    CS_APP_TIMEOUT: int = __sad_if_none(
        __int_from_str(environ.get("CS_APP_TIMEOUT", "45"))
    )
    CS_APP_PRELOAD: int = __sad_if_none(
        __bool_from_str(environ.get("CS_APP_PRELOAD", "TRUE"))
    )

    CS_API_WORKER_TIMEOUT: int = __sad_if_none(
        __int_from_str(environ.get("CS_API_WORKER_TIMEOUT", "90"))
    )
    CS_API_TIMEOUT: int = __sad_if_none(
        __int_from_str(environ.get("CS_API_TIMEOUT", "45"))
    )
    CS_API_PRELOAD: int = __sad_if_none(
        __bool_from_str(environ.get("CS_API_PRELOAD", "TRUE"))
    )

    CS_MAX_UPLOAD_SIZE: int = __sad_if_none(
        __int_from_str(environ.get("CS_MAX_UPLOAD_SIZE", "32768"))
    )

    # DNS Hostnames
    CS_APP_HOST: str = environ.get("CS_APP_HOST", CS_DOMAIN)
    CS_API_HOST: str = environ.get("CS_API_HOST", f"api.{CS_DOMAIN}")

    # API Connection configuration
    CS_AP_SSID: str = environ.get("CS_AP_SSID", "CubeServer-API")
    CS_API_ADDR: str = environ.get("CS_API_ADDR", CS_API_HOST)
    CS_API_PORT: int = __sad_if_none(__int_from_str(environ.get("CS_API_PORT", "8081")))

    # Database Connection & Credentials
    CS_MONGODB_USERNAME: str = environ.get("CS_MONGODV_USERNAME", "flask")
    CS_MONGODB_PASSWORD: str = environ.get("CS_MONGODV_PASSWORD", "")
    CS_MONGODB_DRIVER: str = environ.get("CS_MONGODV_DRIVER", "mongodb")
    CS_MONGODB_DATABASE: str = environ.get("CS_MONGODV_DATABASE", "csdb")
    CS_MONGODB_OPTIONS: str = environ.get("CS_MONGODV_OPTIONS", "authsource=admin")
    CS_MONGODB_PORT: str | None = __int_from_str(environ.get("CS_MONGODV_PORT", ""))
    CS_MONGODB_HOST: str = environ.get("CS_MONGODV_HOST", "mongodb")

    # Container setup
    CS_CONTAINER_PREFIX: str = environ.get("CS_CONTAINER_PREFIX", "CubeServer")
    CS_TEMP_PATH: str = environ.get("CS_TEMP_PATH", "/tmp/")

    # Other
    CS_STR_ENCODING: str = environ.get("CS_STR_ENCODING", "utf-8")

    CS_COMMIT_HASH: str = environ.get("CS_COMMIT_HASH", "undefined")

    @classmethod
    def validate(cls) -> None:
        """Ensures valid configuration.
        Should be run at init.
        @raises EnvConfigError
        """

        print(cls.CS_DEV)

        # Base
        if cls.CS_RELEASE == "":
            raise EnvConfigError("CS_RELEASE must not be empty.")
        if cls.CS_DEVCCONTAINER and not cls.CS_DEV:
            raise EnvConfigError("CS_DEVCONTAINER must not be set in production.")
        # Domain & Hostnames
        if cls.CS_DOMAIN == "":
            raise EnvConfigError("CS_DOMAIN must be provided.")
        if cls.CS_APP_HOST == "":
            raise EnvConfigError(
                "CS_APP_HOST must be something the server can bind to."
            )
        if cls.CS_API_HOST == "":
            raise EnvConfigError(
                "CS_API_HOST must be something the server can bind to."
            )
        # Setup
        if cls.CS_TEMP_PATH[-1] != "/" or not path.isdir(cls.CS_TEMP_PATH):
            raise EnvConfigError(
                "CS_TEMP_PATH must be a valid directory path ending with a '/'."
            )
        if cls.CS_FLASK_SECRET == "devsecret" and not cls.CS_DEV:
            raise EnvConfigError("CS_FLASK_SECRET must be set in production!")
