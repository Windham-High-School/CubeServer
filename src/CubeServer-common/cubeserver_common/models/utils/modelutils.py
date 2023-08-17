"""Some utility classes to help with object mapping

This is not thread safe. Exercise caution if accessing the same instance from multiple threads.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Mapping, Optional, Tuple, Type, cast, Self
from functools import lru_cache
import warnings
from bson import ObjectId
from json import loads
from bson.codec_options import TypeCodec, TypeRegistry
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection

from cubeserver_common.utils import classproperty

from .codecs.dummycodec import DummyCodec
from .codecs.enumcodec import EnumCodec
from .autoencodable import AutoEncodable


__all__ = ["PyMongoModel", "ASCENDING", "DESCENDING"]


def _locatable_name(type_to_name: type) -> str:
    """Returns a string that can be used in reverse with pydoc.locate"""
    module = type_to_name.__module__
    if "builtin" in module:
        return type_to_name.__name__
    return module + "." + type_to_name.__name__

@classproperty
def _collection_def() -> Collection:
    """Define the Mongodb collection in your class.
    Use the PyMongoModel.model_type_registry as the type registry.
    """
    raise ValueError(
        "The mongo client has not been given to this class.\nPlease call update_mongo_client."
    )

class PyMongoModel(AutoEncodable, ABC):
    """A class for easy object-mapping to bson.
    Extend this class for any classes that describe a type of document."""

    mongo: Optional[MongoClient] = None
    collection: Collection = _collection_def

    __collection_name: Optional[str] = None

    @classmethod
    def update_mongo_client(cls, mongo_client: Optional[MongoClient]):
        """Sets the MongoClient reference in PyMongoModel, which is then
        used by any models that extend this class."""
        cls.mongo = mongo_client
        # If this method is called post-__init_subclass__
        if cls.__collection_name is not None:
            cls.set_collection_name(cls.__collection_name)

    @classmethod
    def set_collection_name(cls, collection_name: str):
        """Define the Mongodb collection in your class.
        Use the PyMongoModel.model_type_registry as the type registry."""
        cls.__collection_name = collection_name
        if PyMongoModel.mongo is not None:
            cls.collection = PyMongoModel.mongo.db.get_collection(collection_name)

    def __init_subclass__(cls):
        """Note that subclasses must implement a constructor or a __new__()
        which initializes all attributes with the proper values."""

        # Determine the name of the mongo collection by the class name:
        cls.set_collection_name(cls.__name__.lower())

        super().__init_subclass__()

    @abstractmethod
    def __init__(self):
        """Initializes the PyMongoModel overhead"""
        super().__init__()

    @classmethod
    @classproperty
    @lru_cache(maxsize=1)
    def default(cls) -> Self:
        """Returns the default object"""
        return cls()

    @property
    def id(self):
        """The internal document identifier"""
        return self._id

    def __hash__(self) -> int:
        return hash(self._id)

    @property
    def id_secondary(self):
        """A dummy property; always equal to id
        Used to have multiple id-driven columns in a Flask-tables table
        """
        return self.id

    def save(self):
        """Saves this document to the collection"""
        if not self._id:
            self.collection.insert_one(self.encode(add_id=True))
        else:
            self.collection.replace_one({"_id": self._id}, self.encode())

    def remove(self):
        """Removes this document from the collection"""
        if self._id:
            self.collection.delete_one({"_id": self._id})

    @classmethod
    def _encode_query(cls, query: dict[str, Any]) -> dict[str, Any]:
        return {
            key:
            cls.default.encode_value(value) for key, value in query.items()
        }

    @classmethod
    def find(cls, *args, **kwargs):
        """Finds documents from the collection
        Arguments are the same as those for PyMongo.collection's find(), by default.

        Or, specify no positional arguments and all kwargs- In this way you can query where field=val
        """
        if len(args) == 0:  # Supports new query type
            return cls.find(cls._encode_query(kwargs))

        # kwargs as field=value
        return [cls.decode(document) for document in cls.collection.find(*args, **kwargs)]

    @classmethod
    def find_sorted(cls, *args, key: str, order=ASCENDING, **kwargs):
        """Same a find(), but with sorting!"""
        if len(args) == 0:  # Supports new query type
            return cls.find_sorted(cls._encode_query(kwargs), key=key, order=order)
        return (
            [
                cls.decode(document)
                for document in cls.collection.find(*args, **kwargs).sort(key, order)
            ]
        )

    @classmethod
    def find_one(cls, *args, **kwargs):
        """Finds a document from the collection
        Arguments are the same as those for PyMongo's find_one()."""
        if len(args) == 0:  # Supports new query type
            return cls.find_one(cls._encode_query(kwargs))
        results = (
            cls.collection.find_one(*args, **kwargs)
        )
        if results is None:
            return None
        return cls.decode(results)

    def find_self(self):
        """Returns the database's version of self"""
        return self.find_by_id(self.id)

    @classmethod
    def find_by_id(cls, identifier):
        """Finds a document from the collection, given the id"""
        return cls.find_one({"_id": ObjectId(identifier)}) or None

    @classmethod
    def find_safe(cls, *args, **kwargs):
        return cls.collection.find(*args, **kwargs)
