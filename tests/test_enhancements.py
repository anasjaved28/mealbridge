from datetime import timedelta
from app.models import Listing, User, OPEN, CLAIMED, DISPATCHED, COLLECTED, utc_now
from app.extensions import db


def test_handover_pin_workflow(client, auth, app):
    with app.app_context():
        donor = User.query.filter_by(email="donor@test.com").first()
        listing = Listing(
            food_key="biryani",
            food_name="Dum Biryani",
            quantity=40,
            is_veg=False,
            address="Koramangala 80ft Rd",
            city="Bengaluru",
            best_before=utc_now() + timedelta(hours=3),
            status=OPEN,
            donor_id=donor.id,
        )
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

    # 1. Receiver claims -> generates 4-digit PIN
    auth.login("receiver1@test.com", "test1234")
    claim_res = client.post(f"/receiver/claim/{listing_id}", follow_redirects=True)
    assert claim_res.status_code == 200

    with app.app_context():
        claimed_listing = db.session.get(Listing, listing_id)
        pin = claimed_listing.pickup_pin
        assert pin is not None
        assert len(pin) == 4
        assert pin.isdigit()

    # Receiver views claims page and sees the PIN displayed
    claims_page = client.get("/receiver/my-claims")
    assert pin.encode() in claims_page.data
    assert b"HANDOVER PIN" in claims_page.data
    auth.logout()

    # 2. Donor attempts dispatch with an INCORRECT PIN -> rejected
    auth.login("donor@test.com", "test1234")
    wrong_dispatch = client.post(
        f"/donor/dispatch/{listing_id}",
        data={"pin": "0000" if pin != "0000" else "9999"},
        follow_redirects=True,
    )
    assert b"Invalid Handover PIN" in wrong_dispatch.data

    with app.app_context():
        check_listing = db.session.get(Listing, listing_id)
        assert check_listing.status == CLAIMED  # Did not dispatch

    # 3. Donor enters the CORRECT PIN -> successfully dispatched
    correct_dispatch = client.post(
        f"/donor/dispatch/{listing_id}",
        data={"pin": pin},
        follow_redirects=True,
    )
    assert b"PIN verified" in correct_dispatch.data

    with app.app_context():
        check_dispatched = db.session.get(Listing, listing_id)
        assert check_dispatched.status == DISPATCHED


def test_packaging_type_selection(client, auth, app):
    auth.login("donor@test.com", "test1234")

    # Post with "vessels" packaging
    response = client.post(
        "/donor/new",
        data={
            "food_key": "khichdi",
            "quantity": 30,
            "packaging_type": "vessels",
            "is_veg": "y",
            "city": "Bengaluru",
            "best_before_hours": 3,
            "address": "Kitchen Gate 2, Indiranagar",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    auth.logout()

    with app.app_context():
        listing = Listing.query.filter_by(address="Kitchen Gate 2, Indiranagar").first()
        assert listing is not None
        assert listing.packaging_type == "vessels"

    # Receiver opens feed and sees the packaging label
    auth.login("receiver1@test.com", "test1234")
    feed_res = client.get("/receiver/feed")
    assert b"Large Vessels" in feed_res.data


def test_repost_prefills_form(client, auth, app):
    with app.app_context():
        donor = User.query.filter_by(email="donor@test.com").first()
        old_listing = Listing(
            food_key="pav_bhaji",
            food_name="Pav Bhaji",
            quantity=50,
            packaging_type="trays",
            is_veg=True,
            address="Old Airport Road, Mess 1",
            city="Bengaluru",
            best_before=utc_now() - timedelta(hours=2),
            status=COLLECTED,
            donor_id=donor.id,
        )
        db.session.add(old_listing)
        db.session.commit()
        old_id = old_listing.id

    auth.login("donor@test.com", "test1234")
    repost_page = client.get(f"/donor/new?repost_id={old_id}")
    assert repost_page.status_code == 200
    assert b"Details pre-filled from your previous donation" in repost_page.data
    assert b"Old Airport Road, Mess 1" in repost_page.data


def test_donation_receipt_access(client, auth, app):
    with app.app_context():
        donor = User.query.filter_by(email="donor@test.com").first()
        other_donor = User.query.filter_by(email="donor_mumbai@test.com").first()
        receiver = User.query.filter_by(email="receiver1@test.com").first()

        collected_listing = Listing(
            food_key="dal_rice",
            food_name="Dal & Rice",
            quantity=75,
            packaging_type="packets",
            is_veg=True,
            address="Residency Road",
            city="Bengaluru",
            best_before=utc_now() + timedelta(hours=2),
            status=COLLECTED,
            donor_id=donor.id,
            claimed_by_id=receiver.id,
            collected_at=utc_now(),
        )
        uncollected_listing = Listing(
            food_key="biryani",
            food_name="Dum Biryani",
            quantity=40,
            packaging_type="packets",
            is_veg=False,
            address="Residency Road",
            city="Bengaluru",
            best_before=utc_now() + timedelta(hours=2),
            status=OPEN,
            donor_id=donor.id,
        )
        db.session.add_all([collected_listing, uncollected_listing])
        db.session.commit()
        collected_id = collected_listing.id
        uncollected_id = uncollected_listing.id

    # 1. Owner donor views collected receipt -> 200 OK
    auth.login("donor@test.com", "test1234")
    receipt_res = client.get(f"/donor/receipt/{collected_id}")
    assert receipt_res.status_code == 200
    assert b"Certificate of Food Donation" in receipt_res.data
    assert b"75 Plates" in receipt_res.data
    assert b"Approved NGO 1" in receipt_res.data

    # 2. Owner attempts to view receipt for an UNCOLLECTED meal -> blocked with warning
    uncollected_res = client.get(f"/donor/receipt/{uncollected_id}", follow_redirects=True)
    assert b"An official donation receipt is generated once the meal is successfully marked Collected" in uncollected_res.data
    auth.logout()

    # 3. Other donor attempts to view someone else's receipt -> 403 Forbidden
    auth.login("donor_mumbai@test.com", "test1234")
    forbidden_res = client.get(f"/donor/receipt/{collected_id}")
    assert forbidden_res.status_code == 403
