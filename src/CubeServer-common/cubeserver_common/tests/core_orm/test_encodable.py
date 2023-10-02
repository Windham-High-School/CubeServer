"""Tests for Encodable and EncodableCodec."""

from bson import ObjectId
from enum import Enum
from typing import List, Optional
from cubeserver_common.models.utils.codecutils import Encodable, EncodableCodec


class MyEnum(Enum):
    FOO = "foo"
    BAR = "bar"


class MyEncodable(Encodable):
    def __init__(
        self, foo: str, bar: int, baz: Optional[List[str]], qux: ObjectId, enum: MyEnum
    ):
        self.foo = foo
        self.bar = bar
        self.baz = baz
        self.qux = qux
        self.enum = enum

    def encode(self) -> dict:
        return {
            "foo": self.foo,
            "bar": self.bar,
            "baz": self.baz,
            "qux": str(self.qux),
            "enum": self.enum.value,
        }

    @classmethod
    def decode(cls, document: dict) -> "MyEncodable":
        return MyEncodable(
            foo=document["foo"],
            bar=document["bar"],
            baz=document.get("baz"),
            qux=ObjectId(document["qux"]),
            enum=MyEnum(document["enum"]),
        )

    @classmethod
    def test_encodable(cls) -> "MyEncodable":
        return MyEncodable(
            foo="foo",
            bar=42,
            baz=["baz"],
            qux=ObjectId("64d691a0ada6bf5f1b868c1b"),
            enum=MyEnum.FOO,
        )


def test_encodable():
    obj_id = ObjectId()
    encodable = MyEncodable(foo="foo", bar=42, baz=["baz"], qux=obj_id, enum=MyEnum.FOO)
    assert encodable.encode() == {
        "foo": "foo",
        "bar": 42,
        "baz": ["baz"],
        "qux": str(obj_id),
        "enum": "foo",
    }
    assert encodable == encodable


def test_encodable_codec():
    obj_id = ObjectId()
    document = {
        "foo": "foo",
        "bar": 42,
        "baz": ["baz"],
        "qux": str(obj_id),
        "enum": "foo",
    }
    encodable = MyEncodable.decode(document)
    assert encodable.foo == "foo"
    assert encodable.bar == 42
    assert encodable.baz == ["baz"]
    assert encodable.qux == obj_id
    assert encodable.enum == MyEnum.FOO
    # Check raw encoding:
    assert MyEncodable.encode(encodable) == document
    # Check EncodableCodec:
    assert (
        EncodableCodec(MyEncodable).transform_python(
            EncodableCodec(MyEncodable).transform_bson(document)
        )
        == document
    )
    assert EncodableCodec(MyEncodable).transform_bson(document) == encodable


def test_json():
    """Tests the json serialization functionality"""
    json_str = '{"foo": "foo", "bar": 42, "baz": ["baz"], "qux": "64d691a0ada6bf5f1b868c1b", "enum": "foo"}'  # noqa: E501
    encodable = MyEncodable.test_encodable()
    assert encodable.to_json() == json_str
    assert MyEncodable.from_json(json_str) == encodable


def test_bson():
    """Tests the bson serialization functionality"""
    bson_str = b"`\x00\x00\x00\x02foo\x00\x04\x00\x00\x00foo\x00\x10bar\x00*\x00\x00\x00\x04baz\x00\x10\x00\x00\x00\x020\x00\x04\x00\x00\x00baz\x00\x00\x02qux\x00\x19\x00\x00\x0064d691a0ada6bf5f1b868c1b\x00\x02enum\x00\x04\x00\x00\x00foo\x00\x00"  # noqa: E501
    encodable = MyEncodable.test_encodable()
    assert encodable.to_bson() == bson_str
    assert MyEncodable.from_bson(bson_str) == encodable
