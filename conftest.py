import pytest 
from captaina import create_app
import pymodm
import pymongo

TEST_DB_URI = "mongodb://root:debug@localhost:27017/test?authSource=admin"

@pytest.fixture
def app():
    app = create_app(
            TESTING=True,
            MONGO_DATABASE_URI = TEST_DB_URI 
            )
    yield app
    pymongo.MongoClient(TEST_DB_URI).drop_database('test')

@pytest.fixture
def client(app):
    client = app.test_client()
    yield client

@pytest.fixture
def add_user(app):
    from captaina.models import User
    users_added = []

    def _add_user(user_kwargs, password):
        new_user = User(**user_kwargs)
        new_user.set_password(password)
        new_user.save(force_insert=True)
        users_added.append(new_user)
        return new_user
    yield _add_user
    for user in users_added:
        user.delete()
      

