import pymodm as modm
import pymongo as mongo
import datetime

class Feedback(modm.MongoModel):
    message = modm.fields.CharField(required = True)
    created = modm.DateTimeField(required = True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created = datetime.datetime.now()

