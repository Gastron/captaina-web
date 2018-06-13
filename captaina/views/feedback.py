from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from ..forms import FeedbackForm
from ..models import Feedback

feedback_bp = Blueprint('feedback_bp', __name__)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_feedback = Feedback()
        new_feedback.message = form.message.data
        new_feedback.save()
        flash("Feedback submitted", category="success")
        return render_template('thanks.html')
    return render_template('feedback.html', form=form)
