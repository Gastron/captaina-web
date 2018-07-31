import pymodm as modm
import pymongo as mongo
import re
from werkzeug.utils import secure_filename
from ..utils import mongo_serial_unique_attribute

class Prompt(modm.MongoModel):
    text = modm.fields.CharField(required = True)
    graph_id = modm.fields.CharField(required = True)
    class Meta:
        final = True
        indexes = [mongo.operations.IndexModel([('graph_id', 1)], unique = True)] 

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
    return mongo_serial_unique_attribute(lesson, "url_id", url_id)
