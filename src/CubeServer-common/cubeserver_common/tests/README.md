# Unit Tests for CubeServer-common


## Writing / updating tests

Don't just change the test until it works, please.  
If a test fails, it's probably not the test's fault.


### Imports

Pretend you're just outside the `cubeserver_common` package (`cubeserver_common` is in the current working directory).

Example import statement:
```Python
from cubeserver_common.models.utils import (
    PyMongoModel,
    EncodableCodec,
    Encodable,
    BSON_TYPES,
)
```


### Database

MongoMock is used to pretend there's a database when there isn't.

For a PyMongoModel subclass `MyModel`, have fixtures like this...
```Python
@pytest.fixture()
def mock_mongo():
    """Establishes a fake Mongo instance for testing"""
    mc = mongomock.MongoClient()
    yield mc
    mc.close()

@pytest.fixture(autouse=True)
def init_orm(mock_mongo):
    """Initializes MyModel and the db and stuff"""
    PyMongoModel.update_mongo_client(mock_mongo)
    MyModel.__init_subclass__()
    yield
```
