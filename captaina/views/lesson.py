from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from flask_login import login_required, current_user
from ..models import Lesson, Prompt, LessonRecord, cookie_from_lesson_record,\
        get_latest_lesson_record, ensure_and_get_incomplete_lesson_record
from ..utils import get_or_404
import pymongo as mongo

lesson_bp = Blueprint('lesson_bp', __name__)

@lesson_bp.route('/<lesson_url_id>/')
@lesson_bp.route('/<lesson_url_id>/overview')
@login_required
def overview(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    try:
        lesson_record = get_latest_lesson_record(current_user, lesson)
    except LessonRecord.DoesNotExist:
        return redirect(url_for('lesson_bp.start_new',
            lesson_url_id = lesson_url_id))
    lesson_records = LessonRecord.objects.raw({
        'user': current_user.pk, 
        'lesson': lesson.pk})
    total_prompts = len(lesson.prompts)
    all_done = all(lesson_record.is_complete() for lesson_record in lesson_records)
    return render_template("lesson_overview.html",
            lesson = lesson,
            lesson_records = lesson_records,
            total_prompts = total_prompts,
            all_done = all_done)

@lesson_bp.route('/<lesson_url_id>/delete/', methods = ['GET'])
@login_required
def delete_lesson(lesson_url_id):
    if lesson_url_id == 'the_beginning':
        flash("You may not delete The Beginning", category="warning")
        return redirect(url_for('dashboard_bp.dashboard'))
    else:
        lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
        lesson.delete()
        flash("Lesson deleted", category="success")
        return redirect(url_for('dashboard_bp.dashboard'))



            

@lesson_bp.route('/<lesson_url_id>/start_new/')
@login_required
def start_new(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    ensure_and_get_incomplete_lesson_record(current_user, lesson)
    return redirect(url_for('lesson_bp.read',
        lesson_url_id = lesson_url_id))
    

      
@lesson_bp.route('/<lesson_url_id>/read')
@login_required
def read(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    lesson_record = get_latest_lesson_record(current_user, lesson)
    if lesson_record.is_complete():
        return redirect(url_for('lesson_bp.overview',
                lesson_url_id = lesson_url_id))
    prompt_index = lesson_record.num_prompts_completed()
    total_prompts = len(lesson.prompts)
    prompt = lesson.prompts[prompt_index]
    record_cookie = cookie_from_lesson_record(lesson_record, current_app.config["SECRET_KEY"])
    current_app.logger.info(record_cookie)
    return render_template("prompt.html", 
            lesson = lesson, 
            prompt = prompt,
            promptnum = prompt_index + 1,
            total_prompts = total_prompts,
            record_cookie = record_cookie) 

