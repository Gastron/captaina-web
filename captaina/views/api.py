from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request, abort
from flask import jsonify, Response
from ..models import LessonRecord, AudioRecord, User, Prompt, Lesson
from ..models import validate_audio_record_files
from ..models import record_from_cookie
import pymongo as mongo
import itsdangerous

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/log-audio', methods=['POST'])
def log_audio():
    data = request.get_json()
    #Parse the data, handle missing values:
    try:
        record_cookie = data["record-cookie"]
        record = record_from_cookie(record_cookie, 
                current_app.config["SECRET_KEY"])
        user = record.user
        lesson = record.lesson
        graph_id = data["graph-id"]
        prompt = Prompt.objects.get({"graph_id": graph_id})
        filekey = data["file-key"]
        passed_validation = data["passed-validation"]
    #TODO: Answer better to bad requests
    except IndexError: #Some parameter was omitted from the request
        current_app.logger.info("Missing parameters in log-audio request")
        return Response("Parameters omitted", status = 400, mimetype = "text/plain")
    except Prompt.DoesNotExist:
        current_app.logger.info("Invalid graph_id in log-audio request")
        return Response("Invalid graph_id", status = 400, mimetype = "text/plain")
    try:
        if record.submitted:
            abort(403)
    except AttributeError:
        pass #ReferenceRecord has no "submitted"
    #Create audio record:
    audio_record = AudioRecord(user=user, prompt=prompt, filekey=filekey,
        passed_validation=passed_validation)
    if not validate_audio_record_files(audio_record, 
            current_app.config["AUDIO_UPLOAD_PATH"]):
        current_app.logger.info("Audio or align not found in log-audio request")
        return Response("Audio or align not found", status = 200, mimetype = "text/plain")
    try:
        audio_record.save(force_insert = True)
    except mongo.errors.DuplicateKeyError:
        current_app.logger.info("Duplicate request in log-audio")
        abort(400) #The align or wav files are already in some record
    try:
        record.audio_records.append(audio_record)
        record.save()
        return Response("OK", status = 200, mimetype = "text/plain")
    except:
        current_app.logger.info("Error in log-audio")
        return Response("Unknown error", status = 500, mimetype = "text/plain")

@api_bp.route('/verify-record-cookie', methods=['POST'])
def verify_record_cookie():
    data = request.get_json()
    cookie = data["record-cookie"]
    try:
        record = record_from_cookie(cookie, current_app.config["SECRET_KEY"])
        try:
            if not record.submitted:
                resp = "OK"
            else:
                resp = "Record already submitted"
        except AttributeError:
            resp = "OK"
    except ValueError:
        resp = "Record not found"
    except itsdangerous.BadData:
        resp = "Bad cookie"
    return Response(resp, status = 200, mimetype = "text/plain")


