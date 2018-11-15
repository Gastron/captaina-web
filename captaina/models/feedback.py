import pymodm as modm
import pymongo as mongo
from datetime import datetime
from ..jinja_filters import datetimefmt

class Feedback(modm.MongoModel):
    message = modm.fields.CharField(required = True)
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)
    read = modm.fields.BooleanField(default = False)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def pretty_print(self):
        print()
        print("="*80)
        print("Feedback, last modified on:", datetimefmt(self.modified))
        print("=== Message: ===")
        print(self.message)
