from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from flask_login import login_required, current_user
from ..models import Lesson, Prompt, LessonRecord, cookie_from_lesson_record,\
        get_latest_lesson_record, ensure_and_get_incomplete_lesson_record, \
        lesson_record_from_cookie, AudioReview, fetch_word_alignment, choose_word_alignments
from ..utils import get_or_404, student_only, \
        match_words_and_aligns, pad_aligns, aligns_to_millis, match_aligns_words_and_reviews
import pymongo as mongo

lesson_bp = Blueprint('lesson_bp', __name__)

@lesson_bp.route('/<lesson_url_id>/')
@lesson_bp.route('/<lesson_url_id>/overview')
@login_required
@student_only
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
    lesson_records = attach_cookies(lesson_records)
    return render_template("lesson_overview.html",
            lesson = lesson,
            lesson_records = lesson_records,
            total_prompts = total_prompts,
            all_done = all_done)

def attach_cookies(lesson_records):
    result = []
    for lesson_record in lesson_records:
        setattr(lesson_record, "record_cookie", cookie_from_lesson_record(lesson_record, 
                current_app.config["SECRET_KEY"]))
        result.append(lesson_record)
    return result

@lesson_bp.route('/<lesson_url_id>/start_new/')
@login_required
@student_only
def start_new(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    ensure_and_get_incomplete_lesson_record(current_user, lesson)
    return redirect(url_for('lesson_bp.read',
        lesson_url_id = lesson_url_id))
      
@lesson_bp.route('/<lesson_url_id>/read')
@login_required
@student_only
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

@lesson_bp.route('/<record_cookie>/<int:prompt_num>')
@login_required
@student_only
def browse_reviews(record_cookie, prompt_num):
    try:
        lesson_record = lesson_record_from_cookie(record_cookie, current_app.config["SECRET_KEY"])
    except:
        abort(404)
    try:
        audio_record = lesson_record.validated_audio_records()[prompt_num-1]
    except IndexError:
        return redirect(url_for('lesson_bp.overview',
            lesson_url_id = lesson_record.lesson.url_id))
    try:
        reviews = AudioReview.objects.raw({"audio_record": audio_record.pk})
    except AudioReview.DoesNotExist:
        abort(404)
    word_aligns = fetch_word_alignment(audio_record, current_app.config["AUDIO_UPLOAD_PATH"])
    chosen_aligns = choose_word_alignments(word_aligns)
    millis = aligns_to_millis(chosen_aligns)
    padded = pad_aligns(millis)
    matched_aligns = match_words_and_aligns(audio_record, padded)
    matched_aligns_and_scores = match_aligns_words_and_reviews(matched_aligns, reviews)
    return render_template("show_ratings.html",
            lesson_url_id = lesson_record.lesson.url_id,
            record_cookie = record_cookie,
            audio_record = audio_record,
            word_list = matched_aligns_and_scores,
            next_num = prompt_num+1if prompt_num < lesson_record.num_prompts_completed() else None)

            
