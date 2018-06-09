from peewee import MySQLDatabase
from geetest import GeetestLib
import redis

db = MySQLDatabase('database', **{'host': 'host', 'password': 'password', 'port': 'post', 'user': 'user'})

pc_geetest_key = "YourGeetestKey"
pc_geetest_id = "YourGeetestID"

gt = GeetestLib(pc_geetest_id,pc_geetest_key)

pool = redis.ConnectionPool(host='host', port='port', db=0)
r = redis.Redis(connection_pool=pool)

SECRET_KEY = 'YourSecretKey'