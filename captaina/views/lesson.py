from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request, abort
from flask_login import login_required
from ..models import Lesson, Prompt

lesson_bp = Blueprint('lesson_bp', __name__)

@lesson_bp.route('/<lesson_url_id>/')
@lesson_bp.route('/<lesson_url_id>/overview')
@login_required
def overview(lesson_url_id):
    try:
        lesson = Lesson.objects.get({'url_id': lesson_url_id})
    except Lesson.DoesNotExist:
        abort(404)
    return redirect(url_for('lesson_bp.prompt',
            lesson_url_id = lesson_url_id,
            promptnum = 1))
      
@lesson_bp.route('/<lesson_url_id>/<int:promptnum>')
@login_required
def prompt(lesson_url_id, promptnum):
    if promptnum <=0:
        abort(404)
    prompt_index = promptnum-1
    try:
        lesson = Lesson.objects.get({'url_id': lesson_url_id})
        prompt = lesson.prompts[prompt_index]
    except (Lesson.DoesNotExist, IndexError) as e:
        abort(404)
    total_prompts = len(lesson.prompts)
    return render_template("prompt.html", 
            lesson = lesson, 
            prompt=prompt,
            promptnum=promptnum,
            total_prompts=total_prompts)
