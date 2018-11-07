import pymodm as modm
import pymongo as mongo
import re
import requests
from werkzeug.utils import secure_filename
from .helpers import mongo_serial_unique_attribute
from datetime import datetime

class Prompt(modm.MongoModel):
    text = modm.fields.CharField(required = True)
    graph_id = modm.fields.CharField(required = True)
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [mongo.operations.IndexModel([('graph_id', 1)], unique = True)] 

def check_prompt_list():
    #Makes sure that all the prompts returned by graph-creator have a Prompt object
    graphs_request = requests.get("http://graph-creator:5000/list-graphs")
    graphs = graphs_request.json()
    for graph_id, uniqued_text in graphs.items():
        try:
            prompt = Prompt(text=uniqued_text, graph_id=graph_id)
            prompt.save(force_insert = True)
        except mongo.errors.DuplicateKeyError:
            pass #It's cool.

class Lesson(modm.MongoModel):
    label = modm.fields.CharField(required = True)
    url_id = modm.fields.CharField(required = True)
    prompts = modm.fields.ListField(modm.fields.ReferenceField(Prompt), default = list,
            blank = True)
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)
    is_public = modm.fields.BooleanField(default = False)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [mongo.operations.IndexModel([('url_id', 1)], 
            unique = True, background = False)] 

    def graphs_ready(self):
        graphs_request = requests.get("http://graph-creator:5000/list-graphs")
        graphs = graphs_request.json()
        for prompt in self.prompts:
            if prompt.graph_id not in graphs:
                return False
        return True

    def is_ready(self):
        return self.graphs_ready()

def create_lesson_with_safe_url_id(label):
    lesson = Lesson()
    lesson.label = label
    url_id = label.lower()
    url_id = secure_filename(url_id) #secure filename is also a pretty good url
    return mongo_serial_unique_attribute(lesson, "url_id", url_id)

def create_and_queue_lesson_from_form(form):
    lesson = create_lesson_with_safe_url_id(form.title.data)
    text = normalize_text(form.raw_text.data)
    sentences = split_text(text)
    #Filter empty:
    sentences = [sentence for sentence in sentences if sentence]
    if not sentences:
        lesson.delete()
        raise ValueError("No sentences remain after filtering")
    for sentence in sentences:
        prompt = Prompt(text = sentence)
        check_prompt_list()
        prompt = mongo_serial_unique_attribute(prompt, "graph_id", lesson.url_id)
        response = requests.post("http://graph-creator:5000/create-graph", 
                json={'key': prompt.graph_id,
                    'prompt': sentence})
        if response.json()["graph_status"] != "queued":
            lesson.delete()
            raise ValueError("GRAPH QUEUEING FAILED")
        lesson.prompts.append(prompt)
        lesson.save()
    return lesson

def split_text(raw_text):
    for hard_punctuation in [".","?","!"]:
        raw_text = raw_text.replace(hard_punctuation, hard_punctuation + "<stop>")
    sentences = raw_text.split("<stop>")
    sentences = sentences[:]
    sentences = [s.strip() for s in sentences]
    return sentences

def normalize_text(raw_text):
    text = re.sub(r"\s+"," ",raw_text) 
    #all lone special symbols:
    text = re.sub(r" [^\w ]* ", "", text, flags=re.UNICODE)
    return text

