import pytest 
from captaina import create_app
from pymodm.context_managers import switch_connection
import pymongo
import uuid as uuid_module

TEST_DB_URI = "mongodb://root:debug@localhost:27017/test?authSource=admin"

@pytest.fixture(scope="session")
def app():
    #NOTE: Shared DB! Always use UUID for usernames or other unique strings, to avoid conflict
    app = create_app(
            TESTING=True,
            MONGO_DATABASE_URI = TEST_DB_URI
            )
    reset_data()
    yield app

@pytest.fixture
def uuid():
    return uuid_module.uuid4().hex

def reset_data():
    from captaina.models import User, Lesson, Prompt, Feedback
    User.objects.all().delete()
    Prompt.objects.all().delete()
    Lesson.objects.all().delete()
    Feedback.objects.all().delete()
    user = User(username="tester", 
            email="example@example.com")
    user.set_password("password")
    user.save()
    prompt = Prompt(text="Test phrase please ignore", 
            graph_id="graph_1").save()
    Lesson(label="Beginnings",
            url_id="beginnings",
            prompts = [prompt]).save()
    Feedback(message = "Test suite message")

@pytest.fixture
def client(app):
    client = app.test_client()
    yield client



