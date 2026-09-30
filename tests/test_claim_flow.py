from datetime import timedelta
from app.models import Listing, User, OPEN, CLAIMED, DISPATCHED, COLLECTED, utc_now
from app.extensions import db


def test_first_claim_wins_atomic(client, auth, app):
    with app.app_context():
        donor = User.query.filter_by(email="donor@test.com").first()
        listing = Listing(
            food_key="biryani",
            food_name="Dum Biryani",
            quantity=50,
            is_veg=False,
            address="Indiranagar 100ft Rd",
            city="Bengaluru",
            best_before=utc_now() + timedelta(hours=3),
            status=OPEN,
            donor_id=donor.id,
        )
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

    # 1. Receiver 1 claims the listing
    auth.login("receiver1@test.com", "test1234")
    res1 = client.post(f"/receiver/claim/{listing_id}", follow_redirects=True)
    assert res1.status_code == 200
    assert b"claimed successfully" in res1.data

    with app.app_context():
        updated = db.session.get(Listing, listing_id)
        assert updated.status == CLAIMED
        receiver1 = User.query.filter_by(email="receiver1@test.com").first()
        assert updated.claimed_by_id == receiver1.id

    # Log out receiver 1
    auth.logout()

    # 2. Receiver 2 attempts to claim the already-claimed listing
    auth.login("receiver2@test.com", "test1234")
    res2 = client.post(f"/receiver/claim/{listing_id}", follow_redirects=True)
    assert res2.status_code == 200
    assert b"already claimed" in res2.data

    # Verify listing is still assigned to Receiver 1
    with app.app_context():
        final_check = db.session.get(Listing, listing_id)
        assert final_check.claimed_by_id == receiver1.id


def test_receiver_cannot_claim_in_different_city(client, auth, app):
    with app.app_context():
        donor = User.query.filter_by(email="donor_mumbai@test.com").first()
        # Listing in Mumbai
        listing = Listing(
            food_key="pav_bhaji",
            food_name="Pav Bhaji",
            quantity=40,
            is_veg=True,
            address="Powai Mess Hall",
            city="Mumbai",
            best_before=utc_now() + timedelta(hours=3),
            status=OPEN,
            donor_id=donor.id,
        )
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

    # receiver1 is based in Bengaluru
    auth.login("receiver1@test.com", "test1234")
    res = client.post(f"/receiver/claim/{listing_id}", follow_redirects=True)
    # Claim rejected due to city mismatch
    assert b"already claimed by another NGO or has expired" in res.data

    with app.app_context():
        check = db.session.get(Listing, listing_id)
        assert check.status == OPEN
        assert check.claimed_by_id is None


def test_receiver_cannot_claim_expired_listing(client, auth, app):
    with app.app_context():
        donor = User.query.filter_by(email="donor@test.com").first()
        # Expired listing in Bengaluru
        listing = Listing(
            food_key="roti_curry",
            food_name="Roti & Sabzi",
            quantity=20,
            is_veg=True,
            address="Koramangala",
            city="Bengaluru",
            best_before=utc_now() - timedelta(minutes=10),  # In the past
            status=OPEN,
            donor_id=donor.id,
        )
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

    auth.login("receiver1@test.com", "test1234")
    res = client.post(f"/receiver/claim/{listing_id}", follow_redirects=True)
    assert b"already claimed by another NGO or has expired" in res.data

    with app.app_context():
        check = db.session.get(Listing, listing_id)
        assert check.status == OPEN
        assert check.claimed_by_id is None


def test_complete_loop_post_see_claim_dispatch_collect(client, auth, app):
    # Step 1: Donor posts
    auth.login("donor@test.com", "test1234")
    post_res = client.post(
        "/donor/new",
        data={
            "food_key": "paneer_curry",
            "quantity": 30,
            "is_veg": "y",
            "city": "Bengaluru",
            "best_before_hours": 3,
            "address": "Banquet Hall, MG Road",
        },
        follow_redirects=True,
    )
    assert post_res.status_code == 200
    auth.logout()

    with app.app_context():
        listing = Listing.query.filter_by(address="Banquet Hall, MG Road").first()
        listing_id = listing.id
        assert listing.status == OPEN

    # Step 2: Receiver sees in feed
    auth.login("receiver1@test.com", "test1234")
    feed_res = client.get("/receiver/feed")
    assert b"Paneer Masala" in feed_res.data

    # Step 3: Receiver claims
    claim_res = client.post(f"/receiver/claim/{listing_id}", follow_redirects=True)
    assert b"claimed successfully" in claim_res.data
    auth.logout()

    # Step 3.5: Receiver tries to collect BEFORE donor dispatches (should fail)
    auth.login("receiver1@test.com", "test1234")
    premature_collect = client.post(f"/receiver/collect/{listing_id}", follow_redirects=True)
    assert b"cannot be collected yet" in premature_collect.data or b"Dispatched" in premature_collect.data
    auth.logout()

    with app.app_context():
        current_listing = db.session.get(Listing, listing_id)
        pin = current_listing.pickup_pin
        assert pin is not None
        assert len(pin) == 4

    # Step 4: Donor dispatches with verified PIN
    auth.login("donor@test.com", "test1234")
    dispatch_res = client.post(f"/donor/dispatch/{listing_id}", data={"pin": pin}, follow_redirects=True)
    assert b"Dispatched" in dispatch_res.data
    auth.logout()

    # Step 5: Receiver confirms collected -> closes the loop
    auth.login("receiver1@test.com", "test1234")
    collect_res = client.post(f"/receiver/collect/{listing_id}", follow_redirects=True)
    assert b"Collected" in collect_res.data

    with app.app_context():
        finished_listing = db.session.get(Listing, listing_id)
        assert finished_listing.status == COLLECTED
        assert finished_listing.dispatched_at is not None
        assert finished_listing.collected_at is not None
