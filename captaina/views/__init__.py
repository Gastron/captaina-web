from .login import login_bp
from .dashboard import dashboard_bp
from .feedback import feedback_bp
from .lesson import lesson_bp
from .api import api_bp
from .lesson_creator import lesson_creator_bp

def register_blueprints(app, csrf_protector):
    app.register_blueprint(login_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(lesson_bp, url_prefix='/lessons')
    csrf_protector.exempt(api_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(lesson_creator_bp)
