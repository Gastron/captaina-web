from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request,\
        send_from_directory, abort
from flask_login import login_required, current_user
from ..models import Lesson, Prompt, LessonRecord, AudioReview, \
        create_and_queue_lesson_from_form, get_matched_alignment, \
        cookie_from_record, record_from_cookie, get_or_make_reference_record
from ..forms import LessonCreatorForm, EmptyForm
from ..utils import get_or_404, teacher_only
import pymongo as mongo

teacher_bp = Blueprint('teacher_bp', __name__)

@teacher_bp.route('/')
@teacher_bp.route('/overview')
@login_required
@teacher_only
def overview():
    return render_template('teacher_panel.html', lessons=Lesson.objects.all())

@teacher_bp.route('/create-lesson', methods=['GET', 'POST'])
@login_required
@teacher_only
def create_lesson():
    form = LessonCreatorForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            create_and_queue_lesson_from_form(form)
        except ValueError:
            flash("Invalid data", category="error")
            return render_template('lesson_creator.html', form=form)
        flash("Lesson submission successful", category="success")
        flash("Compiling ASR decode graphs, this may take a while", category="info")
        return redirect(url_for('teacher_bp.overview'))
    return render_template('lesson_creator.html', form=form)

#TODO: this should be named similarly, and the url should be the same, as in lesson_bp
@teacher_bp.route('/lesson/<lesson_url_id>')
@login_required
@teacher_only
def lesson_overview(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    records = LessonRecord.objects.raw({'lesson': lesson.pk}).order_by([('modified', mongo.DESCENDING)])
    filtered = filter(lambda record: record.is_complete() and record.submitted, records)
    filtered = filter(lambda record: 
            next_audio_record_to_review(record, current_user) is not None, filtered)
    record_cookies = map(lambda r: cookie_from_record(r, current_app.config["SECRET_KEY"]),
            records)
    return render_template('lesson_review.html', 
            lesson = lesson, 
            records = zip(filtered, record_cookies),
            reference_record = get_or_make_reference_record(current_user, lesson))

@teacher_bp.route('/lesson/<lesson_url_id>/<graph_id>/read')
@login_required
@teacher_only
def read(lesson_url_id, graph_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    record = get_or_make_reference_record(current_user, lesson)
    try:
        #Find the prompt in the lesson (verify input) 
        prompt_index, prompt = [(i, prompt) for i, prompt in enumerate(lesson.prompts)
            if prompt.graph_id == graph_id][0] #[0] to pick the first; there should only be one
    except IndexError:
        abort(404)
    record_cookie = cookie_from_record(record, current_app.config["SECRET_KEY"])
    return render_template("prompt.html", 
            lesson = lesson, 
            prompt = prompt,
            promptnum = prompt_index + 1,
            total_prompts = len(lesson.prompts),
            record_cookie = record_cookie,
            reference_record = True) 

@teacher_bp.route('/<lesson_url_id>/<graph_id>/read_next')
@login_required
@teacher_only
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
        return redirect(url_for('teacher_bp.lesson_overview',
            lesson_url_id = lesson_url_id))
    else:
        return redirect(url_for('teacher_bp.read',
            lesson_url_id = lesson_url_id,
            graph_id = lesson.prompts[prompt_index+1].graph_id))

@teacher_bp.route('/lesson/<lesson_url_id>/<graph_id>/reference')
@login_required
@teacher_only
def review_reference(lesson_url_id, graph_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    record = get_or_make_reference_record(current_user, lesson)
    try:
        #Find the prompt in the lesson (verify input) 
        prompt_index, prompt = [(i, prompt) for i, prompt in enumerate(lesson.prompts)
            if prompt.graph_id == graph_id][0] #[0] to pick the first; there should only be one
    except IndexError:
        abort(404)
    audio_record = record.get_reference(prompt)
    if audio_record is None:
        abort(404)
    matched_aligns = get_matched_alignment(audio_record, current_app.config["AUDIO_UPLOAD_PATH"])
    return render_template("review_reference.html",
            lesson = lesson,
            prompt = prompt,
            word_alignment = matched_aligns,
            audio_record = audio_record)

@teacher_bp.route('/lesson/<lesson_url_id>/publish', methods = ['POST'])
@login_required
@teacher_only
def publish_lesson(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    lesson.is_public = True
    lesson.save()
    flash("Lesson published", category = "success")
    return redirect(url_for('teacher_bp.lesson_overview',
        lesson_url_id = lesson_url_id))

@teacher_bp.route('/lesson/<lesson_url_id>/unpublish', methods = ['POST'])
@login_required
@teacher_only
def unpublish_lesson(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    lesson.is_public = False
    lesson.save()
    flash("Lesson unpublished", category = "success")
    return redirect(url_for('teacher_bp.lesson_overview',
        lesson_url_id = lesson_url_id))

@teacher_bp.route('/lesson/<lesson_url_id>/review/<record_cookie>/next', methods = ['GET', 'POST'])
@login_required
@teacher_only
def review_lesson_record(lesson_url_id, record_cookie):
    lesson_record = record_from_cookie(record_cookie, current_app.config["SECRET_KEY"])
    audio_record = next_audio_record_to_review(lesson_record, current_user)
    if request.method == 'GET' and audio_record is None:
        flash("Review completed", category="success")
        return redirect(url_for('teacher_bp.lesson_overview',
            lesson_url_id = lesson_url_id))
    matched = get_matched_alignment(audio_record, current_app.config["AUDIO_UPLOAD_PATH"])
    form = EmptyForm() #For CSRF token
    if request.method == 'POST' and form.validate_on_submit():
        review = dict(request.form)
        review.pop("csrf_token")
        audio_review = AudioReview(reviewer = current_user.pk,
            audio_record = audio_record.pk,
            review = review)
        audio_review.save()
        flash("Ratings saved", category="success")
        return redirect(url_for('teacher_bp.review_lesson_record',
            lesson_url_id = lesson_url_id,
            record_cookie = record_cookie))
    else:
        return render_template("review.html", 
                form = form,
                audio_record = audio_record,
                word_alignment = matched)


def next_audio_record_to_review(lesson_record, user):
    for audio_record in lesson_record.validated_audio_records():
        try:
            AudioReview.objects.get({"reviewer": user.pk,
                "audio_record": audio_record.pk})
        except AudioReview.DoesNotExist:
            return audio_record
    return None

@teacher_bp.route('get-wav/<filekey>.wav')
@login_required
def get_wav(filekey):
    return send_from_directory(current_app.config["AUDIO_UPLOAD_PATH"],
            filekey + ".wav")

@teacher_bp.route('get-ogg/<filekey>.ogg')
@login_required
def get_ogg(filekey):
    return send_from_directory(current_app.config["AUDIO_UPLOAD_PATH"],
            filekey + ".ogg")
