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
    #user = User(username="tester", 
    #        email="example@example.com")
    #user.set_password("password")
    #user.save()
    #prompt = Prompt(text="Test phrase please ignore", 
    #        graph_id="graph_1").save()
    #Lesson(label="Beginnings",
    #        url_id="beginnings",
    #        prompts = [prompt]).save()
    #Feedback(message = "Test suite message")

@pytest.fixture
def client(app):
    client = app.test_client()
    yield client



