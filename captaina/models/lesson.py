import pymodm as modm
import pymongo as mongo
import re
from werkzeug.utils import secure_filename
MAX_SAFE_URL_ID_ATTEMPTS = 1024

class Prompt(modm.MongoModel):
    text = modm.fields.CharField(required = True)
    graph_id = modm.fields.CharField(required = True)
    class Meta:
        final = True

class Lesson(modm.MongoModel):
    label = modm.fields.CharField(required = True)
    url_id = modm.fields.CharField(required = True)
    prompts = modm.fields.ListField(modm.fields.ReferenceField(Prompt), blank=True, default=list())
    class Meta:
        indexes = [mongo.operations.IndexModel([('url_id', 1)], 
            unique = True, background = False)] 

def create_lesson_with_safe_url_id(label):
    lesson = Lesson()
    lesson.label = label
    url_id = label.lower()
    url_id = secure_filename(url_id) #secure filename is also a pretty good url
    try:
        lesson.url_id = url_id
        #If not forcing insert, can also just update, i.e. overwrite existing
        lesson.save(force_insert=True) 
        return lesson
    except mongo.errors.DuplicateKeyError:
        #conflicting id, start adding an incremental index number
        pass
    counter = 2
    while counter < MAX_SAFE_URL_ID_ATTEMPTS:
        try:
            url_id_augmented = url_id + "_" + str(counter)
            lesson.url_id = url_id_augmented
            lesson.save(force_insert=True)
            return lesson
        except mongo.errors.DuplicateKeyError:
            counter += 1
    raise RuntimeError("Exceeded maximum number of safe url_id creation attempt with label: " +
            label)
