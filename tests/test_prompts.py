import pytest
from test_login import login, logout

def test_get_prompt(client, uuid):
    from captaina.models import Lesson, Prompt, create_lesson_with_safe_url_id, create_user 
    user = create_user(uuid, "password")
    login(client, uuid, "password")
    first_prompt = Prompt(text = "Äyskäröinti on kivaa",
            graph_id = "graph_1").save()
    second_prompt = Prompt(text = "Pelkkää makkaraa ei kannata pitää ravintona",
            graph_id = "graph_2").save()
    test_lesson = create_lesson_with_safe_url_id("Test lesson")
    test_lesson.prompts = [first_prompt, second_prompt]
    test_lesson.save()
    #can go to first prompt:
    response = client.get("lessons/"+test_lesson.url_id+"/1")
    assert "Äyskäröinti on kivaa" in response.data.decode('utf-8')
    #redirect to first prompt if attempting others or overview first
    response = client.get("lessons/"+test_lesson.url_id+"/overview", follow_redirects=True)
    assert "Äyskäröinti on kivaa" in response.data.decode('utf-8')
    response = client.get("lessons/"+test_lesson.url_id+"/2", follow_redirects=True)
    assert "Äyskäröinti on kivaa" in response.data.decode('utf-8')
