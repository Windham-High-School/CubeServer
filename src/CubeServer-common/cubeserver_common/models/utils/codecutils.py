"""Utilities for database codecs
"""

from typing import Type, Self
from abc import ABC, abstractmethod
import json
import bson
from bson.codec_options import TypeCodec


__all__ = ["Encodable", "EncodableCodec"]


class Encodable(ABC):
    """An abstract class for classes that contain codec data"""

    @abstractmethod
    def __init__(self) -> None:
        """Encodables must have a no-argument constructor that just
        populates default values for decoding purposes."""
        super().__init__()

    @abstractmethod
    def encode(self) -> dict:
        """Encodes an Encodable object into a plain old, bson-able
        dictionary"""

    @classmethod
    @abstractmethod
    def decode(cls, value: dict) -> Self:
        """Decodes a dictionary into an Encodable object"""

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Encodable):
            return False
        return self.encode() == __value.encode()

    def to_json(self) -> str:
        """Returns a JSON representation of this Encodable"""
        return json.dumps(self.encode())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Returns an Encodable object from a JSON representation"""
        return cls.decode(json.loads(json_str))

    def to_bson(self) -> bytes:
        """Returns a BSON representation of this Encodable"""
        return bson.encode(self.encode())

    @classmethod
    def from_bson(cls, bson_str: bytes) -> Self:
        """Returns an Encodable object from a BSON representation"""
        return cls.decode(bson.decode(bson_str))


class EncodableCodec(TypeCodec):
    """A TypeCodec for PyMongoModel objects"""

    bson_type = dict

    def __init__(self, encodable_class: Type[Encodable]):
        self.encodable = encodable_class

    @property
    def python_type(self) -> Type[Encodable]:
        return self.encodable

    def transform_python(self, value: Encodable) -> dict:
        """Encodes a PyMongoModel object into a plain old, bson-able and
        json-able dictionary"""
        return value.encode()

    def transform_bson(self, value: dict) -> Encodable:
        """Decodes a dictionary into a PyMongoModel object"""
        return self.python_type.decode(value)
