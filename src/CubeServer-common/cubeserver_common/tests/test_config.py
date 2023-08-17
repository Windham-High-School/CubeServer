"""
Tests for CubeServer-common environment variables.
"""

from cubeserver_common.models.utils import Encodable
from cubeserver_common.config import EnvConfig, DEFAULT_CONFIG


# Tests
def test_validate_envconf():
    EnvConfig.validate()


def test_default_config_static():
    assert isinstance(DEFAULT_CONFIG, Encodable)
