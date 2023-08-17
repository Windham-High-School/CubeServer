"""Classes to allow for easy object-mapping to bson for MongoDb

Example usages
--------------

Basic usage:

.. highlight:: python
.. code-block:: python

    class MyModel(models.utils.PyMongoModel):
        '''Example No. 1
        Basic usage
        '''

        def __init__(self, a:int = 1):
            self.a: int = a
    
    # Create an object:
    my_object = MyModel(9)

    # Save the object in the database:
    my_object.save()

    # Remove the object from the database:
    my_object.remove()

    # Find the object in the database:
    my_object_also = my_object.find_self()
    
    my_object_also_2 = MyModel.find_by_id(my_object.id)

    my_object_also_3 = MyModel.find_one(a=9)

    assert my_object == my_object_also == my_object_also_2 == my_object_also_3

    # Update the object in the database:
    my_obj = MyModel.find_by_id(my_object.id)
    my_obj.a = 12
    my_obj.save()

    # Find all objects (as a list):
    all_mymodel_objects: list[MyModel] = MyModel.find()

Dataclasses usage:

.. highlight:: python
.. code-block:: python

    import dataclasses

    @dataclasses.dataclass
    class MyModelDc(models.utils.PyMongoModel):
        '''Example No. 2
        Dataclasses
        '''

        a: int = 1


Note:   
More complex usage is possible, with compound and non-supported type fields and codecs

"""

from bson import _BUILT_IN_TYPES as BSON_TYPES

from .codecs.enumcodec import *
from .codecs.listcodec import *
from .codecs.dummycodec import *
from .codecs.complexdictcodec import *

from .autoencodable import *

from .modelutils import *
from .codecutils import *
