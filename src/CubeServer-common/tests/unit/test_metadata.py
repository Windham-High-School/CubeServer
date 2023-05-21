"""
Tests for CubeServer-common metadata.
"""

import pytest
import re
from datetime import datetime
from cubeserver_common.metadata import LICENSE, LICENSE_FULL, VERSION, TIMESTAMP, AUTHORS

# Utility functions
def is_semver(version: str):
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))

def is_datetime_stamp(timestamp: str):
    try:
        datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
        return True
    except ValueError:
        return False

# Tests
def test_license():
    assert isinstance(LICENSE, str)
    assert LICENSE == 'MIT'

def test_license_full():
    assert isinstance(LICENSE_FULL, str)
    assert LICENSE_FULL.lstrip().startswith('MIT License')

def test_version():
    assert isinstance(VERSION, str)
    if 'dev' in VERSION:
        print("WARNING: VERSION contains 'dev'")
        assert is_semver(VERSION[:-4]), "VERSION is not a valid semantic version"
    else:
        assert is_semver(VERSION), "VERSION is not a valid semantic version"

def test_timestamp():
    assert isinstance(TIMESTAMP, str)
    assert is_datetime_stamp(TIMESTAMP), "TIMESTAMP is not a valid datetime stamp"

def test_authors():
    assert isinstance(AUTHORS, dict)
    assert 'Joseph R. Freeston' in AUTHORS
