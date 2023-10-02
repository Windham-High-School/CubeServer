"""For encoding/decoding tuples, which are unsupported by json and bson otherwise

Limitations:
Assumes the type of the tuple's elements is uniform
"""

from typing import Optional
from bson.codec_options import TypeCodec

__all__ = ['TupleCodec']

class TupleCodec(TypeCodec):
    """Codec for encoding a tuple into bson
    """

    python_type = tuple
    bson_type = list

    def __init__(self, type_codec: Optional[TypeCodec] = None):
        """Optionally specify a TypeCodec if the list contains
        non-directly-bson-compatible types
        """
        
        self.type_codec = type_codec

    def transform_python(self, value: tuple):
        if self.type_codec is None:
            return list(value)
        return [
            self.type_codec.transform_python(element)
            for element in value
        ]

    def transform_bson(self, value) -> tuple:
        if self.type_codec is None:
            return tuple(value)
        return tuple(
            self.type_codec.transform_bson(element)
            for element in value
        )
