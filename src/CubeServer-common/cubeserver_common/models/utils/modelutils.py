"""Some utility classes to help with object mapping

This is not thread safe. Exercise caution if accessing the same instance from multiple threads.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Self
from functools import lru_cache

from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from loguru import logger

from cubeserver_common.utils import classproperty

from .autoencodable import AutoEncodable


__all__ = ["PyMongoModel", "UninitializedCollectionError", "ASCENDING", "DESCENDING"]


class UninitializedCollectionError(ValueError):
    pass


# TODO: Remove if unneeded-
def _locatable_name(type_to_name: type) -> str:
    """Returns a string that can be used in reverse with pydoc.locate"""
    module = type_to_name.__module__
    if "builtin" in module:
        return type_to_name.__name__
    return module + "." + type_to_name.__name__


class PyMongoModel(AutoEncodable, ABC):
    """A class for easy object-mapping to bson.
    Extend this class for any classes that describe a type of document."""

    mongo: MongoClient | None = None

    __collection_name: str | None = None

    @staticmethod
    def _get_static_mongo_client() -> MongoClient:
        """Returns a mongo client to be used by all models"""
        return PyMongoModel.mongo

    @staticmethod
    def update_mongo_client(mongo_client: Optional[MongoClient]):
        """Sets the MongoClient reference in PyMongoModel, which is then
        used by any models that extend this class."""
        PyMongoModel.mongo = mongo_client

    @classmethod
    @classproperty
    def collection(cls) -> Collection:
        return PyMongoModel._get_static_mongo_client().db.get_collection(
            cls.__collection_name
        )

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
        if self.collection is None:
            raise UninitializedCollectionError(
                "Please initialize the collection attribute or run update_mongo_client"
            )
        if not self._id:
            self.collection.insert_one(self.encode(add_id=True))
        else:
            self.collection.replace_one({"_id": self._id}, self.encode())

    def remove(self):
        """Removes this document from the collection"""
        if self.collection is None:
            raise UninitializedCollectionError(
                "Please initialize the collection attribute or run update_mongo_client"
            )
        if self._id:
            self.collection.delete_one({"_id": self._id})

    @classmethod
    def _encode_query(cls, query: dict[str, Any]) -> dict[str, Any]:
        return {key: cls.default.encode_value(value) for key, value in query.items()}

    @classmethod
    def find(cls, *args, **kwargs):
        """Finds documents from the collection
        Arguments are the same as those for PyMongo.collection's find(), by default.

        Or, specify no positional arguments and all kwargs- In this way you can query where field=val
        """
        if cls.collection is None:
            raise UninitializedCollectionError(
                "Please initialize the collection attribute or run update_mongo_client"
            )

        if len(args) == 0:  # Supports new query type
            return cls.find(cls._encode_query(kwargs))

        # kwargs as field=value
        return [
            cls.decode(document) for document in cls.collection.find(*args, **kwargs)
        ]

    @classmethod
    def find_sorted(cls, *args, key: str, order=ASCENDING, **kwargs):
        """Same a find(), but with sorting!"""
        if cls.collection is None:
            raise UninitializedCollectionError(
                "Please initialize the collection attribute or run update_mongo_client"
            )

        if len(args) == 0:  # Supports new query type
            return cls.find_sorted(cls._encode_query(kwargs), key=key, order=order)
        return [
            cls.decode(document)
            for document in cls.collection.find(*args, **kwargs).sort(key, order)
        ]

    @classmethod
    def find_one(cls, *args, **kwargs):
        """Finds a document from the collection
        Arguments are the same as those for PyMongo's find_one()."""
        if cls.collection is None:
            raise UninitializedCollectionError(
                "Please initialize the collection attribute or run update_mongo_client"
            )

        if len(args) == 0:  # Supports new query type
            return cls.find_one(cls._encode_query(kwargs))
        results = cls.collection.find_one(*args, **kwargs)
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
        if cls.collection is None:
            raise UninitializedCollectionError(
                "Please initialize the collection attribute or run update_mongo_client"
            )

        return cls.collection.find(*args, **kwargs)
