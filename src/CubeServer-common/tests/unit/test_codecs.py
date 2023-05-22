"""Unit tests for different codecs"""

from typing import Dict, List
from bson import ObjectId
from enum import Enum
from cubeserver_common.models.utils.modelutils import DummyCodec
from cubeserver_common.models.utils.complexdictcodec import ComplexDictCodec
from cubeserver_common.models.utils.enumcodec import EnumCodec
from cubeserver_common.models.utils.listcodec import ListCodec

class TestDummyCodec:
    def test_python_type(self):
        codec = DummyCodec(type_class=str)
        assert codec.python_type == str

    def test_bson_type(self):
        codec = DummyCodec(type_class=str)
        assert codec.bson_type == str

    def test_transform_python(self):
        codec = DummyCodec(type_class=str)
        value = 'foo'
        assert codec.transform_python(value) == value

    def test_transform_bson(self):
        codec = DummyCodec(type_class=str)
        value = 'foo'
        assert codec.transform_bson(value) == value

class TestComplexDictCodec:
    def test_python_type(self):
        codec = ComplexDictCodec(key_codec=DummyCodec(ObjectId), value_codec=DummyCodec(str))
        assert codec.python_type == Dict[ObjectId, str]

    def test_bson_type(self):
        codec = ComplexDictCodec(key_codec=DummyCodec(ObjectId), value_codec=DummyCodec(str))
        assert codec.bson_type == dict

    def test_transform(self):
        codec = ComplexDictCodec(key_codec=DummyCodec(ObjectId), value_codec=DummyCodec(str))
        bson_value = {ObjectId('5f9d7f3c8b4b4f0d9c7d3c6f'): 'foo', ObjectId('5f9d7f3c8b4b4f0d9c7d3c70'): 'bar'}
        python_value = {ObjectId('5f9d7f3c8b4b4f0d9c7d3c6f'): 'foo', ObjectId('5f9d7f3c8b4b4f0d9c7d3c70'): 'bar'}
        assert codec.transform_bson(bson_value) == python_value
        assert codec.transform_python(python_value) == bson_value

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

class TestEnumCodec:
    def test_python_type(self):
        codec = EnumCodec(enum_class=Color)
        assert codec.python_type == Color

    def test_bson_type(self):
        codec = EnumCodec(enum_class=Color)
        assert codec.bson_type == codec.value_class

    def test_transform_python(self):
        codec = EnumCodec(enum_class=Color)
        value = Color.RED
        assert codec.transform_python(value) == value.value

    def test_transform_bson(self):
        codec = EnumCodec(enum_class=Color)
        value = 2
        assert codec.transform_bson(value) == Color.GREEN

class TestListCodec:
    def test_python_type(self):
        codec = ListCodec(type_codec=EnumCodec(enum_class=Color))
        assert codec.python_type == List[Color] or codec.python_type == list

    def test_bson_type(self):
        codec = ListCodec(type_codec=EnumCodec(enum_class=Color))
        assert codec.bson_type == list

    def test_transform_python(self):
        codec = ListCodec(type_codec=EnumCodec(enum_class=Color))
        python_value = [Color.RED, Color.GREEN]
        bson_value = [1, 2]
        assert codec.transform_python(python_value) == bson_value

    def test_transform_bson(self):
        codec = ListCodec(type_codec=EnumCodec(enum_class=Color))
        python_value = [Color.RED, Color.GREEN]
        bson_value = [1, 2]
        assert codec.transform_bson(bson_value) == python_value
