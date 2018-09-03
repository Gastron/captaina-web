import os
from flask import Flask
from flask_bcrypt import Bcrypt
import pymodm as modm
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from .jinja_filters import register_jinja_filters
fbcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    instance_path = os.environ["FLASK_INSTANCE_PATH"]
    app = Flask('captaina', 
            instance_path=instance_path, 
            instance_relative_config=True)

    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    csrf.init_app(app) 
    fbcrypt.init_app(app)
    login_manager.init_app(app)
    from .utils import handle_needs_login
    login_manager.unauthorized_handler(handle_needs_login)
    modm.connect(app.config['MONGO_DATABASE_URI'])
    from .models import init_crypt_from_flask
    init_crypt_from_flask(app, login_manager)
    print("Connected to", app.config['MONGO_DATABASE_URI'])
    from .views import register_blueprints
    register_blueprints(app, csrf)
    from .cli import register_cli
    register_cli(app)
    register_jinja_filters(app)
    return app

