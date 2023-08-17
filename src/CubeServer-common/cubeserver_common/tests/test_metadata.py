"""
Tests for CubeServer-common metadata.
"""

from cubeserver_common.metadata import LICENSE, LICENSE_FULL, AUTHORS, SERVER_NAME


# Tests
def test_license():
    assert isinstance(LICENSE, str)
    assert LICENSE == "MIT"


def test_license_full():
    assert isinstance(LICENSE_FULL, str)
    assert len(LICENSE_FULL) > len(LICENSE)
    assert LICENSE_FULL.lstrip().startswith("MIT License")

def test_server_name():
    assert isinstance(SERVER_NAME, str)
    assert "CubeServer" in SERVER_NAME

def test_authors():
    assert isinstance(AUTHORS, dict)
