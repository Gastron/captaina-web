import pymodm as modm
import pymongo as mongo
import pathlib
from . import User, Lesson, Prompt
import itsdangerous
import bson.json_util

class AudioRecord(modm.MongoModel):
    user = modm.fields.ReferenceField(User)
    prompt = modm.fields.ReferenceField(Prompt)
    filekey = modm.fields.CharField()
    alignkey = modm.fields.CharField()
    passed_validation = modm.fields.BooleanField()
    class Meta:
        indexes = [mongo.operations.IndexModel([('wavkey',mongo.ASCENDING)], unique = True),
            mongo.operations.IndexModel([('alignkey', mongo.ASCENDING)], unique = True)]

class LessonRecord(modm.MongoModel):
    user = modm.fields.ReferenceField(User)
    lesson = modm.fields.ReferenceField(Lesson)
    sequence_id = modm.fields.IntegerField()
    audio_records = modm.fields.ListField(modm.fields.ReferenceField(AudioRecord),
            blank = True, default = list())
    class Meta:
        #Each record is uniquely identified by the user, lesson and sequence id combination
        indexes = [mongo.operations.IndexModel([
            ('user', mongo.ASCENDING),
            ('lesson', mongo.ASCENDING),
            ('sequence_id', mongo.DESCENDING)], unique = True)] 

    def get_id(self):
        return bson.json_util.dumps(self._id)

    def is_complete(self):
        #TODO: see if all prompts in the lesson have a succesfully validated record
        pass


def load_lesson_record(record_id):
    return LessonRecord.objects.get({"_id": bson.json_util.loads(record_id)})

def validate_audio_record_files(audio_record, audio_store_path):
    #Makes sure the audio_record's referenced files are found.
    audio_store = pathlib.Path(audio_store_path)
    audio_file_path = audio_store / audio_record.filekey
    align_file_path = audio_store / audio_record.alignkey
    return audio_file_path.exists() and align_file_path.exists()

def cookie_from_lesson_record(lesson_record, secret_key):
    s = itsdangerous.URLSafeTimedSerializer(secret_key)
    return s.dumps(lesson_record.get_id())

def lesson_record_from_cookie(cookie, secret_key, max_age = 3600): 
    s = itsdangerous.URLSafeTimedSerializer(secret_key)
    record_id = s.loads(cookie, max_age = max_age)
    return load_lesson_record(record_id)


