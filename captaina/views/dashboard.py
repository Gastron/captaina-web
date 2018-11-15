from flask import redirect, url_for, current_app, Blueprint, \
        render_template, flash, request
from flask_login import login_required, current_user
from ..models import Lesson, get_or_make_lesson_record
from ..utils import student_only

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
@student_only
def dashboard():
    lessons = Lesson.objects.raw({"is_public":True})
    lessons = list((lesson, get_or_make_lesson_record(current_user, lesson)) 
            for lesson in lessons)
    print(lessons[0][1].lesson.label)
    lessons = list((lesson, lesson_record.reviews_exist()) for lesson, lesson_record in
            lessons)
    return render_template('dashboard.html', lessons=lessons)
