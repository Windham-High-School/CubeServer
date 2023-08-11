"""
Tests for CubeServer-common metadata.
"""

import pytest
import re
from datetime import datetime
from cubeserver_common.metadata import LICENSE, LICENSE_FULL, AUTHORS


# Tests
def test_license():
    assert isinstance(LICENSE, str)
    assert LICENSE == "MIT"


def test_license_full():
    assert isinstance(LICENSE_FULL, str)
    assert LICENSE_FULL.lstrip().startswith("MIT License")


def test_authors():
    assert isinstance(AUTHORS, dict)
