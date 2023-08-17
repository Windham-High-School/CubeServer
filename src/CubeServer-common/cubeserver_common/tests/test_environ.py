"""
Tests for CubeServer-common environment variables.
"""

from cubeserver_common.environ import EnvConfig


# Tests
def test_validate():
    EnvConfig.validate()
