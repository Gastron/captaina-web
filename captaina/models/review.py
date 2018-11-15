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
        rating = self.review.get(word_id, "na")
        if isinstance(rating, list):
            return rating[0] #Deal with wierd list encapsulation
        else:
            return rating

    def get_comment(self):
        comment = self.review.get("comment")
        if not comment: #Test for empty comment
            return None
        else:
            return comment

