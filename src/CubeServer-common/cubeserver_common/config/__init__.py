"""Environment variables and database-stored configuration"""

import logging
import traceback

from .environ import *
from ..models.grouped_config import GroupedConfig
from .config_default import *

__all__ = [
    "EnvConfig",
    "EnvConfigError",
    "DEFAULT_CONFIG",
    "GroupedConfig",
    "DynamicConfig",
]


class _DynamicConfigMeta:
    """Config not defined in env vars
    It will try to load this from the database.
    If that fails, it will log an error and the default will stand-in.
    """

    def fget(self) -> GroupedConfig:
        conf: GroupedConfig
        try:
            conf = GroupedConfig.selected
        except Exception:
            logging.error("Dynamic config could not be loaded:")
            logging.error(traceback.format_exc())
            logging.warn("Using default config instead.")
            return DEFAULT_CONFIG
        if conf is None:
            logging.error("No dynamic config selected in the database!")
            logging.warn("Using default config instead.")
            return DEFAULT_CONFIG
        return conf

    def __get__(self, instance, owner):
        return self.fget(owner)


DynamicConfig = _DynamicConfigMeta()
