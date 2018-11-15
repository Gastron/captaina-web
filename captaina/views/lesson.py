from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from flask_login import login_required, current_user
from ..models import Lesson, Prompt, LessonRecord, cookie_from_record,\
        record_from_cookie, AudioReview, get_matched_alignment, \
        get_or_make_lesson_record, get_record, get_references_for_prompt
from ..utils import get_or_404, student_only, match_alignment_words_and_reviews
import pymongo as mongo

lesson_bp = Blueprint('lesson_bp', __name__)

@lesson_bp.route('/<lesson_url_id>/')
@lesson_bp.route('/<lesson_url_id>/overview')
@login_required
@student_only
def overview(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    if not lesson.is_public:
        abort(403)
    lesson_record = get_or_make_lesson_record(current_user, lesson)
    if lesson_record.is_new():
        return redirect(url_for('lesson_bp.read',
            lesson_url_id = lesson_url_id,
            graph_id = lesson.prompts[0].graph_id))
    total_prompts = len(lesson.prompts)
    return render_template("lesson_overview.html",
            lesson = lesson,
            lesson_record = lesson_record,
            total_prompts = total_prompts)
      
@lesson_bp.route('/<lesson_url_id>/<graph_id>/read')
@login_required
@student_only
def read(lesson_url_id, graph_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    lesson_record = get_or_make_lesson_record(current_user, lesson)
    if lesson_record.submitted:
        flash("You have already submitted your work", category = "error")
        return redirect(url_for('lesson_bp.overview',
            lesson_url_id = lesson_url_id))
    try:
        #Find the prompt in the lesson (verify input) 
        prompt_index, prompt = [(i, prompt) for i, prompt in enumerate(lesson.prompts)
            if prompt.graph_id == graph_id][0] #[0] to pick the first; there should only be one
    except IndexError:
        abort(404)
    total_prompts = len(lesson.prompts)
    record_cookie = cookie_from_record(lesson_record, current_app.config["SECRET_KEY"])
    return render_template("prompt.html", 
            lesson = lesson, 
            prompt = prompt,
            promptnum = prompt_index + 1,
            total_prompts = total_prompts,
            record_cookie = record_cookie,
            reference_record = False) #We are not making a reference recording

@lesson_bp.route('/<lesson_url_id>/<graph_id>/read_next')
@login_required
@student_only
def read_next(lesson_url_id, graph_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    try:
        #Find the prompt in the lesson (verify input) 
        prompt_index, prompt = [(i, prompt) for i, prompt in enumerate(lesson.prompts)
            if prompt.graph_id == graph_id][0] #[0] to pick the first; there should only be one
    except IndexError:
        abort(404)
    if (prompt_index + 1) == len(lesson.prompts):
        flash("All done", category="success")
        return redirect(url_for('lesson_bp.overview',
            lesson_url_id = lesson_url_id))
    else:
        return redirect(url_for('lesson_bp.read',
            lesson_url_id = lesson_url_id,
            graph_id = lesson.prompts[prompt_index+1].graph_id))

@lesson_bp.route('/<lesson_url_id>/<graph_id>/see_review')
@login_required
@student_only
def see_review(lesson_url_id, graph_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    lesson_record = get_or_make_lesson_record(current_user, lesson)
    try:
        #Find the prompt in the lesson (verify input) 
        prompt_index, prompt = [(i, prompt) for i, prompt in enumerate(lesson.prompts)
            if prompt.graph_id == graph_id][0] #[0] to pick the first; there should only be one
    except IndexError:
        abort(404)
    student_audio_record = lesson_record.get_audiorecord(prompt)
    if student_audio_record is None:
        return redirect(url_for("lesson_bp.read", 
            lesson_url_id = lesson_url_id,
            graph_id = graph_id))
    teacher_audio_records = get_references_for_prompt(lesson, prompt)
    try:
        reviews = AudioReview.objects.raw({"audio_record": student_audio_record.pk})
        comments = [review.get_comment() for review in reviews if review.get_comment() is not None]
    except AudioReview.DoesNotExist:
        reviews = []
        comments = []

    #Student's aligns:
    student_matched_alignment = get_matched_alignment(student_audio_record,
            current_app.config["AUDIO_UPLOAD_PATH"])

    #Reference aligns: 
    teacher_matched_alignments = [
            (audio_rec, get_matched_alignment(audio_rec, current_app.config["AUDIO_UPLOAD_PATH"]))
            for audio_rec in teacher_audio_records]

    matched_reviews = match_alignment_words_and_reviews(
            student_matched_alignment,
            reviews)

    return render_template("show_ratings.html",
            lesson = lesson,
            prompt = prompt,
            lesson_record = lesson_record,
            audio_record = student_audio_record,
            word_list = matched_reviews, #TODO: Call this something else than word_list
            comments = comments,
            teacher_alignments = teacher_matched_alignments)

@lesson_bp.route('/<lesson_url_id>/<graph_id>/see_next_review')
@login_required
@student_only
def see_next_review(lesson_url_id, graph_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    try:
        #Find the prompt in the lesson (verify input) 
        prompt_index, prompt = [(i, prompt) for i, prompt in enumerate(lesson.prompts)
            if prompt.graph_id == graph_id][0] #[0] to pick the first; there should only be one
    except IndexError:
        abort(404)
    if (prompt_index + 1) == len(lesson.prompts):
        flash("All done", category="success")
        return redirect(url_for('lesson_bp.overview',
            lesson_url_id = lesson_url_id))
    else:
        return redirect(url_for('lesson_bp.see_review',
            lesson_url_id = lesson_url_id,
            graph_id = lesson.prompts[prompt_index+1].graph_id))
            
@lesson_bp.route('/<lesson_url_id>/submit', methods = ["POST"])
@login_required
@student_only
def submit(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    lesson_record = get_or_make_lesson_record(current_user, lesson)
    if not lesson_record.is_complete():
        flash("You have not read all sentences yet!", category="error")
        return redirect(url_for('lesson_bp.overview',
            lesson_url_id = lesson_url_id))
    if lesson_record.submitted:
        flash("You have already submitted this lesson.", category="info")
        return redirect(url_for('lesson_bp.overview',
            lesson_url_id = lesson_url_id))
    lesson_record.submitted = True
    lesson_record.save() 
    flash("Submitted for teacher's rating.", category="success")
    return redirect(url_for('lesson_bp.overview',
        lesson_url_id = lesson_url_id))
