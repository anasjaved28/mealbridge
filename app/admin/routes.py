from flask import Blueprint, render_template, redirect, url_for, flash, abort
from app.extensions import db
from app.models import User, ROLE_RECEIVER, ROLE_ADMIN
from app.utils import role_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/receivers")
@role_required(ROLE_ADMIN)
def receivers():
    pending_receivers = (
        User.query.filter_by(role=ROLE_RECEIVER, is_approved=False)
        .order_by(User.created_at.desc())
        .all()
    )
    approved_receivers = (
        User.query.filter_by(role=ROLE_RECEIVER, is_approved=True)
        .order_by(User.created_at.desc())
        .limit(30)
        .all()
    )
    return render_template(
        "admin/receivers.html",
        pending_receivers=pending_receivers,
        approved_receivers=approved_receivers,
    )


@admin_bp.route("/approve/<int:id>", methods=["POST"])
@role_required(ROLE_ADMIN)
def approve(id):
    user = db.session.get(User, id)
    if not user:
        abort(404)

    if user.role != ROLE_RECEIVER:
        flash("Only receiver/NGO accounts require verification approval.", "warning")
        return redirect(url_for("admin.receivers"))

    user.is_approved = True
    db.session.commit()

    flash(f"Receiver '{user.name}' ({user.email}) has been approved successfully.", "success")
    return redirect(url_for("admin.receivers"))


@admin_bp.route("/reject/<int:id>", methods=["POST"])
@role_required(ROLE_ADMIN)
def reject(id):
    user = db.session.get(User, id)
    if not user:
        abort(404)

    if user.role != ROLE_RECEIVER:
        flash("Only receiver/NGO accounts can be rejected.", "warning")
        return redirect(url_for("admin.receivers"))

    user_name = user.name
    db.session.delete(user)
    db.session.commit()

    flash(f"Receiver account for '{user_name}' has been rejected and removed.", "info")
    return redirect(url_for("admin.receivers"))
