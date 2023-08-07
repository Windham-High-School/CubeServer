""" Automatic serialization / bson-compatible dict encoding
This was originally a part of PyMongoModel in modelutils.py,
moved here for neatness, maintainability, and versatility.

Example:
class MyModel(AutoEncodable):
    def __init__(self) -> None:
        super().__init__()
        self.my_attribute: str = "my_value"
        self.my_other_attribute: int = 0

instance = MyModel()
instance.encode() # {"my_attribute": "my_value", "my_other_attribute": 0}
"""

from typing import List, Optional, Type, cast, Any, Callable, NewType
from abc import ABC
from enum import Enum

from bson import _BUILT_IN_TYPES as BSON_TYPES
from bson import ObjectId
from bson.codec_options import TypeRegistry, TypeCodec

from .codecutils import Encodable, EncodableCodec
from .codecs import EnumCodec, DummyCodec
from .encodedproperty import DerivedFieldManager


__all__ = ['AutoEncodable', 'TypeReference']


TypeReference = NewType("TypeReference", str)
"""A type reference for use in bson serialization

This is effectively just a string, but it is used to indicate an absolute
type:
- "None" indicates that the value is directly bson-compatible,
    as will any built-in type name for which this is the case.
- "derived-property" indicates that the value is a derived property,
    and will generally be (at least mostly) ignored when decoding.
- "str" indicates that the value is of the built-in Python string type
- "module.ClassName" indicates that the value is of the specified class.
    This is used for all other types, including enums.
"""

def type_to_reference(type_to_name: Type[Any]) -> TypeReference:
    """Returns a string that can be used in reverse with pydoc.locate
    (but probably should not be used in such conjunction in production code).

    This is used in tables with type-based keys.
    While a hash could be used, and probably should be for efficiency,
    this is far more human-readable and far easier to work with if
    manual database editing is required for any reason.
    """
    module = type_to_name.__module__
    if "builtin" in module:
        return TypeReference(type_to_name.__name__)
    return TypeReference(module + "." + type_to_name.__name__)


class AutoEncodable(Encodable, ABC):
    """A class for (relatively) painless object-mapping to bson

    The following attributes are special:
    - _ignored: A list of attributes to ignore when encoding/decoding
    - _codecs: A dictionary of codecs to use for specific types
    - _fields: A dictionary of codecs to use for specific attributes
    - _id: Reserved for the document's ObjectId if MongoDB is used
    - model_type_registry: A TypeRegistry to be used when getting the
        collection from the database
    - _derived_fields: A DerivedFieldManager for derived fields
    """

    @property
    @classmethod
    def model_type_registry(cls) -> TypeRegistry:
        """A TypeRegistry to be used when getting the collection from
        the database"""
        return TypeRegistry([EncodableCodec(cls)])

    def __init__(self) -> None:
        """Note that subclasses MUST implement a constructor or a __new__()
        which initializes all attributes with the proper values."""

        self._ignored: List[str] = [
            "_id",
            "type_codec",
            "_codecs",
            "_fields",
            "_ignored",
            "_derived_fields"
        ]

        # Registered TypeCodecs:
        self._codecs: dict[TypeReference, TypeCodec] = {}

        # Registered fields and their corresponding TypeCodecs:
        # (None is an acceptable codec for directly bson-compatible types)
        self._fields: dict[str, Optional[TypeCodec]] = {}

        # Initialize encoded/cached property store:
        self._derived_fields = DerivedFieldManager()

        # Reserved for the document's ObjectId if MongoDB is used:
        self._id: Optional[ObjectId] = None

        super().__init__()

    # Codec management:
    def register_codec(self, type_codec: TypeCodec, replace = False):
        """Register a TypeCodec for use in the PyMongoModelCodec
        Specify whether to replace an existing one if applicable,
        with the default being False."""
        if type_codec.python_type in self._codecs and not replace:
            raise KeyError(
                "A TypeCodec is already registered"
                f" for type {type_codec.python_type}"
            )
        if not isinstance(type_codec.python_type, type):
            raise TypeError(
                "TypeCodec.python_type must be a type,"
                f" not {type(type_codec.python_type)}"
            )
        self._codecs[
            type_to_reference(type_codec.python_type)
        ] = type_codec

    def ignore_attribute(self, attr_name: str):
        """Forces an attribute to be ignored as a document field"""
        if attr_name not in self._ignored:
            self._ignored += [attr_name]

    def locate_codec(self, data_type: type) -> TypeCodec:
        """Tries to find a TypeCodec for the specified type if possible.
        If the type is built-in to bson, DummyCodec is returned.
        If the type is not built-in to bson, but a TypeCodec is registered
        for it, that TypeCodec is returned.
        
        If no TypeCodec is registered for the type, a TypeError is raised.

        All dictionaries, lists, etc are assumed to be completely
        bson-compatible for performance reasons (to avoid recursive
        type-checking). If this is not the case, a TypeCodec must be
        specified explicitly for this field.
        """
        # Best-case scenarios (efficient):
        if issubclass(data_type, Encodable): # Use the one specified:
            return EncodableCodec(data_type)
        elif type(data_type) in BSON_TYPES or data_type is ObjectId:
            return DummyCodec(data_type)
        # Available codecs:
        elif issubclass(data_type, Enum): # Use the EnumCodec class:
            return EnumCodec(data_type)
        # Worst-case scenarios (problem. that's bad.):
        elif issubclass(data_type, TypeCodec):
            raise TypeError("TypeCodecs cannot be serialized.")
        else:
            raise TypeError("No TypeCodec is registered for type "
                            f"{data_type}. Please register "
                            "one before setting an attribute of this type.")

    # Serializable field management:
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
        already registered.
        The force parameter allows you to force the registration of a field
        despite checks failing or the type appearing to be bson-compatible"""

        if value is not None:  # Also set the value while we're at it:
            self._setattr_shady(attr_name, value)

        if attr_name in self._fields:
            return
        codec = custom_codec
        # TODO: Check recursively for bson compat- there can be dicts of enums for ex
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
            codec = self._codecs[
                type_to_reference(type(value))
            ]
        self._fields[attr_name] = codec  # Register the field!

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

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, AutoEncodable):
            return False
        for field in self._fields:
            if field in self._ignored:
                continue
            if getattr(self, field) != getattr(__value, field):
                return False
        return True

    def _setattr_shady(self, __name: str, __value: Any):
        """Shadily goes around __setattr__ and straight to the superclass.
        This is a workaround to allow for easier implementation of the
        decode() method."""
        super().__setattr__(__name, __value)

    def derived_field(
            self,
            property_method: Callable[[], Any],
            cache: bool = False
    ) -> Callable[[], Any]:
        """Decorator for a derived property method
        @param func: The property method to decorate
        @param cache: set to False to force re-evaluation of the property

        Properties MUST be of bson types; no exceptions.
        """
        def property_wrapper():
            val = property_method()
            if type(val) not in BSON_TYPES:
                raise TypeError(
                    "Derived properties must be of"
                    "directly-compatible bson types."
                    )
            return val
        return self._derived_fields.derived_property(property_wrapper, cache)

    def encode(self) -> dict:
        """Encodes this into a dictionary for BSON to be happy"""
        dictionary: dict[str, tuple[str, Any] | ObjectId] = {}
        # Deal with ObjectId:
        if '_id' not in vars(self) or self._id is None:
            self._id = ObjectId()
        dictionary['_id'] = self._id
        for (field, codec) in zip(self._fields, self._fields.values()):
            if codec:  # Encode each field:
                dictionary[field] = (type_to_reference(codec.python_type),
                    codec.transform_python(
                        getattr(self, field)
                    )
                )
            else:  # If no TypeCodec was specified, just leave the value raw:
                value = getattr(self, field)
                #dictionary[field] = (_locatable_name(type(value)), value)
                dictionary[field] = ("None", value)
        for (field, value) in self._derived_fields.__property_cache.items():
            dictionary[field] = ("derived-property", value)
        return dictionary

    def _find_codec(self, field_name: str, field_type_name: TypeReference) -> TypeCodec:
        """Finds a codec for a given field (w/ name and type name specified)"""
        return ( self._fields[field_name]
            if field_name in self._fields
            else (
                self._codecs[field_type_name]
                if field_type_name in self._codecs
                else DummyCodec()
            )
        )

    @classmethod
    def decode(cls, value: dict[str, Any]) -> Encodable:
        """Populates an object from a dictionary of the document
        """
        if value is None:
            raise ValueError("Cannot decode Nonetype serial value")
        new_object = cls()
        new_object._id = value.pop("_id")
        for field_name, (field_type_name, val) in zip(value, value.values()):
            if field_type_name == "None":
                new_object._setattr_shady(field_name, val)
            elif field_type_name == "derived-property":
                new_object._derived_fields.init_property(field_name, val)
            else:
                # Try to get the codec from the fields registry
                # or else try to fall back on the codecs registry
                # or, if that fails, try the fallback dummy codec:
#                codec: TypeCodec = new_object._find_codec(field_name, field_type_name)
                codec: TypeCodec
                if field_name in new_object._fields:
                    codec = new_object._fields[field_name] or DummyCodec()
                elif field_type_name in new_object._codecs:
                    codec = new_object._codecs[field_type_name]

                new_object._setattr_shady(field_name,
                    codec.transform_bson(val)
                )
        return new_object
