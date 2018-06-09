# -*- coding: UTF-8 -*-
from flask import Flask, render_template, request, flash, session, redirect, url_for
from models import database, User, Message
from flask import jsonify
from config import gt, r, SECRET_KEY
from page import get_page_index, Page

database.connect()
database.create_tables([User, Message])

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/gtinit', methods=["GET"])
def get_pc_captcha():
    if session.get('user_id'):
        user_id = session['user_id']
    else:
        number = request.form.get('number')
        user_id = number
    status = gt.pre_process(user_id)
    session[gt.GT_STATUS_SESSION_KEY] = status
    response_str = gt.get_response_str()
    return response_str


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        page = request.args.get('page')
        if not page:
            page = 1
        page_index = get_page_index(page)
        messages = Message.select().order_by(Message.created_date.desc())
        author = {}
        if not messages:
            messages = []
        else:
            message_count = messages.count()
            page = Page(message_count, page_index)
            messages = messages[page.offset: page.limit]
            for message in messages:
                if User.select().where(User.id == message.user_id):
                    author[message.id] = User.select().where(User.id == message.user_id).get().username
        return render_template('main_geetest.html', messages=messages, pagination=page, author=author)
    else:
        subtype = request.form.get('type')
        content = request.form.get('content')
        if not content:
            flash('必须输入内容')
            return redirect(url_for('main'))
        if session.get('user_id'):
            user_id = session['user_id']
        else:
            number = request.form.get('number')
            user_id = number
        if subtype == 'captcha':
            challenge = request.form[gt.FN_CHALLENGE]
            validate = request.form[gt.FN_VALIDATE]
            seccode = request.form[gt.FN_SECCODE]
            status = session[gt.GT_STATUS_SESSION_KEY]
            if status:
                result = gt.success_validate(challenge, validate, seccode, user_id)
            else:
                result = gt.failback_validate(challenge, validate, seccode)
            if not result:
                flash('验证失败请重试')
                return redirect(url_for('main'))
            r.delete('needtest')
            Message.create(user_id=user_id, message=content)
            return redirect(url_for('main'))
        if r.exists(user_id):
            r.set('needtest', 1)
            flash('短时间内提交过多，请验证后发表')
            return redirect(url_for('main'))
        if not r.exists(user_id):
            pipe = r.pipeline(transaction=True)
            r.incr(user_id, 1)
            r.expire(user_id, 5)
            pipe.execute()
        Message.create(user_id=user_id, message=content)
        return redirect(url_for('main'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        user = request.form.get('user')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if not user:
            flash('请输入用户名！')
            return render_template('register.html')
        if len(user) < 3 or len(user) > 32:
            flash('用户名长度不对（大于3个字符且小于32个字符）')
            return render_template('register.html')
        if User.select().where(User.username == user):
            flash('该用户名已被注册！')
            return render_template('register.html')
        if not password1 or not password2:
            flash('请输入密码！')
            return render_template('register.html')
        if len(password1) < 6 or len(password1) > 24:
            flash('密码长度不对（大于6个字符且小于24个字符）')
            return render_template('register.html')
        if password1 != password2:
            flash('两次密码输入不同！')
            return render_template('register.html')
        User.create(username=user, password=password1)
        return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user = request.form.get('username')
        password = request.form.get('password')
        if not user or not password:
            flash('please input username and password!')
            return render_template('login.html')
        elif not User.select().where(User.username == user) or User.select().where(
                User.username == user).get().password != password:
            flash('wrong username or wrong password,try again')
            return render_template('login.html')
        else:
            user = User.select().where(User.username == user).get()
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('main'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))


@app.context_processor
def getuser():
    user_id = session.get('user_id')
    if user_id:
        user = User.select().where(User.id == user_id).get()
        if user:
            return {'user': user}
    return {}


@app.route('/isvalid/')
def isvalid():
    valid = r.exists('needtest')
    return jsonify({'valid': valid})


if __name__ == '__main__':
    app.run()
