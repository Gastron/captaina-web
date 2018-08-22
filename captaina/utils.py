from flask import request, url_for, redirect, flash, abort

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

