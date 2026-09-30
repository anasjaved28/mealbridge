from datetime import timedelta
from app.models import Listing, User, OPEN, CLAIMED, DISPATCHED, COLLECTED, utc_now
from app.utils import clean_phone
from app.extensions import db


def test_clean_phone_sanitization():
    assert clean_phone("+91 98888 11111") == "919888811111"
    assert clean_phone("080-1234-5678") == "08012345678"
    assert clean_phone("(+91) 98765-43210") == "919876543210"
    assert clean_phone("") == ""
    assert clean_phone(None) == ""


def test_homepage_impact_counter(client, app):
    with app.app_context():
        donor = User.query.filter_by(email="donor@test.com").first()
        receiver = User.query.filter_by(email="receiver1@test.com").first()

        # Add a collected listing with 60 plates
        listing = Listing(
            food_key="biryani",
            food_name="Dum Biryani",
            quantity=60,
            is_veg=False,
            address="100ft Road",
            city="Bengaluru",
            best_before=utc_now() + timedelta(hours=2),
            status=COLLECTED,
            donor_id=donor.id,
            claimed_by_id=receiver.id,
            collected_at=utc_now(),
        )
        db.session.add(listing)
        db.session.commit()

    response = client.get("/")
    assert response.status_code == 200
    assert b"Plates of Food Rescued" in response.data
    assert b"Completed Food Pickups" in response.data
    assert b"Verified NGO Partners" in response.data
    assert b"Active Donors & Messes" in response.data
    # 60 plates should be reflected
    assert b"60" in response.data


def test_whatsapp_and_maps_links_on_claimed_card(client, auth, app):
    with app.app_context():
        donor = User.query.filter_by(email="donor@test.com").first()
        receiver = User.query.filter_by(email="receiver1@test.com").first()

        listing = Listing(
            food_key="dal_rice",
            food_name="Dal & Rice",
            quantity=25,
            is_veg=True,
            address="MG Road Food Street",
            city="Bengaluru",
            best_before=utc_now() + timedelta(hours=3),
            status=CLAIMED,
            donor_id=donor.id,
            claimed_by_id=receiver.id,
            claimed_at=utc_now(),
        )
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

    # 1. Receiver views "My Claims" -> sees WhatsApp button & Google Maps link
    auth.login("receiver1@test.com", "test1234")
    my_claims_res = client.get("/receiver/my-claims")
    assert my_claims_res.status_code == 200
    assert b"wa.me" in my_claims_res.data
    assert b"google.com/maps/search" in my_claims_res.data
    assert b"Open in Maps" in my_claims_res.data
    auth.logout()

    # 2. Donor views "Dashboard" -> sees NGO contact with WhatsApp button
    auth.login("donor@test.com", "test1234")
    donor_res = client.get("/donor/dashboard")
    assert donor_res.status_code == 200
    assert b"wa.me" in donor_res.data
    assert b"WhatsApp" in donor_res.data
