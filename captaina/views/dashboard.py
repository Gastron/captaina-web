from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from flask_login import login_required
from ..models import Lesson

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html', lessons=Lesson.objects.all())
