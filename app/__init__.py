from flask import Flask, session
from config import SECRET_KEY
from models import database, User, Message

app = Flask(__name__)


def create_app():
    database.connect()
    database.create_tables([User, Message])
    app.secret_key = SECRET_KEY
    from app.auth import auth as auth_blueprint
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint, )
    app.register_blueprint(auth_blueprint)
    return app


@app.context_processor
def getuser():
    user_id = session.get("user_id")
    if user_id:
        user = User.select().where(User.id == user_id).get()
        if user:
            return {"user": user}
    return {}



