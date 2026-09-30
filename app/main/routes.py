from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.extensions import db
from app.models import Listing, User, ROLE_DONOR, ROLE_RECEIVER, ROLE_ADMIN, COLLECTED

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    # Live platform impact metrics
    total_meals_rescued = (
        db.session.query(db.func.sum(Listing.quantity))
        .filter(Listing.status == COLLECTED)
        .scalar()
        or 0
    )
    total_completed_pickups = Listing.query.filter_by(status=COLLECTED).count()
    total_verified_ngos = User.query.filter_by(role=ROLE_RECEIVER, is_approved=True).count()
    total_active_donors = User.query.filter_by(role=ROLE_DONOR).count()

    return render_template(
        "index.html",
        total_meals_rescued=total_meals_rescued,
        total_completed_pickups=total_completed_pickups,
        total_verified_ngos=total_verified_ngos,
        total_active_donors=total_active_donors,
    )


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
