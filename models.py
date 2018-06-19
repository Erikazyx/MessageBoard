from peewee import Model, CharField, BigIntegerField, TextField, DateTimeField
import datetime
from config import db as database
from werkzeug.security import generate_password_hash, check_password_hash


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    username = CharField(unique=True, null=False)
    password = CharField(null=False)

    @property
    def password_hash(self):
        raise AttributeError('该属性不可读')

    @password_hash.setter
    def password_hash(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    class Meta:
        db_table = 'user'


class Message(BaseModel):
    user_id = BigIntegerField()
    message = TextField(null=False)
    created_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'message'
