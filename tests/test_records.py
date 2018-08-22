import pytest

def test_create_lesson_records(app, uuid_generator):
    from captaina.models import create_user, AudioRecord, Prompt,\
            create_lesson_with_safe_url_id, ensure_and_get_incomplete_lesson_record
    #Lengthy setup:
    lesson = create_lesson_with_safe_url_id(uuid_generator())
    first_prompt = Prompt(text = "Karviaismarjakausi ei ole ohi",
            graph_id = uuid_generator()).save()
    second_prompt = Prompt(text = "Pelkkää makkaraa ei kannata pitää ravintona",
            graph_id = uuid_generator()).save()
    lesson.prompts = [first_prompt, second_prompt]
    lesson.save()
    user = create_user(uuid_generator(), "pass") 
    #Now the test portion:
    lesson_record = ensure_and_get_incomplete_lesson_record(user, lesson)
    other_lesson_record = ensure_and_get_incomplete_lesson_record(user, lesson)
    assert lesson_record == other_lesson_record
    first_audio_record = AudioRecord(user = user,
            prompt = first_prompt,
            filekey = uuid_generator(),
            alignkey = uuid_generator(),
            passed_validation = True).save()
    lesson_record.audio_records.append(first_audio_record)
    lesson_record.save()
    assert not lesson_record.is_complete()
    second_audio_record = AudioRecord(user = user,
            prompt = second_prompt,
            filekey = uuid_generator(),
            alignkey = uuid_generator(),
            passed_validation = False).save()
    lesson_record.audio_records.append(second_audio_record)
    lesson_record.save()
    assert not lesson_record.is_complete()
    third_audio_record = AudioRecord(user = user,
            prompt = second_prompt,
            filekey = uuid_generator(),
            alignkey = uuid_generator(),
            passed_validation = True).save()
    lesson_record.audio_records.append(third_audio_record)
    lesson_record.save()
    assert lesson_record.is_complete()
    still_another_lesson_record = ensure_and_get_incomplete_lesson_record(user, lesson)
    assert lesson_record != still_another_lesson_record
        
def test_lesson_record_cookie_exchange(app, uuid_generator):
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
    secret_key = uuid_generator()
    cookie = cookie_from_lesson_record(lesson_record, secret_key)
    recovered_record = lesson_record_from_cookie(cookie, secret_key)
    assert lesson_record == recovered_record

