import pymodm as modm
import pymongo as mongo
import pathlib
from .user import User
from .lesson import Lesson, Prompt
import itsdangerous
import bson.json_util
from datetime import datetime
import json


class AudioRecord(modm.MongoModel):
    user = modm.fields.ReferenceField(User)
    prompt = modm.fields.ReferenceField(Prompt)
    filekey = modm.fields.CharField()
    passed_validation = modm.fields.BooleanField()
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [mongo.operations.IndexModel([('filekey',mongo.ASCENDING)], unique = True)]

def validate_audio_record_files(audio_record, audio_store_path):
    #Makes sure the audio_record's referenced files are found.
    audio_store = pathlib.Path(audio_store_path)
    id_path = audio_store / audio_record.filekey
    audio_file_path = id_path.with_suffix(".raw")
    align_file_path = id_path.with_suffix(".ali.json") 
    return audio_file_path.exists() and align_file_path.exists()

def choose_word_alignments(word_alignment):
    """ Chooses the last occurences of each word in the alignment,
    and nothing more """
    chosen = {}
    for word_dict in word_alignment:    
        word = word_dict["word"]
        if word == "<UNK>" or "[TRUNC:]" in word:
            continue
        word_index = int(word.split("@")[1])
        chosen[word_index] = word_dict
    return [chosen[index] for index in sorted(chosen.keys())]

def fetch_word_alignment(audio_record, audio_store_path):
    audio_store = pathlib.Path(audio_store_path)
    id_path = audio_store / audio_record.filekey
    align_file_path = id_path.with_suffix(".ali.json") 
    return json.loads(align_file_path.read_text())["word-alignment"]

def aligns_to_millis(aligns):
    return [{
        "word": align["word"], 
        "start": int(1000*align["start"]),
        "length": int(1000*align["length"])} for align in aligns]

def pad_aligns(aligns, front_pad=10, end_pad=10):
    """ Add padding milliseconds of padding to aligns. Assumed aligns already in millis. """
    result = aligns[:]
    for align in result:
        align["start"] = align["start"]-front_pad
        if align["start"] < 0:
            align["start"] = 0
        align["length"] += end_pad
    return result

def match_words_and_aligns(audio_record, aligns):
    words = audio_record.prompt.text.split()
    if not len(words) == len(aligns):
        raise ValueError("Prompt and align do not match!")
    return list(zip(words, aligns, range(len(words)))) # add an index also

def get_matched_alignment(audio_record, audio_store_path, front_pad=10, end_pad=10):
    word_aligns = fetch_word_alignment(audio_record, audio_store_path)
    chosen_aligns = choose_word_alignments(word_aligns)
    millis = aligns_to_millis(chosen_aligns)
    padded = pad_aligns(millis)
    matched_aligns = match_words_and_aligns(audio_record, padded)
    return matched_aligns

class LessonRecord(modm.MongoModel):
    user = modm.fields.ReferenceField(User)
    lesson = modm.fields.ReferenceField(Lesson)
    audio_records = modm.fields.ListField(modm.fields.ReferenceField(AudioRecord),
            blank = True, default = list)
    submitted = modm.fields.BooleanField(default = False)
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

    class Meta:
        #Each record is uniquely identified by the user, lesson and sequence id combination
        indexes = [mongo.operations.IndexModel([
            ('user', mongo.ASCENDING),
            ('lesson', mongo.ASCENDING)], unique = True)] 

    def get_id(self):
        return bson.json_util.dumps(self._id)

    def is_complete(self):
        # A bit convoluted, but:
        # Make sure there is at least one audio_record which passed validation
        # for each prompt
        for prompt in self.lesson.prompts:
            if not any(record.prompt == prompt and record.passed_validation
                    for record in self.audio_records):
                return False
        return True

    def num_prompts_completed(self):
        for i, prompt in enumerate(self.lesson.prompts):
            if not any(record.prompt == prompt and record.passed_validation
                    for record in self.audio_records):
                return i
        return len(self.lesson.prompts)

    def recording_exists(self, prompt):
        if any(record for record in self.audio_records if
                record.passed_validation and record.prompt == prompt):
            return True
        else:
            return False

    def get_audiorecord(self, prompt):
        """ Gets the currently chosen AudioRecord for the given prompt.
        This is the latest validated entry. """
        possible_records = [record for record in self.audio_records if
                record.passed_validation and record.prompt == prompt]
        if not possible_records:
            return None
        else:
            #Current decision: return the latest one
            return possible_records[-1]
    
    def validated_audio_records(self):
        return [record for record in self.audio_records if record.passed_validation]

    def reviews_exist(self):
        if not (self.is_complete() and self.submitted):
            return False
        from .review import AudioReview
        for prompt in self.lesson.prompts:
            audio_record = self.get_audiorecord(prompt)
            try:
                AudioReview.objects.raw({"audio_record": audio_record.pk}).first()
            except AudioReview.DoesNotExist:
                return False
        return True

    def is_new(self):
        #If there are no audio_records yet, it's new
        return not self.audio_records


class ReferenceRecord(modm.MongoModel):
    user = modm.fields.ReferenceField(User)
    lesson = modm.fields.ReferenceField(Lesson)
    audio_records = modm.fields.ListField(modm.fields.ReferenceField(AudioRecord),
            blank = True, default = list)
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

    def get_id(self):
        return bson.json_util.dumps(self._id)

    def get_reference(self, prompt):
        possible_references = [record for record in self.audio_records if
                record.passed_validation and record.prompt == prompt]
        if not possible_references:
            return None
        else:
            #Current decision: return the latest one
            return possible_references[-1]

    def reference_exists(self, prompt):
        if any(record for record in self.audio_records if
                record.passed_validation and record.prompt == prompt):
            return True
        else:
            return False

    class Meta:
        #Only one reference per lesson, per user
        indexes = [mongo.operations.IndexModel([
            ('user', mongo.ASCENDING),
            ('lesson', mongo.ASCENDING)], unique = True)] 


def get_references_for_prompt(lesson, prompt):
    references = ReferenceRecord.objects.raw({'lesson': lesson.pk})
    audio_records = []
    for reference in references:
        if reference.reference_exists(prompt):
            audio_records.append(reference.get_reference(prompt))
    return audio_records

def get_or_make_lesson_record(user, lesson):
    try:
        return LessonRecord.objects.raw({'user':user.pk, 'lesson':lesson.pk}).first()
    except LessonRecord.DoesNotExist:
        record = LessonRecord(user = user.pk, 
                lesson = lesson.pk)
        record.save(force_insert = True)
        return record
    except mongo.errors.DuplicateKeyError: #Duplicate request
        raise ValueError("Duplicate request")

def get_or_make_reference_record(user, lesson):
    try:
        return ReferenceRecord.objects.raw({'user':user.pk, 'lesson':lesson.pk}).first()
    except ReferenceRecord.DoesNotExist:
        record = ReferenceRecord(user = user.pk, 
                lesson = lesson.pk)
        record.save(force_insert = True)
        return record
    except mongo.errors.DuplicateKeyError: #Duplicate request
        raise ValueError("Duplicate request")

def get_record(user, lesson):
    try:
        return LessonRecord.objects.raw({'user':user.pk, 'lesson':lesson.pk}).first()
    except LessonRecord.DoesNotExist:
        try:
            return ReferenceRecord.objects.raw({'user':user.pk, 'lesson':lesson.pk}).first()
        except ReferenceRecord.DoesNotExist:
            raise ValueError("Record does not exist")

def load_record(record_id):
    try:
        return LessonRecord.objects.get({"_id": bson.json_util.loads(record_id)})
    except LessonRecord.DoesNotExist:
        try:
            return ReferenceRecord.objects.get({"_id": bson.json_util.loads(record_id)})
        except ReferenceRecord.DoesNotExist:
            raise ValueError("Record does not exist")



def cookie_from_record(record, secret_key):
    s = itsdangerous.URLSafeTimedSerializer(secret_key)
    return s.dumps(record.get_id())

def record_from_cookie(cookie, secret_key, max_age = 3600): 
    # Raises ValueError if not found
    s = itsdangerous.URLSafeTimedSerializer(secret_key)
    record_id = s.loads(cookie, max_age = max_age)
    return load_record(record_id)
