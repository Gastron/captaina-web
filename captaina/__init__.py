from flask import Flask
from flask_bcrypt import Bcrypt
fbcrypt = Bcrypt()

def create_app(**config_overrides):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config')
    app.config.from_pyfile('config.py')
    app.config.update(config_overrides)

    fbcrypt.init_app(app)
    import pymodm as modm
    modm.connect(app.config['MONGO_DATABASE_URI'])
    return app

