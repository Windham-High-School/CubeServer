"""Utilities for database codecs
"""

from bson.codec_options import TypeCodec
from abc import ABC, abstractmethod
from typing import Type, Self


class _Encoder(ABC):
    @abstractmethod
    def encode(self) -> dict:
        """Encodes an Encodable object into a plain old, bson-able
        dictionary"""

    @classmethod
    @abstractmethod
    def decode(cls, value: dict) -> Self:
        """Decodes a dictionary into an Encodable object"""

class EncodableCodec(TypeCodec):
    """A TypeCodec for PyMongoModel objects"""

    bson_type = dict

    def __init__(self, encodable: Type[_Encoder]):
        self.encodable = encodable

    @property
    def python_type(self) -> Type[_Encoder]:
        return self.encodable

    def transform_python(self, value: _Encoder) -> dict:
        """Encodes a PyMongoModel object into a plain old, bson-able
        dictionary"""
        return value.encode()

    def transform_bson(self, value: dict) -> _Encoder:
        """Decodes a dictionary into a PyMongoModel object"""
        return self.python_type.decode(value)

class Encodable(_Encoder):
    """An abstract class for classes that contain codec data"""

    @abstractmethod
    def __init__(self) -> None:
        """Encodables must have a no-argument constructor that just
        populates default values for decoding purposes."""
        super().__init__()

    # From _Encoder:
    @abstractmethod
    def encode(self) -> dict:
        """Encodes an Encodable object into a plain old, bson-able
        dictionary"""

    @classmethod
    @abstractmethod
    def decode(cls, value: dict) -> _Encoder:
        """Decodes a dictionary into an Encodable object"""

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Encodable):
            return False
        return self.encode() == __value.encode()
