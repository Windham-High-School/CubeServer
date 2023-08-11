"""Structures and validates runtime config via environment variables"""

from os import environ, path

__all__ = ["EnvConfig"]


class EnvConfigError(ValueError):
    """Invalid environment variable configuration"""


def __bool_from_str(input_str: str) -> bool:
    if input_str not in ["TRUE", "FALSE"]:
        raise EnvConfigError(
            f"Invalid boolean value {input_str}. \nMust be TRUE or FALSE."
        )
    return {"TRUE": True, "FALSE": False}[input_str]


def __int_from_str(input_str: str) -> int:
    if not input_str.isnumeric():
        raise EnvConfigError(
            f"Invalid integer value {input_str}. \nMust be numeric only."
        )


class EnvConfig:
    """Runtime config all in one place"""

    CS_DEV: bool = __bool_from_str(environ("CS_DEV", "FALSE"))
    CS_RELEASE: str = environ("CS_RELEASE", "dev" if CS_DEV else "")
    CS_DEVCCONTAINER: bool = __bool_from_str(environ("CS_DEVCONTAINER", "FALSE"))
    CS_LOGLEVEL: str = environ("CS_LOGLEVEL", "info").upper()

    CS_DOMAIN: str = environ("CS_DOMAIN", "localhost")

    # Default credentials
    CS_DEFAULT_ADMIN_USER: str = environ("CS_DEFAULT_ADMIN_USER", "admin")
    CS_DEFAULT_ADMIN_PASS: str = environ("CS_DEFAULT_ADMIN_PASS", "12345")

    # GUnicorn parameters
    CS_APP_WORKER_TIMEOUT: int = __int_from_str(environ("CS_APP_WORKER_TIMEOUT", "90"))
    CS_APP_TIMEOUT: int = __int_from_str(environ("CS_APP_TIMEOUT", "45"))
    CS_APP_PRELOAD: int = __bool_from_str(environ("CS_APP_PRELOAD", "TRUE"))

    CS_API_WORKER_TIMEOUT: int = __int_from_str(environ("CS_API_WORKER_TIMEOUT", "90"))
    CS_API_TIMEOUT: int = __int_from_str(environ("CS_API_TIMEOUT", "45"))
    CS_API_PRELOAD: int = __bool_from_str(environ("CS_API_PRELOAD", "TRUE"))

    CS_MAX_UPLOAD_SIZE: int = __int_from_str(environ("CS_MAX_UPLOAD_SIZE", "32768"))

    # DNS Hostnames
    CS_APP_HOST: str = environ("CS_APP_HOST", CS_DOMAIN)
    CS_API_HOST: str = environ("CS_API_HOST", f"api.{CS_DOMAIN}")

    # API Connection configuration
    CS_API_ADDR: str = environ("CS_API_ADDR", CS_API_HOST)
    CS_API_PORT: int = __int_from_str(environ("CS_API_PORT", "8081"))

    # Container setup
    CS_CONTAINER_PREFIX: str = environ("CS_CONTAINER_PREFIX", "CubeServer")
    CS_TEMP_PATH: str = environ("CS_TEMP_PATH", "/tmp/")

    # Other
    CS_STR_ENCODING: str = environ("CS_STR_ENCODING", "utf-8")

    @classmethod
    def validate(cls) -> None:
        """Ensures valid configuration.
        Should be run at init.
        @raises EnvConfigError
        """

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
