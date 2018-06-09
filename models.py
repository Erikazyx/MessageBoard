from peewee import *
import datetime
from config import db as database


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    username = CharField(unique=True, null=False)
    password = CharField(null=False)

    class Meta:
        db_table = 'user'


class Message(BaseModel):
    user_id = BigIntegerField()
    message = TextField(null=False)
    created_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'message'
