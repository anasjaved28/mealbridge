from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app.extensions import db
from app.models import User, ROLE_DONOR, ROLE_RECEIVER, ROLE_ADMIN
from app.auth.forms import SignupForm, LoginForm

auth_bp = Blueprint("auth", __name__)


def is_safe_url(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc or not test_url.netloc


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip(),
            city=form.city.data,
            role=form.role.data,
            is_approved=True if form.role.data == ROLE_DONOR else False,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        if user.role == ROLE_RECEIVER:
            flash(
                "Registration successful! Your NGO account has been submitted for admin approval. "
                "You can log in now to check your approval status.",
                "info",
            )
        else:
            flash("Account created successfully! Please log in.", "success")

        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.name}!", "success")

            next_page = request.args.get("next")
            if next_page and is_safe_url(next_page):
                return redirect(next_page)

            # Redirect based on status and role
            if user.role == ROLE_RECEIVER and not user.is_approved:
                return redirect(url_for("receiver.pending"))
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password. Please verify your credentials.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("auth.login"))
