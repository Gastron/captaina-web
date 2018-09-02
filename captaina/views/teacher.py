from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request,\
        send_from_directory
from flask_login import login_required, current_user
from ..models import Lesson, Prompt, LessonRecord, AudioReview, \
        cookie_from_lesson_record, lesson_record_from_cookie, \
        create_and_queue_lesson_from_form, fetch_word_alignment, choose_word_alignments
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

@teacher_bp.route('/lesson/<lesson_url_id>')
@login_required
@teacher_only
def lesson_overview(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    records = LessonRecord.objects.raw({'lesson': lesson.pk}).order_by([('modified', mongo.DESCENDING)])
    filtered = filter(lambda record: record.is_complete(), records)
    filtered = filter(lambda record: record.user.username == current_user.assignee, records)
    filtered = filter(lambda record: 
            next_audio_record_to_review(record, current_user) is not None, filtered)
    record_cookies = map(lambda r: cookie_from_lesson_record(r, current_app.config["SECRET_KEY"]),
            records)
    return render_template('lesson_review.html', 
            lesson = lesson, 
            records = zip(filtered, record_cookies))

@teacher_bp.route('/lesson/<lesson_url_id>/delete/', methods = ['GET'])
@login_required
@teacher_only
def delete_lesson(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    lesson.delete()
    flash("Lesson deleted", category="success")
    return redirect(url_for('teacher_bp.overview'))

@teacher_bp.route('/lesson/<lesson_url_id>/review/<record_cookie>/next', methods = ['GET', 'POST'])
@login_required
@teacher_only
def review_lesson_record(lesson_url_id, record_cookie):
    lesson_record = lesson_record_from_cookie(record_cookie, current_app.config["SECRET_KEY"])
    audio_record = next_audio_record_to_review(lesson_record, current_user)
    if request.method == 'GET' and audio_record is None:
        flash("Review completed", category="success")
        return redirect(url_for('teacher_bp.lesson_overview',
            lesson_url_id = lesson_url_id))
    word_aligns = fetch_word_alignment(audio_record, current_app.config["AUDIO_UPLOAD_PATH"])
    chosen_aligns = choose_word_alignments(word_aligns)
    millis = aligns_to_millis(chosen_aligns)
    padded = pad_aligns(millis)
    matched = match_words_and_aligns(audio_record, padded)
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

def aligns_to_millis(aligns):
    return [{
        "word": align["word"], 
        "start": int(1000*align["start"]),
        "length": int(1000*align["length"])} for align in aligns]

def pad_aligns(aligns, front_pad=20, end_pad=20):
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
    return list(zip(words, aligns, range(len(words))))

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
