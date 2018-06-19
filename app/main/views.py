# -*- coding: UTF-8 -*-
from app.main import main
from flask import session, request, redirect, render_template, flash, jsonify, url_for
from config import r, gt
from tools import get_id, Page, get_page_index
from models import Message, User


@main.route("/gtinit", methods=["GET"])
def get_pc_captcha():
    user_id = get_id()
    status = gt.pre_process(user_id)
    session[gt.GT_STATUS_SESSION_KEY] = status
    response_str = gt.get_response_str()
    return response_str


@main.route("/", methods=["GET"])
def main_page():
    page = request.args.get("page")
    if not page:
        page = 1
    page_index = get_page_index(page)
    messages = Message.select().order_by(Message.created_date.desc())
    author = {}
    if not messages:
        messages = []
    else:
        for message in messages:
            user = User.select().where(User.id == message.user_id)
            if user:
                author[message.user_id] = user.get().username
        message_count = messages.count()
        page = Page(message_count, page_index)
        messages = messages[page.offset : page.limit]

    return render_template(
        "main_geetest.html", messages=messages, pagination=page, author=author
    )


@main.route("/", methods=["POST"])
def submit():
    subtype = request.form.get("type")
    content = request.form.get("content")
    if not content:
        flash("必须输入内容")
        return redirect(url_for("main.main_page"))
    user_id = get_id()
    if subtype == "captcha":
        challenge = request.form[gt.FN_CHALLENGE]
        validate = request.form[gt.FN_VALIDATE]
        seccode = request.form[gt.FN_SECCODE]
        status = session[gt.GT_STATUS_SESSION_KEY]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if not result:
            flash("验证失败请重试")
            return redirect(url_for("main.main_page"))
        r.delete("needtest")
        Message.create(user_id=user_id, message=content)
        return redirect(url_for("main.main_page"))
    if r.exists(user_id):
        r.set("needtest", 1)
        flash("短时间内提交过多，请验证后发表")
        return redirect(url_for("main.main_page"))
    else:
        pipe = r.pipeline(transaction=True)
        r.incr(user_id, 1)
        r.expire(user_id, 5)
        pipe.execute()
    Message.create(user_id=user_id, message=content)
    return redirect(url_for("main.main_page"))


@main.route("/isvalid/")
def isvalid():
    valid = r.exists("needtest")
    return jsonify({"valid": valid})
