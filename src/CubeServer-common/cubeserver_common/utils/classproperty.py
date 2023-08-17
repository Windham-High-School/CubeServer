"""Workaround class to replace simple functionality of classmethod properties in python 3.11+

Usage: (see unit test, ../../tests/core_orm/test_classpropery.py)

class MyTestClass:
    _CLASS_CONST = 1.57

    @classmethod
    @classproperty
    def my_prop(cls):
        return cls._CLASS_CONST * 2

assert MyTestClass.my_prop == 3.14
"""

__all__ = ['classproperty']

class classproperty:
    """Decorator class to implement the most basic functionality of @property,
    but for classmethods"""
    def __init__(self, func):
        self.fget = (func)
    def __get__(self, instance, owner):
        return self.fget(owner)
