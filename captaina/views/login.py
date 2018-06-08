from flask import redirect, url_for, current_app, Blueprint, render_template, flash, request
from flask_login import login_user
from ..forms import UsernamePasswordForm
from ..models import User

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=["GET", "POST"])
def login():
    form = UsernamePasswordForm()
    if form.validate_on_submit():
        try:
            user = User.objects.get({'username':form.username.data})
        except User.DoesNotExist:
            #flash('Invalid username')
            return 'Invalid username'
        if user.is_correct_password(form.password.data):
            login_user(user)
            #flash('You were logged in')
            return 'You were logged in'
        else:
            #flash('Invalid password')
            return 'Invalid password'
    return render_template('login.html', form=form)

