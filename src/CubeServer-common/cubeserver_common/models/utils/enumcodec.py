"""For encoding/decoding Enums into bson

Limitations:
Only works with Enums that have bson-compatible typed values
Enum values must all be of the same type
"""

from enum import Enum
from typing import Type
from bson import _BUILT_IN_TYPES as BSON_TYPES
from bson.codec_options import TypeCodec

__all__ = ['EnumCodec']

class EnumCodec(TypeCodec):
    """Codec for encoding a generic Enum into bson
    *This assumes the Enum only contains primitive/built-in/bson-compatible
    types*"""

    def __init__(self, enum_class: Type[Enum], value_class: type = ...):
        """Specify the enum class to encode/decode
        and the type of the Enum's values.
        The value class MUST be DIRECTLY bson-compatible!"""
        if value_class is ...:  # If we need to figure that out...
            value_class = type(next(iter(enum_class)).value)
        assert value_class in BSON_TYPES, \
            "Enum values must be DIRECTLY bson-compatible."
        assert all(isinstance(val.value, value_class) for val in enum_class), \
            "Enum values must all have the same type, as specified."

        self.enum_class = enum_class
        self.value_class = value_class

    @property
    def python_type(self):
        return self.enum_class

    @property
    def bson_type(self):
        return self.value_class

    def transform_python(self, value: Enum):
        return value.value

    def transform_bson(self, value) -> Enum:
        return self.python_type(value)
