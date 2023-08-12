"""Tests for Encodable and EncodableCodec."""

from bson import ObjectId
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from cubeserver_common.models.utils.autoencodable import AutoEncodable


class MyEnum(Enum):
    """A simple and meaningless enum to use for testing"""

    FOO = "foo"
    BAR = "bar"


class MyAutoEncodable(AutoEncodable):
    """AutoEncodable demo class. Simple and plain."""

    def __init__(
        self,
        foo: str = "foo",
        bar: int = 42,
        baz: Optional[List[str]] = None,
        qux: ObjectId = ObjectId(),
        enum: MyEnum = MyEnum.FOO,
    ):
        self.foo = foo
        self.bar = bar
        self.baz = baz
        self.qux = qux
        self.enum = enum


@dataclass
class MyDataclassAutoEncodable(AutoEncodable):
    """AutoEncodable demo class that uses the dataclass decorator"""

    foo: str = "foo"
    bar: int = 42
    baz: Optional[List[str]] = None
    qux: ObjectId = ObjectId()
    enum: MyEnum = MyEnum.FOO


def test_encodable_equality():
    """Tests the __eq__ method of AutoEncodables"""
    obj_id = ObjectId()
    encodable = MyAutoEncodable(
        foo="foo", bar=42, baz=["baz"], qux=obj_id, enum=MyEnum.FOO
    )
    # Identical to encodable:
    encodable2 = MyAutoEncodable(
        foo="foo", bar=42, baz=["baz"], qux=obj_id, enum=MyEnum.FOO
    )
    # Different `baz`:
    encodable3 = MyAutoEncodable(
        foo="foo", bar=42, baz=["foo", "bar", "baz"], qux=obj_id, enum=MyEnum.FOO
    )
    assert encodable == encodable
    assert encodable is not encodable2
    assert encodable == encodable2
    assert encodable2 != encodable3


def test_encodable():
    """Tests basic funtionality of AutoEncodable"""
    # Create test object:
    obj_id = ObjectId()
    encodable = MyAutoEncodable(
        foo="foo", bar=42, baz=["baz"], qux=obj_id, enum=MyEnum.FOO
    )
    # Test expected encode functionality:
    assert encodable.encode() == {
        "foo": ("None", "foo"),
        "bar": ("None", 42),
        "baz": ("None", ["baz"]),
        "qux": ("None", obj_id),
        "enum": ("test_autoencodable.MyEnum", "foo"),
    }
    # Test expected decode functionality:
    assert (
        MyAutoEncodable.decode(
            {
                "foo": ("None", "foo"),
                "bar": ("None", 42),
                "baz": ("None", ["baz"]),
                "qux": ("None", obj_id),
                "enum": ("test_autoencodable.MyEnum", "foo"),
            }
        )
        == encodable
    )


def test_dataclass_encodable():
    """Tests basic funtionality of AutoEncodable"""
    # Create test object:
    obj_id = ObjectId()
    encodable = MyDataclassAutoEncodable(
        foo="foo", bar=42, baz=["baz"], qux=obj_id, enum=MyEnum.FOO
    )
    # Test expected encode functionality:
    assert encodable.encode() == {
        "foo": ("None", "foo"),
        "bar": ("None", 42),
        "baz": ("None", ["baz"]),
        "qux": ("None", obj_id),
        "enum": ("test_autoencodable.MyEnum", "foo"),
    }
    # Test expected decode functionality:
    assert (
        MyDataclassAutoEncodable.decode(
            {
                "foo": ("None", "foo"),
                "bar": ("None", 42),
                "baz": ("None", ["baz"]),
                "qux": ("None", obj_id),
                "enum": ("test_autoencodable.MyEnum", "foo"),
            }
        )
        == encodable
    )


# def test_encodable_codec():
#     obj_id = ObjectId()
#     document = {
#         'foo': 'foo',
#         'bar': 42,
#         'baz': ['baz'],
#         'qux': str(obj_id),
#         'enum': 'foo',
#     }
#     encodable = MyAutoEncodable.decode(document)
#     assert encodable.foo == 'foo'
#     assert encodable.bar == 42
#     assert encodable.baz == ['baz']
#     assert encodable.qux == obj_id
#     assert encodable.enum == MyEnum.FOO
#     # Check raw encoding:
#     assert MyAutoEncodable.encode(encodable) == document
#     # Check equality:
#     assert encodable == encodable
#     assert encodable == MyAutoEncodable(foo='foo', bar=42, baz=['baz'], qux=obj_id, enum=MyEnum.FOO)
#     assert encodable != MyAutoEncodable(foo='foo', bar=42, baz=['baz'], qux=obj_id, enum=MyEnum.BAR)
#     assert encodable is not MyAutoEncodable(foo='foo', bar=42, baz=['baz'], qux=obj_id, enum=MyEnum.FOO)
