"""Environment variables and database-stored configuration"""

from typing import Any
import traceback

from loguru import logger

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
            logger.error("Dynamic config could not be loaded:")
            logger.error(traceback.format_exc())
            logger.warning("Using default config instead of loading from db.")
            return DEFAULT_CONFIG
        if conf is None:
            logger.error("No dynamic config selected in the database!")
            logger.warning("Saving default config to db.")
            new_config = DEFAULT_CONFIG.clone()
            new_config.selected = True
            new_config.save()
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
        logger.debug(f'Loaded config "{new_config.name}"')

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
