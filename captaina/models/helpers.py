import pymongo as mongo
import pymodm as modm
from datetime import datetime

def mongo_serial_unique_attribute(pre_filled_instance, 
        attr, 
        value_to_try, 
        max_attempts=1024):
    """Given an instance of a PyMODM class, tries to save the instance with
    a value, suffixed by _<increment> until a saveable value is found. When
    the value has an index in the Mongo DB with the unique constraint, this
    makes sure a unique version is saved and avoids race conditions.

    E.G.
    class Example(pymodm.MongoModel):
        label = pymodm.fields.CharField(required = True)
        url_id = pymodm.fields.CharField(required = True)        
        class Meta:
            indexes = [mongo.operations.IndexModel([('url_id', 1)], 
                unique = True, background = False)] 
    
    example = Example()
    example.label = "example label"
    example = mongo_serial_unique_attribute(example, "url_id", "example")
    print(example.url_id) #prints: example
    example_two = Example(label="example again")
    example_two = mongo_serial_unique_attribute(example, "url_id", "example")
    print(example_two.url_id) #prints: example_2
    """
    try:
        setattr(pre_filled_instance, attr, value_to_try)
        #If not forcing insert, can also just update, i.e. overwrite existing
        pre_filled_instance.save(force_insert=True) 
        return pre_filled_instance 
    except mongo.errors.DuplicateKeyError:
        #conflicting value, start adding an incremental index number
        pass
    counter = 2
    while counter < max_attempts:
        try:
            value_augmented = value_to_try + "_" + str(counter)
            setattr(pre_filled_instance, attr, value_augmented)
            pre_filled_instance.save(force_insert=True)
            return pre_filled_instance
        except mongo.errors.DuplicateKeyError:
            counter += 1
    raise RuntimeError("""Exceeded max_attempts in serial unique attribute setting
        with attribute {attr}, 
        starting value {start_value}""".format(attr=attr, start_value=value_to_try))

class TimeStampedMongoModel(modm.MongoModel):
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

