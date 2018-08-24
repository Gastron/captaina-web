from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request, abort
from flask import jsonify, Response
from ..models import LessonRecord, AudioRecord, User, Prompt, Lesson
from ..models import validate_audio_record_files
from ..models import lesson_record_from_cookie
import pymongo as mongo
import itsdangerous

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/log-audio', methods=['POST'])
def log_audio():
    data = request.get_json()
    #Parse the data, handle missing values:
    try:
        record_cookie = data["record-cookie"]
        lesson_record = lesson_record_from_cookie(record_cookie, 
                current_app.config["SECRET_KEY"])
        user = lesson_record.user
        lesson = lesson_record.lesson
        graph_id = data["graph-id"]
        prompt = Prompt.objects.get({"graph_id": graph_id})
        filekey = data["file-key"]
        passed_validation = data["passed-validation"]
    #TODO: Answer better to bad requests
    except IndexError: #Some parameter was omitted from the request
        return Response("Parameters omitted", status = 400, mimetype = "text/plain")
    except Prompt.DoesNotExist:
        return Response("Invalid graph_id", status = 200, mimetype = "text/plain")
    #Create audio record:
    audio_record = AudioRecord(user=user, prompt=prompt, filekey=filekey,
        passed_validation=passed_validation)
    if not validate_audio_record_files(audio_record, 
            current_app.config["AUDIO_UPLOAD_PATH"]):
        return Response("Audio or align not found", status = 200, mimetype = "text/plain")
    try:
        audio_record.save()
    except mongo.errors.DuplicateKeyError:
        abort(400) #The align or wav files are already in some record
    lesson_record.audio_records.append(audio_record)
    lesson_record.save()
    return Response("OK", status = 200, mimetype = "text/plain")

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


