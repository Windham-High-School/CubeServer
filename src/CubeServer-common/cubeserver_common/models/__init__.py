"""
The `models` package provides a framework for defining
and serializing MongoDB data models in Python.
The package includes support for defining codecs for custom data types,
and AutoEncodable serialization to bson or json.

Model object serialization is used automatically to serialize
and deserialize data models based on their attributes and save
each object as a document in a MongoDB database.

The `models` package includes a base class, `AutoEncodable`,
that can be used to define data models that support automatic
serialization and deserialization.
"""

from .utils import *