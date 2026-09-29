from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models import ROLE_DONOR, ROLE_RECEIVER, ROLE_ADMIN

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main_bp.route("/dashboard")
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if current_user.role == ROLE_DONOR:
        return redirect(url_for("donor.dashboard"))
    elif current_user.role == ROLE_RECEIVER:
        if current_user.is_approved:
            return redirect(url_for("receiver.feed"))
        return redirect(url_for("receiver.pending"))
    elif current_user.role == ROLE_ADMIN:
        return redirect(url_for("admin.receivers"))

    return redirect(url_for("main.index"))
