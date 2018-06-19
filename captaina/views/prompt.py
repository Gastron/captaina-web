from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from flask_login import login_required
from ..models import Lesson, Prompt

prompt_bp = Blueprint('prompt_bp', __name__)

@prompt_bp.route('/<lesson_url_id>/<promptnum>')
@login_required
def prompt(lesson_url_id, promptnum):
    lesson = Lesson.objects.get()
