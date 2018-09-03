import pymodm as modm
import pymongo as mongo
from datetime import datetime
from .records import AudioRecord
from .user import User

class AudioReview(modm.MongoModel):
    reviewer = modm.fields.ReferenceField(User)
    audio_record = modm.fields.ReferenceField(AudioRecord)
    review = modm.fields.DictField(blank=True)
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

    def get_rating(self, word_id):
        return self.review.get(word_id, ["na"])[0] #Deal with wierd list encapsulation

