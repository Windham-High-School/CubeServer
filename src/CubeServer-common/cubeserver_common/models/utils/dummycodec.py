"""A dummy, fallback codec that effectively does nothing."""

from typing import Any, Type
from bson.codec_options import TypeCodec

__all__ = ["DummyCodec"]


class DummyCodec(TypeCodec):
    """Dummy Codec.
    Does nothing as far as encoding/decoding.
    Returns what was given.
    No questions asked.
    """

    def __init__(self, type_class: Type[Any] = str):
        self.type_class = type_class

    @property
    def python_type(self):
        return self.type_class

    @property
    def bson_type(self):
        return self.type_class

    def transform_python(self, value):
        return value

    def transform_bson(self, value):
        return value
