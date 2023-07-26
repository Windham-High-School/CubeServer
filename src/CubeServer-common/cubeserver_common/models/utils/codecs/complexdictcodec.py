"""For encoding/decoding "complex dictionaries" into bson

- "complex dictionary" meaning a dictionary with non-bson-compatible types
"""

from enum import Enum
from typing import Type, Dict
from bson import _BUILT_IN_TYPES as BSON_TYPES
from bson.codec_options import TypeCodec

from .dummycodec import DummyCodec

__all__ = ['ComplexDictCodec']

class ComplexDictCodec(TypeCodec):
    """Codec for encoding a complex dictionary into bson
    """

    def __init__(
        self,
        key_codec: TypeCodec = DummyCodec,
        value_codec: TypeCodec = DummyCodec
    ):
        """Provide codecs for the key and values"""

        self.key_codec = key_codec
        self.value_codec = value_codec

    @property
    def python_type(self):
        return Dict[self.key_codec.python_type, self.value_codec.python_type]

    @property
    def bson_type(self):
        return dict

    def transform_python(self, value: dict):
        return {
            self.key_codec.transform_python(k): self.value_codec.transform_python(v)
            for k,v in value.items()
        }

    def transform_bson(self, value) -> dict:
        return {
            self.key_codec.transform_bson(k): self.value_codec.transform_bson(v)
            for k,v in value.items()
        }
