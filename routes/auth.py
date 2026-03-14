from flask import Blueprint, render_template, redirect, request
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect("/admin" if user.role == "admin" else "/user")
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed = generate_password_hash(request.form["password"])
        user = User(
            username=request.form["username"],
            password=hashed,
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/auth/login")
    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect("/auth/login")
