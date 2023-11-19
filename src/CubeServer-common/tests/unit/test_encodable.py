"""Tests for Encodable and EncodableCodec."""

from bson import ObjectId
from enum import Enum
from typing import List, Optional
from cubeserver_common.models.utils.modelutils import Encodable, EncodableCodec


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
            foo="foo", bar=42, baz=["baz"], qux=ObjectId(), enum=MyEnum.FOO
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
