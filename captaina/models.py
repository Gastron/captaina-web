from . import fbcrypt, login_manager
import pymodm as modm
import pymongo as mongo
from flask_login import UserMixin
import bson.json_util

class User(modm.MongoModel, UserMixin):
    username = modm.fields.CharField(required = True)
    _password = modm.fields.CharField(required = True)
    email = modm.fields.EmailField()
    class Meta:
        indexes = [mongo.operations.IndexModel([('username', mongo.TEXT)], unique = True)]

    def set_password(self, plaintext):
        self._password = fbcrypt.generate_password_hash(plaintext).decode('utf-8')

    def is_correct_password(self, plaintext):
        return fbcrypt.check_password_hash(self._password, plaintext)
    
    def get_id(self):
        return bson.json_util.dumps(self._id)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.objects.get({"_id": bson.json_util.loads(user_id)})
    except User.DoesNotExist:
        return None

def create_user(username, plaintext_password):
    new_user = User()
    new_user.username = username
    new_user.set_password(plaintext_password)
    try:
        new_user.save(force_insert=True)
    except mongo.errors.DuplicateKeyError as e:
        raise ValueError("Username already exists")

def change_password(username, new_plaintext_password):
    try:
        user = User.objects.get({'username':username})
    except User.DoesNotExist:
        raise ValueError("Username not found")
    user.set_password(new_plaintext_password)
