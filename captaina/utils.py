from flask import request, url_for, redirect, flash, abort, current_app
from flask_login import current_user
from functools import wraps

#See:
#https://stackoverflow.com/questions/36269485/how-do-i-pass-through-the-next-url-with-flask-and-flask-login
def handle_needs_login():
    #Add this as the unauthorized_handler
    flash("Please log in to access this page.")
    return redirect(url_for('login_bp.login', next=request.endpoint, **request.view_args))
def redirect_dest(fallback):
    dest = request.args.get('next')
    try:
        dest_url = url_for(dest, **request.view_args)
    except:
        return redirect(fallback)
    return redirect(dest_url)

def get_or_404(cls, query):
    #The pattern where you get a resource but 404 for malformed input
    try:
        return cls.objects.get(query)
    except cls.DoesNotExist: #Not found
        abort(404)

def role_restriction(func, role):
    """ Decorator to mark some pages only accessible with certain role accounts """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs)
        elif not current_user.role == role:
            flash("You need to be logged in as a " + role + " to view that page")
            return redirect(url_for('login_bp.login', next=request.endpoint, **request.view_args))
        return func(*args, **kwargs)
    return decorated_view
teacher_only = lambda func: role_restriction(func, "teacher")
student_only = lambda func: role_restriction(func, "student")
    
