from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import UsernamePasswordForm
from ..models import User
from ..utils import redirect_dest

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=["GET", "POST"])
def login():
    form = UsernamePasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            user = User.objects.get({'username':form.username.data})
            if user.is_correct_password(form.password.data):
                login_user(user)
                flash('You were logged in', category='success')
                return redirect_dest(fallback = url_for('dashboard_bp.dashboard'))
            else:
                flash('Invalid password', category='error')
        except User.DoesNotExist:
            flash('Invalid username', category='error')
    return render_template('login.html', form=form)

@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out', category='success')
    return redirect(url_for('login_bp.login'))
