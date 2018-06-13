import pytest 
import pymongo

def test_create_user(app):
    #Note: Must import here, because without the app_fixture the db connection does not exist
    from captaina.models import User
    new_user = User()
    assert not new_user.is_valid()
    new_user.username = "user"
    new_user.set_password("pass")
    assert new_user.is_valid()
    new_user.save()
    with pytest.raises(pymongo.errors.DuplicateKeyError):
        new_user.save(force_insert=True)

def test_passwords(app):
    from captaina.models import User
    new_user = User()
    new_user.username = "user"
    new_user.set_password("pass")
    assert new_user._password is not "pass"
    assert new_user.is_correct_password("pass")
    assert not new_user.is_correct_password("hunter2")
    assert not new_user.is_correct_password("")
    with pytest.raises(ValueError):
        new_user.set_password("")

def test_feedback(app):
    from captaina.models import Feedback
    new_feedback = Feedback()
    assert not new_feedback.is_valid()
    new_feedback.message = "The test suite works nicely"
    assert new_feedback.is_valid()
    new_feedback.save()
