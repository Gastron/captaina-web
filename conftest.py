import pytest 
from captaina import create_app
import pymodm
import pymongo
import threading

COUNTER_LOCK = threading.Lock()
with COUNTER_LOCK:
    db_counter = 0 
TEST_DB_TEMPLATE = "mongodb://root:debug@localhost:27017/{dbname}?authSource=admin"

@pytest.fixture
def app():
    global db_counter
    with COUNTER_LOCK:
        dbname = 'test' + str(db_counter)
        test_db_uri = TEST_DB_TEMPLATE.format(dbname=dbname)
        db_counter += 1
    app = create_app(
            TESTING=True,
            MONGO_DATABASE_URI = test_db_uri
            )
    yield app
    pymongo.MongoClient(test_db_uri).drop_database(dbname)

@pytest.fixture
def client(app):
    client = app.test_client()
    yield client



