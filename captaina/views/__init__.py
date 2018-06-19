from .login import login_bp
from .dashboard import dashboard_bp
from .feedback import feedback_bp
from .lesson import lesson_bp

def register_blueprints(app):
    app.register_blueprint(login_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(lesson_bp, url_prefix='/lessons')
