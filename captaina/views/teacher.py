from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from flask_login import login_required, current_user
from ..models import Lesson, Prompt, LessonRecord, AudioReview, \
        cookie_from_lesson_record, lesson_record_from_cookie \
        create_and_queue_lesson_from_form
from ..forms import LessonCreatorForm
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
    record_cookies = map(lambda r: cookie_from_lesson_record(r, current_app.config["SECRET_KEY"]),
            records)
    return render_template('lesson_review.html', 
            lesson = lesson, 
            records = filtered, 
            record_cookies = record_cookies)

@teacher_bp.route('/lesson/<lesson_url_id>/delete/', methods = ['GET'])
@login_required
@teacher_only
def delete_lesson(lesson_url_id):
    lesson = get_or_404(Lesson, {'url_id': lesson_url_id})
    lesson.delete()
    flash("Lesson deleted", category="success")
    return redirect(url_for('teacher_bp.overview'))

@teacher_bp.route('/lesson/review/<record_cookie>/next', methods = ['GET', 'POST'])
@login_required
@teacher_only
def review_lesson_record(record_cookie):
    lesson_record = lesson_record_from_cookie(record_cookie, current_app.config["SECRET_KEY"])
    for audio_record in [record for record in lesson_record.audio_records if record.passed_validation]:
        try: 
            AudioReview.objects.get({"reviewer": current_user.pk, 
                "audio_record": audio_record.pk})
        except AudioReview.DoesNotExist:
            word_aligns = choose_word_alignments(fetch_word_alignment(audio_record, current_app.confg["AUDIO_UPLOAD_PATH"]))
            return render_template("review.html", 
                    audio_record = audio_record, 
                    word_alignment = 



