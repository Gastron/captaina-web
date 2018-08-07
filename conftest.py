import os
import pytest 
from captaina import create_app
from pymodm.context_managers import switch_connection
import pymongo
import uuid as uuid_module

#Force the test suite to use the test_instance values, so that nothing gets overwritten
@pytest.fixture(scope="session", autouse=True)
def test_instance():
    os.environ["FLASK_INSTANCE_PATH"] = os.path.join(os.getcwd(),"test_instance")
    yield

@pytest.fixture(scope="session")
def app():
    #NOTE: Shared DB! Always use UUID for usernames or other unique strings, to avoid conflict
    app = create_app()
    reset_data(app.config['MONGO_DATABASE_URI'])
    yield app

@pytest.fixture
def uuid():
    return uuid_module.uuid4().hex

@pytest.fixture
def uuid_generator():
    return lambda: uuid_module.uuid4().hex[:12] #twelve first chars should be good enough

def reset_data(db_uri):
    import captaina.models
    import pymodm
    for cls in pymodm.MongoModel.__subclasses__():
        cls.objects.all().delete()

@pytest.fixture
def client(app):
    client = app.test_client()
    yield client



