from datetime import timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import current_user
from app.extensions import db
from app.models import Listing, User, OPEN, CLAIMED, DISPATCHED, ROLE_DONOR, utc_now
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

    # Pre-select donor's city on initial GET
    if request.method == "GET" and current_user.city:
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

    listing.status = DISPATCHED
    listing.dispatched_at = utc_now()
    db.session.commit()

    flash(
        f"Marked '{listing.food_name}' as Dispatched! The receiver can now mark it Collected once picked up.",
        "success",
    )
    return redirect(url_for("donor.dashboard"))
