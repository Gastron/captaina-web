from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from flask import jsonify, Response
from ..models import LessonRecord, AudioRecord, User, Prompt, Lesson
from ..models import validate_audio_record_files
from ..models import lesson_record_from_cookie
import pymongo as mongo
import itsdangerous

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/log_audio', methods=['POST'])
def log_audio():
    data = request.get_json()
    #Parse the data, handle missing values:
    try:
        user = User.objects.get({"username": data["username"]})
        prompt = Prompt.objects.get({"graph_id": data["graph_id"]})
        lesson_record = LessonRecord.objects.get({"record_key": data["lesson_record_id"]})
        filekey = data["filekey"]
        alignkey = data["alignkey"]
        passed_validation = data["passed_validation"]
    #TODO: Answer better to bad requests
    except IndexError: #Some parameter was omitted from the request
        abort(400)
    except User.DoesNotExist: #The given username does not exist
        abort(400)
    except Prompt.DoesNotExist: #The graph_id did not match a prompt
        abort(400)
    except LessonRecord.DoesNotExist: #The lesson_record_id did not match a lesson record
        abort(400)
    audio_record = AudioRecord(user=user, prompt=prompt, filekey=filekey,
            alignkey=alignkey, passed_validation=passed_validation)
    if not validate_audio_record_files(audio_record):
        abort(400) #Audio files not found
    try:
        audio_record.save()
    except mongo.errors.DuplicateKeyError:
        abort(400) #The align or wav files are already in some record
    lesson_record.audio_records.append(audio_record)
    lesson_record.save()

@api_bp.route('/verify-record-cookie', methods=['POST'])
def verify_record_cookie():
    data = request.get_json()
    cookie = data["record-cookie"]
    try:
        lesson_record_from_cookie(cookie, current_app.config["SECRET_KEY"])
        resp = "OK"
    except LessonRecord.DoesNotExist:
        resp = "LessonRecord not found"
    except itsdangerous.BadData:
        resp = "Bad cookie"
    return Response(resp, status = 200, mimetype = "text/plain")
