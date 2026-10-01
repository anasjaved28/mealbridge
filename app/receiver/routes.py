from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import current_user, login_required
from app.extensions import db
from app.models import Listing, User, OPEN, CLAIMED, DISPATCHED, COLLECTED, ROLE_RECEIVER, utc_now
from app.utils import role_required

receiver_bp = Blueprint("receiver", __name__)


@receiver_bp.route("/pending")
@login_required
def pending():
    if current_user.role != ROLE_RECEIVER:
        return redirect(url_for("main.dashboard"))
    if current_user.is_approved:
        return redirect(url_for("receiver.feed"))
    return render_template("receiver/pending.html")


@receiver_bp.route("/feed")
@role_required(ROLE_RECEIVER)
def feed():
    now = utc_now()
    # Receiver sees open listings in their city, newest first, with time left
    listings = (
        Listing.query.filter(
            Listing.city == current_user.city,
            Listing.status == OPEN,
            Listing.best_before > now,
        )
        .order_by(Listing.created_at.desc())
        .all()
    )

    # HTMX polling/partial request: return just the listings container
    if request.headers.get("HX-Request"):
        return render_template(
            "receiver/_feed_listings.html",
            listings=listings,
            viewer_role=ROLE_RECEIVER,
        )

    return render_template(
        "receiver/feed.html",
        listings=listings,
        viewer_role=ROLE_RECEIVER,
    )


@receiver_bp.route("/claim/<int:id>", methods=["POST"])
@role_required(ROLE_RECEIVER)
def claim(id):
    now = utc_now()

    import random
    handover_pin = f"{random.randint(1000, 9999)}"

    # Atomic claim: first to claim wins; checks status, expiry, and matching city in a single DB query
    rows_updated = (
        Listing.query.filter(
            Listing.id == id,
            Listing.status == OPEN,
            Listing.best_before > now,
            Listing.city == current_user.city,
        )
        .update(
            {
                Listing.status: CLAIMED,
                Listing.claimed_by_id: current_user.id,
                Listing.claimed_at: now,
                Listing.pickup_pin: handover_pin,
            },
            synchronize_session=False,
        )
    )
    db.session.commit()

    if rows_updated == 0:
        flash(
            "This food listing was already claimed by another NGO or has expired.",
            "warning",
        )
        return redirect(url_for("receiver.feed"))

    # Send notification email to the donor
    claimed_listing = db.session.get(Listing, id)
    if claimed_listing:
        from app.notifications import notify_donor_listing_claimed
        notify_donor_listing_claimed(claimed_listing)

    flash(
        "Food listing claimed successfully! Please contact the donor using their phone number to coordinate pickup.",
        "success",
    )
    return redirect(url_for("receiver.my_claims"))


@receiver_bp.route("/my-claims")
@role_required(ROLE_RECEIVER)
def my_claims():
    # Retrieve all listings claimed by current receiver, newest first
    listings = (
        Listing.query.filter_by(claimed_by_id=current_user.id)
        .order_by(Listing.claimed_at.desc())
        .all()
    )
    return render_template(
        "receiver/my_claims.html",
        listings=listings,
        viewer_role=ROLE_RECEIVER,
    )


@receiver_bp.route("/collect/<int:id>", methods=["POST"])
@role_required(ROLE_RECEIVER)
def collect(id):
    listing = db.session.get(Listing, id)
    if not listing:
        abort(404)

    # Only the claimer can mark as collected
    if listing.claimed_by_id != current_user.id:
        abort(403)

    # Must be in DISPATCHED state
    if listing.status != DISPATCHED:
        flash(
            "Listing cannot be collected yet. The donor must mark it 'Dispatched' before you can confirm collection.",
            "warning",
        )
        return redirect(url_for("receiver.my_claims"))

    listing.status = COLLECTED
    listing.collected_at = utc_now()
    db.session.commit()

    from app.notifications import notify_donor_food_collected
    notify_donor_food_collected(listing)

    flash(
        f"Thank you! You marked '{listing.food_name}' as Collected. The donation loop is complete!",
        "success",
    )
    return redirect(url_for("receiver.my_claims"))
