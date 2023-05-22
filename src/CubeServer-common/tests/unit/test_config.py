"""
Unit tests for the config module.
"""

import hashlib
import os
import re

from cubeserver_common import config


def test_password_hash_algorithm():
    assert config.PASSWORD_HASH_ALGORITHM in hashlib.algorithms_available

def test_crypto_hash_algorithm():
    assert config.CRYPTO_HASH_ALGORITHM in hashlib.algorithms_available

def test_temp_path():
    assert isinstance(config.TEMP_PATH, str)

def test_contributors_yaml():
    assert isinstance(config.CONTRIBUTORS_YAML, str)

def test_comment_filter_profanity():
    assert isinstance(config.COMMENT_FILTER_PROFANITY, bool)

def test_encoding():
    assert isinstance(config.ENCODING, str)

def test_secret_key_file():
    assert isinstance(config.SECRET_KEY_FILE, str)

def test_secret_key_file_encoding():
    assert isinstance(config.SECRET_KEY_FILE_ENCODING, str)

def test_secret_key_file():
    assert isinstance(config.SECRET_KEY_FILE, str)

def test_password_hash_algorithm_exists():
    assert config.PASSWORD_HASH_ALGORITHM in hashlib.algorithms_available
    
def test_crypto_hash_algorithm_exists():
    assert config.CRYPTO_HASH_ALGORITHM in hashlib.algorithms_available
    
def test_temp_path_exists():
    assert os.path.exists(config.TEMP_PATH)
    
def test_team_max_update_length():
    assert isinstance(config.TEAM_MAX_UPDATE_LENGTH, int)
    
def test_beacon_team_name():
    assert isinstance(config.BEACON_TEAM_NAME, str)
    
def test_reference_team_name():
    assert isinstance(config.REFERENCE_TEAM_NAME, str)
    
def test_reference_port_range():
    assert isinstance(config.REFERENCE_PORT_RANGE, tuple)
    assert len(config.REFERENCE_PORT_RANGE) == 2
    assert isinstance(config.REFERENCE_PORT_RANGE[0], int)
    assert isinstance(config.REFERENCE_PORT_RANGE[1], int)
    
def test_reference_command_port():
    assert isinstance(config.REFERENCE_COMMAND_PORT, int)
