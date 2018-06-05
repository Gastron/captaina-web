from . import flask_bcrypt, app
import pymodm as modm
import pymongo as mongo

modm.connect(app.config["MONGO_DATABASE_URI"])

class User(modm.MongoModel):
    username = modm.fields.CharField(required = True)
    _password = modm.fields.CharField(required = True)
    email = modm.fields.EmailField()
    class Meta:
        indexes = [mongo.operations.IndexModel([('username', mongo.TEXT)], unique = True)]

    def set_password(self, plaintext):
        self._password = flask_bcrypt.generate_password_hash(plaintext).decode('utf-8')

    def is_correct_password(self, plaintext):
        return flask_bcrypt.check_password_hash(self._password, plaintext)

