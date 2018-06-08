from .login import login_bp

def register_blueprints(app):
    app.register_blueprint(login_bp)
