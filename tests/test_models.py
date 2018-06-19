import pytest 
import pymongo

def test_create_user(app, uuid):
    from captaina.models import User, create_user
    new_user = User()
    assert not new_user.is_valid()
    new_user = create_user(uuid, "pass")
    assert new_user.is_valid()
    new_user.save()
    with pytest.raises(pymongo.errors.DuplicateKeyError):
        new_user.save(force_insert=True)
    with pytest.raises(ValueError):
        other_user = create_user(uuid, "hunter1")

def test_passwords(app, uuid):
    from captaina.models import User
    new_user = User()
    new_user.username = uuid
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

def test_create_lesson_with_safe_url_id(app, uuid):
    from captaina.models import Lesson, Prompt, create_lesson_with_safe_url_id
    lesson = create_lesson_with_safe_url_id(uuid)
    assert lesson.is_valid()
    other_lesson = create_lesson_with_safe_url_id(uuid)
    assert other_lesson.is_valid()
    assert lesson.url_id != other_lesson.url_id
    third_lesson = create_lesson_with_safe_url_id("*ÅAS*DA haha")
    assert " " not in third_lesson.url_id
    
