"""Logging stuff
"""

import logging
import sys
from typing import Any
from loguru import logger

from .config import EnvConfig


__all__ = ['InterceptHandler', 'init_logging']


_LOGLEVEL: str = EnvConfig.CS_LOGLEVEL
_LOGCOLORS: bool = EnvConfig.CS_LOGCOLORS
_LOGOUTPUT: Any

if EnvConfig.CS_LOGOUTPUT == "stdout":
    _LOGOUTPUT = sys.stdout
elif EnvConfig.CS_LOGOUTPUT == "stderr" or EnvConfig.CS_LOGOUTPUT == "":
    _LOGOUTPUT = None
else:
    _LOGOUTPUT = EnvConfig.CS_LOGOUTPUT


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def init_logging():
    """Init logger"""
    if _LOGOUTPUT is not None:
        logger.start(_LOGOUTPUT, level=_LOGLEVEL)

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logging.debug("Test legacy logging debug succeeded.")
