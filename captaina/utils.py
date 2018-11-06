from flask import request, url_for, redirect, flash, abort, current_app, Flask
from werkzeug import DispatcherMiddleware
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

def average_review(reviews):
    """ Returns the mean review score. If more than half of all reviews were na, returns na"""
    if not reviews: return "na"
    no_na = list(filter(lambda r: r != "na", reviews))
    if len(no_na) <= len(reviews)/2:
        return "na"
    else:
        return sum(map(int, no_na)) // len(no_na) #With rounding

def match_alignment_words_and_reviews(matched_aligns, reviews):
    matched = []
    for word, align, word_index in matched_aligns:
        this_word_reviews = [review.get_rating(align["word"]) for review in reviews]
        matched.append({"as_written": word,
            "word_id": align["word"],
            "score": average_review(this_word_reviews),
            "start": align["start"],
            "length": align["length"]})
    return matched

def prefix_application_path(app, prefix):
    """ Add a prefix to all URLs. Need this typically for serving the whole application
    under a proxy """
    app.wsgi_app = DispatcherMiddleware(Flask('dummy_app'), #for 404,
        {prefix: app.wsgi_app})
