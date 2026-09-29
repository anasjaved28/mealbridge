from datetime import timedelta
from app.models import Listing, User, OPEN, CLAIMED, DISPATCHED, utc_now
from app.extensions import db


def test_donor_can_post_listing(client, auth, app):
    auth.login("donor@test.com", "test1234")

    response = client.post(
        "/donor/new",
        data={
            "food_key": "biryani",
            "quantity": 50,
            "is_veg": "y",
            "city": "Bengaluru",
            "best_before_hours": 4,
            "address": "Gate 1, Tech Park Food Court, Bengaluru",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Successfully posted" in response.data or b"Dum Biryani" in response.data

    with app.app_context():
        listing = Listing.query.filter_by(address="Gate 1, Tech Park Food Court, Bengaluru").first()
        assert listing is not None
        assert listing.food_key == "biryani"
        assert listing.food_name == "Dum Biryani"
        assert listing.quantity == 50
        assert listing.status == OPEN
        assert listing.best_before > utc_now()


def test_donor_cannot_dispatch_other_donor_listing(client, auth, app):
    with app.app_context():
        donor1 = User.query.filter_by(email="donor@test.com").first()
        donor2 = User.query.filter_by(email="donor_mumbai@test.com").first()
        receiver = User.query.filter_by(email="receiver1@test.com").first()

        # Listing owned by donor2
        listing = Listing(
            food_key="dal_rice",
            food_name="Dal & Rice",
            quantity=30,
            is_veg=True,
            address="123 Mumbai Street",
            city="Mumbai",
            best_before=utc_now() + timedelta(hours=3),
            status=CLAIMED,
            donor_id=donor2.id,
            claimed_by_id=receiver.id,
        )
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

    # Log in as donor1 and attempt to dispatch donor2's listing
    auth.login("donor@test.com", "test1234")
    response = client.post(f"/donor/dispatch/{listing_id}")
    assert response.status_code == 403


def test_dispatch_only_allowed_when_claimed(client, auth, app):
    with app.app_context():
        donor = User.query.filter_by(email="donor@test.com").first()
        # Listing in OPEN status (not claimed yet)
        listing = Listing(
            food_key="khichdi",
            food_name="Moong Dal Khichdi",
            quantity=20,
            is_veg=True,
            address="Koramangala 4th Block",
            city="Bengaluru",
            best_before=utc_now() + timedelta(hours=3),
            status=OPEN,
            donor_id=donor.id,
        )
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

    auth.login("donor@test.com", "test1234")
    response = client.post(f"/donor/dispatch/{listing_id}", follow_redirects=True)
    assert b"Only claimed" in response.data

    with app.app_context():
        checked = db.session.get(Listing, listing_id)
        assert checked.status == OPEN  # Did not transition
