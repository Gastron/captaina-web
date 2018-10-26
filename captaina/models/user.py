from flask_bcrypt import Bcrypt
import pymodm as modm
import pymongo as mongo
from flask_login import UserMixin
import bson.json_util
from datetime import datetime

#Flask-Bcrypt handles tedious but important security work, so we use it for now
#It doesn't really need flask, though!
fbcrypt = Bcrypt()

def init_crypt_from_flask(app, login_manager=None):
    fbcrypt.init_app(app)
    if login_manager is not None:
        login_manager.user_loader(load_user)

def init_from_config(config):
    #Just set the three configs needed:
    #BCRYPT_LOG_ROUNDS
    #BCRYPT_HASH_PREFIX
    #BCRYPT_HANDLE_LONG_PASSWORDS
    fbcrypt._log_rounds = config['BCRYPT_LOG_ROUNDS']
    fbcrypt._prefix = config['BCRYPT_HANDLE_LONG_PASSWORDS']
    fbcrypt._handle_long_passwords = config['BCRYPT_HANDLE_LONG_PASSWORDS']

class User(modm.MongoModel, UserMixin):
    username = modm.fields.CharField(required = True)
    _password = modm.fields.CharField(required = True)
    email = modm.fields.EmailField()
    role = modm.fields.CharField(required = True, 
            choices = ['student', 'teacher'],
            default = 'student')
    assignee = modm.fields.CharField()
    created = modm.fields.DateTimeField(default = datetime.now)
    modified  = modm.fields.DateTimeField(default = datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [mongo.operations.IndexModel([('username',1)], 
            unique = True)]

    def set_password(self, plaintext):
        self._password = fbcrypt.generate_password_hash(plaintext).decode('utf-8')

    def is_correct_password(self, plaintext):
        return fbcrypt.check_password_hash(self._password, plaintext)
    
    def get_id(self):
        return bson.json_util.dumps(self._id)

def load_user(user_id):
    try:
        return User.objects.get({"_id": bson.json_util.loads(user_id)})
    except User.DoesNotExist:
        return None

def create_user(username, plaintext_password, teacher=False):
    new_user = User()
    new_user.username = username
    new_user.set_password(plaintext_password)
    new_user.role = 'teacher' if teacher else 'student'
    try:
        new_user.save(force_insert=True)
        return new_user
    except mongo.errors.DuplicateKeyError:
        raise ValueError("Username already exists")

def change_password(username, new_plaintext_password):
    try:
        user = User.objects.get({'username':username})
    except User.DoesNotExist:
        raise ValueError("Username not found")
    user.set_password(new_plaintext_password)

