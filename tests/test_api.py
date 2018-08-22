import pytest
import json

def test_verify_cookie(app, client, uuid_generator):
    from captaina.models import create_user, AudioRecord, Prompt,\
            create_lesson_with_safe_url_id, ensure_and_get_incomplete_lesson_record,\
            cookie_from_lesson_record, lesson_record_from_cookie
    #Copied lengthy setup above:
    lesson = create_lesson_with_safe_url_id(uuid_generator())
    first_prompt = Prompt(text = "Karviaismarjakausi ei ole ohi",
            graph_id = uuid_generator()).save()
    second_prompt = Prompt(text = "Pelkkää makkaraa ei kannata pitää ravintona",
            graph_id = uuid_generator()).save()
    lesson.prompts = [first_prompt, second_prompt]
    lesson.save()
    user = create_user(uuid_generator(), "pass") 
    lesson_record = ensure_and_get_incomplete_lesson_record(user, lesson)
    #Now the test:
    cookie = cookie_from_lesson_record(lesson_record, app.config["SECRET_KEY"])
    print(cookie)
    response = client.post("/api/verify-record-cookie",
            json = {"record-cookie": cookie})
    assert response.data == b"OK"

