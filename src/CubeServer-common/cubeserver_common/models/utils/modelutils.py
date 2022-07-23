"""Some utility classes to help with object mapping"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Mapping, Optional, Tuple, Type, cast
from pydoc import locate
from bson import ObjectId
from bson import _BUILT_IN_TYPES as BSON_TYPES
from bson.codec_options import TypeCodec, TypeRegistry
from pymongo import MongoClient
from pymongo.collection import Collection

from .dummycodec import DummyCodec
from .enumcodec import EnumCodec

__all__ = ['PyMongoModel', 'Encodable', 'EncodableCodec']

def _locatable_name(type_to_name: type) -> str:
    """Returns a string that can be used in reverse with pydoc.locate"""
    module = type_to_name.__module__
    if "builtin" in module:
        return type_to_name.__name__
    return module + "." + type_to_name.__name__

class _Encoder(ABC):
    @abstractmethod
    def encode(self) -> dict:
        """Encodes an Encodable object into a plain old, bson-able
        dictionary"""

    @classmethod
    @abstractmethod
    def decode(cls, value: dict):
        """Decodes a dictionary into an Encodable object"""

class EncodableCodec(TypeCodec):
    """A TypeCodec for PyMongoModel objects"""

    bson_type = dict

    def __init__(self, encodable: Type[_Encoder]):
        self.encodable = encodable

    @property
    def python_type(self) -> Type[_Encoder]:
        return self.encodable

    def transform_python(self, value: _Encoder) -> dict:
        """Encodes a PyMongoModel object into a plain old, bson-able
        dictionary"""
        return value.encode()

    def transform_bson(self, value: dict) -> _Encoder:
        """Decodes a dictionary into a PyMongoModel object"""
        return self.python_type.decode(value)

class Encodable(_Encoder):
    """An abstract class for classes that contain codec data"""

    @abstractmethod
    def __init__(self) -> None:
        """Encodables must have a no-argument constructor that just
        populates default values for decoding purposes."""
        super().__init__()

    # From _Encoder:
    @abstractmethod
    def encode(self) -> dict:
        """Encodes an Encodable object into a plain old, bson-able
        dictionary"""

    @classmethod
    @abstractmethod
    def decode(cls, value: dict) -> _Encoder:
        """Decodes a dictionary into an Encodable object"""

class PyMongoModel(Encodable):
    """A class for easy object-mapping to bson.
    Extend this class for any classes that describe a type of document."""

    mongo: Optional[MongoClient] = None

    @classmethod
    def update_mongo_client(cls, mongo_client: MongoClient):
        """Sets the MongoClient reference in PyMongoModel, which is then
        used by any models that extend this class."""
        cls.mongo = mongo_client

    @property
    @classmethod
    def model_type_registry(cls) -> TypeRegistry:
        """A TypeRegistry to be used when getting the collection from
        the database"""
        return TypeRegistry([EncodableCodec(cls)])

    @property
    @abstractmethod
    def collection(self) -> Collection:
        """Define the Mongodb collection in your class.
        Use the PyMongoModel.model_type_registry as the type registry."""

    def __init_subclass__(cls):
        """Note that subclasses must implement a constructor or a __new__()
        which initializes all attributes with the proper values."""


        if PyMongoModel.mongo is None:
            raise AttributeError("Dude, you forgot to initialize PyMongoModel"
                                "with the MongoClient!")

        cls._ignored: List[str] = [
            "_id",
            "type_codec",
            "_codecs",
            "_fields",
            "_ignored"
        ]

        # Registered TypeCodecs:
        cls._codecs: Mapping[type, TypeCodec] = {}

        # Registered fields and their corresponding TypeCodecs:
        # (None is an acceptable codec for directly bson-compatible types)
        cls._fields: Mapping[str, Optional[TypeCodec]] = {}

        super().__init_subclass__()

    @abstractmethod
    def __init__(self):
        """Initializes the PyMongoModel overhead"""
        # Id:
        self._id: Optional[ObjectId] = None
        super().__init__()

    def register_codec(self, type_codec: TypeCodec, replace = False):
        """Register a TypeCodec for use in the PyMongoModelCodec
        Specify whether to replace an existing one if applicable,
        with the default being False."""
        if type_codec.python_type in self._codecs and not replace:
            raise KeyError(
                f"A TypeCodec is already registered"
                f" for type {type_codec.python_type}"
            )
        self._codecs[type_codec.python_type] = type_codec

    def ignore_attribute(self, attr_name: str):
        """Forces an attribute to be ignored as a document field"""
        if attr_name not in self._ignored:
            self._ignored += [attr_name]

    def locate_codec(self, data_type: type) -> Optional[TypeCodec]:
        """Tries to find a TypeCodec for the specified type if possible."""
        codec: Optional[TypeCodec] = None
        if issubclass(data_type, Encodable): # Use the one specified:
            codec = EncodableCodec(cast(Encodable, data_type()))
        elif issubclass(data_type, TypeCodec):
            codec = data_type()
        elif issubclass(data_type, Enum): # Use the EnumCodec class:
            codec = EnumCodec(data_type, type(list(cast(Enum, data_type))[0]))
        else:
            raise TypeError(f"No TypeCodec is registered for type "
                            f"{data_type}. "
                            f"Please register one before setting.")
        return codec

    def register_field(self, attr_name: str, value: Optional[Any] = None,
                       custom_codec: Optional[TypeCodec] = None):
        """Register each attribute of the model for the database.
        Optionally specify with a custom codec prior to setting the attribute.
        If a codec is specified optionally here, it will not be automatically
        registered for use in encoding/decoding attributes of the same type
        unless register_codec() is used also.
        The value does not need to be specified ONLY IF a custom_codec is
        provided.
        This method returns immediately if a field with the given name is
        already registered."""
        if attr_name in self._fields:
            return
        codec = custom_codec
        if codec is None and \
           value is not None and \
           type(value) not in BSON_TYPES and \
           not type(value) in self._codecs:    # if a TypeCodec is required:
            # Find or make a TypeCodec for this field:
            if isinstance(value, Encodable): # Use the one specified:
                codec = EncodableCodec(type(value))
            elif isinstance(value, TypeCodec):
                codec = value
            elif isinstance(value, Enum): # Use the EnumCodec class:
                codec = EnumCodec(type(value), type(value.value))
            else:
                raise TypeError(f"No TypeCodec is registered for type " 
                                f"{type(value)}, for attribute {attr_name}. "
                                f"Please register one before setting.")
            self.register_codec(codec)
        if codec is None and type(value) in self._codecs:
            codec = self._codecs[type(value)]
        self._fields[attr_name] = codec

    def encode(self) -> dict:
        """Encodes this into a dictionary for BSON to be happy"""
        if '_id' not in vars(self) or self._id is None:
            self._id = ObjectId()
        dictionary: Mapping[str, Tuple[str, Any]] = {}
        for (field, codec) in zip(self._fields, self._fields.values()):
            if codec:  # Encode each field:
                dictionary[field] = (_locatable_name(codec.python_type),
                    codec.transform_python(
                        getattr(self, field)
                    )
                )
            else:  # If no TypeCodec was specified, just leave the value raw:
                value = getattr(self, field)
                #dictionary[field] = (_locatable_name(type(value)), value)
                dictionary[field] = ("None", value)
        dictionary['_id'] = self._id
        return dictionary

    @classmethod
    def find_codec(cls, field_name: str, field_type_name: str) -> TypeCodec:
        """Finds a codec for a given field (w/ name and type name specified)"""
        return ( cls._fields[field_name]
            if field_name in cls._fields
            else (
                cls._codecs[locate(field_type_name)]
                if locate(field_type_name) in cls._codecs
                else DummyCodec()
            )
        )

    @classmethod
    def decode(cls, value: Optional[Mapping[str, Any]]) -> Optional[Encodable]:
        """Populates an object from a dictionary of the document
        This returns None only if the bson value given is None"""
        if value is None:  # Limit a potential failure
            return None
        new_object = cls()
        new_object._id = value.pop("_id")
        for field_name, (field_type_name, val) in zip(value, value.values()):
            if field_type_name == "None":
                new_object._setattr_shady(field_name, val)
            else:
                # Try to get the codec from the fields registry
                # or else try to fall back on the codecs registry
                # or, if that fails, try the fallback dummy codec:
                codec: TypeCodec = cls.find_codec(field_name, field_type_name)
                new_object._setattr_shady(field_name,
                    codec.transform_bson(val)
                )
        return new_object

    def __delattr__(self, __name: str):
        if __name in self._fields:
            del self._fields[__name]
        super().__delattr__(__name)

    def __setattr__(self, __name: str, __value: Any):
        if __name not in self._ignored and \
           __value is not None and \
           __name not in self._fields:
            self.register_field(__name, __value)
        super().__setattr__(__name, __value)

    def _setattr_shady(self, __name: str, __value: Any):
        """Shadily goes around __setattr__ and straight to the superclass.
        This is a workaround to allow for easier implementation of the
        decode() method."""
        super().__setattr__(__name, __value)

    @property
    def id(self):
        """The internal document identifier"""
        return self._id

    def save(self):
        """Saves this document to the collection"""
        if not self._id:
            self.collection.insert_one(self.encode())
        else:
            self.collection.replace_one(
                {"_id": self._id},
                self.encode()
            )

    def remove(self):
        """Removes this document from the collection"""
        if self._id:
            self.collection.delete_one({"_id": self._id})

    @classmethod
    def find(cls, *args, **kwargs):
        """Finds documents from the collection
        Arguments are the same as those for PyMongo.collection's find()."""
        return [
            cls.decode(document)
            for document in cls.collection.find(*args, **kwargs)
        ]
    
    @classmethod
    def find_one(cls, *args, **kwargs):
        """Finds a document from the collection
        Arguments are the same as those for PyMongo's find_one()."""
        return cls.decode(cls.collection.find_one(*args, **kwargs))

    @classmethod
    def find_by_id(cls, identifier):
        """Finds a document from the collection, given the id"""
        return cls.find_one({'_id': ObjectId(identifier)})

    def set_attr_from_string(self, field_name: str, value: str):
        """Decodes and updates a single string value to the document object"""
        self._setattr_shady(
            field_name,
            self._fields[field_name].transform_bson(value)
        )
