"""Environment variables and database-stored configuration"""

import logging
from typing import Any
import traceback
import time

from .environ import EnvConfig, EnvConfigError
from ..models.grouped_config import GroupedConfig
from .config_default import DEFAULT_CONFIG

__all__ = [
    "EnvConfig",
    "EnvConfigError",
    "DEFAULT_CONFIG",
    "GroupedConfig",
    "DynamicConfig",
]


class _DynamicConfig_meta(dict[str, dict[str, Any]]):
    """Configuration not defined in the environment, but by the admin user
    This will stay cached and must be updated from the database as necessary
    """

    @staticmethod
    def __get_fresh_from_db() -> GroupedConfig:
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

    def reload(self) -> None:
        """Reloads the configuration from the database.
        This should be run on each thread periodically.
        """
        new_config: GroupedConfig = _DynamicConfig_meta.__get_fresh_from_db()
        self.update(
            {
                category.name: {field.name: field.value for field in category}
                for category in new_config
            }
        )
        logging.debug("Loaded config")
        logging.debug(self)

    def __setitem__(self, __key: str, __value: Any) -> None:
        raise TypeError(
            "Config is immutable. To make changes, do so through the ORM model, GroupedConfig."
        )

    def __getitem__(self, __key: str) -> dict[str, Any]:
        try:
            return super().__getitem__(__key)
        except KeyError:
            self.reload()
            return super().__getitem__(__key)


DynamicConfig = _DynamicConfig_meta()
