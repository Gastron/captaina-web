from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from ..forms import LessonCreatorForm
from ..models import Lesson, create_and_queue_lesson_from_form

lesson_creator_bp = Blueprint('lesson_creator_bp', __name__)

@lesson_creator_bp.route('/create-lesson', methods=['GET', 'POST'])
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
        return redirect(url_for('dashboard_bp.dashboard'))
    return render_template('lesson_creator.html', form=form)
