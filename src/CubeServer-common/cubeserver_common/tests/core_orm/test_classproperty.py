"""Tests the `classproperty` class,
a workaround for Python 3.11 no longer supporting classmethod properties
"""

from cubeserver_common.models.utils import classproperty


def test_classproperty():
    """Simple test of classproperty"""
    class MyTestClass:
        _CLASS_CONST = 1.57

        @classmethod
        @classproperty
        def my_prop(cls):
            return cls._CLASS_CONST * 2
    
    assert MyTestClass.my_prop == 3.14

