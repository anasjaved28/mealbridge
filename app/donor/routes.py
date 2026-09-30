from datetime import timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import current_user
from app.extensions import db
from app.models import Listing, User, OPEN, CLAIMED, DISPATCHED, COLLECTED, ROLE_DONOR, ROLE_ADMIN, utc_now
from app.catalog import FOODS, get_food
from app.donor.forms import ListingForm
from app.utils import role_required

donor_bp = Blueprint("donor", __name__)


@donor_bp.route("/dashboard")
@role_required(ROLE_DONOR)
def dashboard():
    # Retrieve listings created by current donor, newest first
    listings = (
        Listing.query.filter_by(donor_id=current_user.id)
        .order_by(Listing.created_at.desc())
        .all()
    )
    return render_template(
        "donor/dashboard.html",
        listings=listings,
        viewer_role=ROLE_DONOR,
    )


@donor_bp.route("/new", methods=["GET", "POST"])
@role_required(ROLE_DONOR)
def new_listing():
    form = ListingForm()

    # Pre-fill form if re-posting an existing listing
    repost_id = request.args.get("repost_id", type=int)
    if request.method == "GET":
        if repost_id:
            original = db.session.get(Listing, repost_id)
            if original and original.donor_id == current_user.id:
                form.food_key.data = original.food_key
                form.quantity.data = original.quantity
                form.packaging_type.data = original.packaging_type
                form.is_veg.data = original.is_veg
                form.city.data = original.city
                form.address.data = original.address
                flash(
                    f"Details pre-filled from your previous donation of '{original.food_name}'! "
                    "Adjust quantity or best-before time if needed and post.",
                    "info",
                )
        elif current_user.city:
            form.city.data = current_user.city

    if form.validate_on_submit():
        food_meta = get_food(form.food_key.data)
        hours = form.best_before_hours.data
        now = utc_now()
        best_before_dt = now + timedelta(hours=hours)

        listing = Listing(
            food_key=form.food_key.data,
            food_name=food_meta["name"],
            quantity=form.quantity.data,
            packaging_type=form.packaging_type.data,
            is_veg=form.is_veg.data,
            address=form.address.data.strip(),
            city=form.city.data,
            best_before=best_before_dt,
            status=OPEN,
            donor_id=current_user.id,
            created_at=now,
        )
        db.session.add(listing)
        db.session.commit()

        flash(
            f"Successfully posted {listing.quantity} plates of {listing.food_name}! "
            f"Nearby approved NGOs in {listing.city} can now claim it.",
            "success",
        )
        return redirect(url_for("donor.dashboard"))

    return render_template("donor/new_listing.html", form=form, catalog=FOODS)


@donor_bp.route("/dispatch/<int:id>", methods=["POST"])
@role_required(ROLE_DONOR)
def dispatch(id):
    listing = db.session.get(Listing, id)
    if not listing:
        abort(404)

    # Check ownership
    if listing.donor_id != current_user.id:
        abort(403)

    # Can only dispatch if currently CLAIMED
    if listing.status != CLAIMED:
        flash("Only claimed food listings can be marked as Dispatched.", "warning")
        return redirect(url_for("donor.dashboard"))

    # Verify 4-digit pickup PIN if generated for this claim
    entered_pin = request.form.get("pin", "").strip()
    if listing.pickup_pin:
        if not entered_pin or entered_pin != listing.pickup_pin:
            flash(
                "Invalid Handover PIN! Please ask the collecting NGO team for their 4-digit PIN "
                "shown on their MealBridge Claims screen.",
                "danger",
            )
            return redirect(url_for("donor.dashboard"))

    listing.status = DISPATCHED
    listing.dispatched_at = utc_now()
    db.session.commit()

    from app.notifications import notify_receiver_food_dispatched
    notify_receiver_food_dispatched(listing)

    flash(
        f"PIN verified! Marked '{listing.food_name}' as Dispatched! The receiver can now confirm collection upon receipt.",
        "success",
    )
    return redirect(url_for("donor.dashboard"))


@donor_bp.route("/receipt/<int:id>")
@role_required(ROLE_DONOR, ROLE_ADMIN)
def receipt(id):
    listing = db.session.get(Listing, id)
    if not listing:
        abort(404)

    # Only donor owner or admin can view receipt
    if current_user.role == ROLE_DONOR and listing.donor_id != current_user.id:
        abort(403)

    if listing.status != COLLECTED:
        flash(
            "An official donation receipt is generated once the meal is successfully marked Collected.",
            "warning",
        )
        return redirect(url_for("donor.dashboard"))

    return render_template("donor/receipt.html", listing=listing)
