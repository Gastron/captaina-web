import pytest 
from captaina import create_app
import pymodm
import pymongo

@pytest.fixture
def app():
    test_uri = "mongodb://root:debug@localhost:27017/test?authSource=admin"
    app = create_app(
            TESTING=True,
            MONGO_DATABASE_URI = test_uri 
            )
    yield app
    pymongo.MongoClient(test_uri).drop_database('test')
