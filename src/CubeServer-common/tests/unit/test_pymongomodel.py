import pytest
from bson import ObjectId
from enum import Enum
from typing import Optional, List
from pymongo.errors import PyMongoError
from cubeserver_common.models.utils.modelutils import (
    PyMongoModel,
    EncodableCodec,
    Encodable,
    BSON_TYPES,
)

from mongomock import MongoClient as MockMongoClient

# Create a mock MongoClient instance
client = MockMongoClient()
PyMongoModel.update_mongo_client(client)


class MyEnum(Enum):
    FOO = "foo"
    BAR = "bar"


class MyEncodable(Encodable):
    def __init__(self, foo: str, bar: int, baz: Optional[List[str]], enum: MyEnum):
        self.foo = foo
        self.bar = bar
        self.baz = baz
        self.enum = enum

    def encode(self) -> dict:
        return {
            "foo": self.foo,
            "bar": self.bar,
            "baz": self.baz,
            "enum": self.enum.value,
        }

    @classmethod
    def decode(cls, document: dict) -> "MyEncodable":
        return MyEncodable(
            foo=document["foo"],
            bar=document["bar"],
            baz=document.get("baz"),
            enum=MyEnum(document["enum"]),
        )

    @classmethod
    def test_encodable(cls) -> "MyEncodable":
        return MyEncodable(foo="foo", bar=42, baz=["baz"], enum=MyEnum.FOO)


class MyModel(PyMongoModel):
    def __init__(
        self, foo: str = "", bar: int = 0, baz: list = [], qux: MyEnum = MyEnum.FOO
    ):
        super().__init__()
        self.foo = foo
        self.bar = bar
        self.baz = baz
        self.qux = qux
        self.register_field(
            "weird",
            value=MyEncodable.test_encodable(),
            custom_codec=EncodableCodec(MyEncodable),
        )


def test_create():
    model = MyModel(foo="foo", bar=42, baz=["baz"], qux=MyEnum.FOO)
    assert isinstance(model, MyModel)
    assert isinstance(model.weird, MyEncodable)
    assert model.foo == "foo"
    assert model.weird.encode() == MyEncodable.test_encodable().encode()
    # Ensure that the model is fully BSON-able
    assert isinstance(model.encode(), dict)

    def assert_bson_types(document):
        for key, value in document.items():
            if isinstance(value, dict):
                assert_bson_types(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        assert_bson_types(item)
                    else:
                        assert isinstance(item, BSON_TYPES)
            else:
                assert isinstance(value, BSON_TYPES)

    assert_bson_types(model.encode())
    model.save()
    assert isinstance(model._id, ObjectId)


def test_find_by_id():
    model = MyModel(foo="foobar", bar=42, baz=["baz"], qux=MyEnum.FOO)
    assert hasattr(model, "weird")
    model.save()
    found_model = MyModel.find_by_id(model._id)
    assert found_model._id == model._id


def test_find():
    model1 = MyModel(foo="foo", bar=42, baz=["baz"], qux=MyEnum.FOO)
    model2 = MyModel(foo="bar", bar=42, baz=["baz"], qux=MyEnum.FOO)
    model3 = MyModel(foo="123", bar=42, baz=["baz"], qux=MyEnum.BAR)
    model1.save()
    model2.save()
    model3.save()
    found_models = MyModel.find({"foo": {"$in": ["foo", "bar"]}})
    assert len(found_models) == 2
    assert MyModel.find_by_id(model3._id).qux == MyEnum.BAR


def test_delete():
    model = MyModel(foo="foobarbaz", bar=42, baz=["baz", "bar", "foo"], qux=MyEnum.FOO)
    model.save()
    model.remove()
    assert MyModel.find_by_id(model._id) is None
