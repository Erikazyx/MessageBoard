# -*- coding: UTF-8 -*-
from flask import request, render_template, redirect, jsonify, session, flash, url_for
from models import User
from app.auth import auth


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        user = request.form.get("user")
        password = request.form.get("password1")
        if User.select().where(User.username == user):
            return jsonify({"error": "该用户名已被注册！"})
        User.create(username=user, password_hash=password)
        return jsonify({"error": ""})


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        user = request.form.get("username")
        password = request.form.get("password")
        if not user or not password:
            flash("please input username and password!")
            return render_template("login.html")
        user = User.select().where(User.username == user)
        if not user or not user.get().verify_password(password):
            flash("wrong username or wrong password,try again")
            return render_template("login.html")
        else:
            session["user_id"] = user.id
            session.permanent = True
            return redirect(url_for("main.main_page"))


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.main_page"))
