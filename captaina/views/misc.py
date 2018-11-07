from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request

misc_bp = Blueprint('misc_bp', __name__)

@misc_bp.route('/privacy_notice.pdf')
def get_privacy_notice():
    return redirect(url_for('static', 
        filename="privacy_notice/captaina_study_participant_01112018.pdf"))
