import pymodm as modm
import pymongo as mongo
import pathlib
from . import User, Lesson, Prompt
from flask import current_app

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
    audio_records = modm.fields.ListField(modm.fields.ReferenceField(AudioRecord),
            blank = True, default = list())

def validate_audio_record_files(audio_record):
    #Makes sure the audio_record's referenced files are found.
    audio_store = pathlib.Path(current_app.config["AUDIO_STORE_PATH"])
    audio_file_path = audio_store / audio_record.filekey
    align_file_path = audio_store / audio_record.alignkey
    return audio_file_path.exists() and align_file_path.exists()
