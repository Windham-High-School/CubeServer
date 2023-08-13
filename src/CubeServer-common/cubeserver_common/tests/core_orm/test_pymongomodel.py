"""Unit tests for PyMongoModel - object-mapping
"""

import dataclasses
from enum import Enum
from typing import Optional, List
import pytest
from bson import ObjectId
from cubeserver_common.models.utils import (
    PyMongoModel,
    EncodableCodec,
    Encodable,
    BSON_TYPES,
)

import mongomock


@pytest.fixture()
def mock_mongo():
    """Establishes a fake Mongo instance for testing"""
    mc = mongomock.MongoClient()
    yield mc
    mc.close()


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
        return MyEncodable(foo="foo", bar=73, baz=["baz"], enum=MyEnum.FOO)


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


@pytest.fixture(autouse=True)
def initorm(mock_mongo):
    """Initializes MyModel and the db and stuff"""
    PyMongoModel.update_mongo_client(mock_mongo)
    MyModel.__init_subclass__()
    yield


def test_create():
    """Tests creation and encoding of PyMongoModel objects"""
    model = MyModel(foo="foo", bar=73, baz=["baz"], qux=MyEnum.FOO)
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
    assert model._id == model.id == model.id_secondary


def test_find_by_id():
    """Test identifying by id"""
    model = MyModel(foo="foobar", bar=73, baz=["baz"], qux=MyEnum.FOO)
    assert hasattr(model, "weird")
    model.save()
    found_model = MyModel.find_by_id(model._id)
    assert found_model._id == model._id


def test_update():
    """Test updating an existing entry in the database"""
    model1 = MyModel(foo="foo", bar=73, baz=["baz"], qux=MyEnum.FOO)
    model1.save()

    model1_found = MyModel.find_by_id(model1.id)
    model1_found.qux = MyEnum.BAR
    model1_found.save()

    # Sanity check
    assert model1.id == model1_found.id

    model1_found_again = MyModel.find_by_id(model1.id)
    assert model1_found.qux == model1_found_again.qux == MyEnum.BAR
    assert model1_found_again != model1

    assert model1.find_self() == model1_found_again


def test_find():
    """Tests finding and filtering with queries"""
    model1 = MyModel(foo="foo", bar=73, baz=["baz"], qux=MyEnum.FOO)
    model2 = MyModel(foo="bar", bar=73, baz=["baz"], qux=MyEnum.FOO)
    model3 = MyModel(foo="123", bar=42, baz=["baz"], qux=MyEnum.BAR)
    model1.save()
    model2.save()
    model3.save()

    # Legacy, manual dict queries:
    found_models = MyModel.find({"foo": {"$in": ["foo", "bar"]}})
    for model in found_models:
        print(model.foo)
    assert len(found_models) == 2
    assert MyModel.find_by_id(model3.id).qux == MyEnum.BAR
    assert len(MyModel.find({"bar": 42})) == 1
    assert MyModel.find_one({"bar": 42}) == MyModel.find({"bar": 42})[0]
    assert MyModel.find_one({"bar": 234}) is None

    # Better queries:
    assert MyModel.find_one({"bar": 42}) == MyModel.find_one(bar=42)
    assert MyModel.find_one(bar=42) == MyModel.find_one(qux=MyEnum.BAR)
    assert MyModel.find_one(bar=42) == MyModel.find(bar=42)[0]
    assert MyModel.find_one(bar=73, foo="bar") == model2




def test_delete():
    """Tests removing an object from the database"""
    model = MyModel(foo="foobarbaz", bar=73, baz=["baz", "bar", "foo"], qux=MyEnum.FOO)
    model.save()
    id = model.id
    assert MyModel.find_by_id(id) is not None
    model.remove()
    assert MyModel.find_by_id(id) is None

def test_dataclasses_simple():
    """Tests dataclasses method"""

    @dataclasses.dataclass
    class MyModelDc(PyMongoModel):
        a: int = 1
    
    # Create objects
    my_obj   = MyModelDc()
    my_obj_2 = MyModelDc(a=2)

    assert my_obj.a   == 1
    assert my_obj_2.a == 2

    # Save:
    my_obj.save()
    my_obj_2.save()

    assert len(MyModelDc.find()) == 2
    my_obj.remove()
    assert len(MyModelDc.find()) == 1
    assert MyModelDc.find_one() == my_obj_2

def test_dataclasses_complex():
    """Tests dataclasses method"""

    @dataclasses.dataclass
    class MyModelDc(PyMongoModel):
        a: tuple[str] = ('Hola', 'Adios')
        b: Enum = MyEnum.FOO
    
    # Create objects
    my_obj   = MyModelDc()
    my_obj_2 = MyModelDc(b = MyEnum.BAR)

    assert my_obj.b   == MyEnum.FOO
    assert my_obj_2.b == MyEnum.BAR

    # Save:
    my_obj.save()
    my_obj_2.save()

    print(my_obj.to_json())

    assert MyModelDc.find_one(b=MyEnum.BAR) == my_obj_2  #*
    assert len(MyModelDc.find()) == 2
    assert MyModelDc.find_one(b=MyEnum.FOO) is not None
    my_obj.remove()
    assert MyModelDc.find_one(b=MyEnum.FOO) is None
    assert len(MyModelDc.find()) == 1
    assert MyModelDc.find_one() == my_obj_2  #*
    assert MyModelDc.find_one().a == ('Hola', 'Adios')
