"""For encoding/decoding lists

Limitations:
Assumes the type of the list's elements is uniform
"""

from typing import Optional
from bson.codec_options import TypeCodec

__all__ = ['ListCodec']

class ListCodec(TypeCodec):
    """Codec for encoding a list into bson
    """

    python_type = list
    bson_type = list

    def __init__(self, type_codec: Optional[TypeCodec] = None):
        """Optionally specify a TypeCodec if the list contains
        non-directly-bson-compatible types
        """
        
        self.type_codec = type_codec

    def transform_python(self, value: list):
        if self.type_codec is None:
            return value
        return [
            self.type_codec.transform_python(element)
            for element in value
        ]

    def transform_bson(self, value) -> list:
        if self.type_codec is None:
            return value
        return [
            self.type_codec.transform_bson(element)
            for element in value
        ]
