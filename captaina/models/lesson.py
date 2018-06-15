import pymodm as modm
import pymongo as mongo

class Prompt(modm.MongoModel):
    text = modm.fields.CharField(required = True)
    graph_id = modm.fields.CharField(required = True)

class Lesson(modm.MongoModel):
    label = modm.fields.CharField(required = True)
    prompts = modm.fields.ListField(Prompt)
    
