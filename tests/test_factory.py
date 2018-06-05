import pytest
from captaina import create_app

def test_app_fixture(app):
    assert app.config['TESTING'] == True

def test_create_app():
    assert not create_app().testing
    assert create_app(TESTING=True).testing
