import pymodm as modm
import pymongo as mongo
from datetime import datetime
from . import AudioRecord, User

class AudioReview(modm.MongoModel):
    reviewer = modm.fields.ReferenceField(User)
    audio_record = modm.fields.ReferenceField(AudioRecord)
    review = modm.fields.DictField()
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

