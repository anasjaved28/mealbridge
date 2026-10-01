import pytest
from app.models import Listing, User, OPEN, CLAIMED, DISPATCHED, COLLECTED, utc_now
from app.extensions import db, mail
from datetime import timedelta


def test_htmx_feed_polling(client, auth):
    """Verifies HTMX partial rendering vs full page rendering on receiver feed."""
    auth.login("receiver1@test.com", "test1234")

    # 1. Normal GET request -> Full HTML document
    resp_full = client.get("/receiver/feed")
    assert resp_full.status_code == 200
    html_full = resp_full.data.decode("utf-8")
    assert "<!DOCTYPE html>" in html_full
    assert "MealBridge <span class=\"brand-badge\">v1</span>" in html_full
    assert "live-feed-container" in html_full

    # 2. HTMX GET request -> Partial HTML only (no <!DOCTYPE html>, no navbar)
    resp_htmx = client.get("/receiver/feed", headers={"HX-Request": "true"})
    assert resp_htmx.status_code == 200
    html_partial = resp_htmx.data.decode("utf-8")
    assert "<!DOCTYPE html>" not in html_partial
    assert "<nav class=\"navbar\">" not in html_partial
    assert "live-feed-container" in html_partial
    assert 'hx-trigger="every 15s"' in html_partial


def test_pwa_manifest_and_service_worker(client):
    """Verifies PWA manifest and Service Worker endpoints are served at root scope."""
    # 1. Manifest
    resp_manifest = client.get("/manifest.json")
    assert resp_manifest.status_code == 200
    manifest_data = resp_manifest.get_json()
    assert manifest_data["short_name"] == "MealBridge"
    assert manifest_data["display"] == "standalone"
    assert manifest_data["start_url"] == "/"
    assert manifest_data["theme_color"] == "#2563eb"

    # 2. Service Worker
    resp_sw = client.get("/sw.js")
    assert resp_sw.status_code == 200
    assert resp_sw.headers.get("Service-Worker-Allowed") == "/"
    sw_code = resp_sw.data.decode("utf-8")
    assert "CACHE_NAME" in sw_code
    assert "mealbridge-static-v1" in sw_code

    # 3. Base page includes manifest link and theme color
    resp_index = client.get("/")
    assert resp_index.status_code == 200
    index_html = resp_index.data.decode("utf-8")
    assert '<link rel="manifest" href="/manifest.json">' in index_html
    assert '<meta name="theme-color" content="#2563eb">' in index_html


def test_bootstrap_icons_cdn_included(client):
    """Verifies Bootstrap Icons CDN stylesheet is loaded in base template."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert "bootstrap-icons@1.11.3" in resp.data.decode("utf-8")


def test_flask_mail_notifications(client, auth, app):
    """Verifies email notifications are triggered for approvals, claims, dispatch, and collection."""
    with app.app_context():
        with mail.record_messages() as outbox:
            # 1. Test Admin approval notification
            auth.login("admin@test.com", "test1234")
            unapproved = User.query.filter_by(email="pending@test.com").first()
            assert unapproved is not None
            client.post(f"/admin/approve/{unapproved.id}", follow_redirects=True)
            auth.logout()

            assert len(outbox) == 1
            approval_mail = outbox[0]
            assert "pending@test.com" in approval_mail.recipients
            assert "Account Approved" in approval_mail.subject

            # 2. Test Claim notification to Donor
            donor = User.query.filter_by(email="donor@test.com").first()
            listing = Listing(
                food_key="dal_rice",
                food_name="Dal & Rice",
                quantity=30,
                is_veg=True,
                packaging_type="packets",
                address="123 Food Street",
                city="Bengaluru",
                best_before=utc_now() + timedelta(hours=3),
                status=OPEN,
                donor_id=donor.id,
            )
            db.session.add(listing)
            db.session.commit()
            listing_id = listing.id

            auth.login("receiver1@test.com", "test1234")
            client.post(f"/receiver/claim/{listing_id}", follow_redirects=True)
            auth.logout()

            assert len(outbox) == 2
            claim_mail = outbox[1]
            assert "donor@test.com" in claim_mail.recipients
            assert "Was Claimed" in claim_mail.subject

            # Check pickup PIN was sent in the body
            claimed_listing = db.session.get(Listing, listing_id)
            assert claimed_listing.pickup_pin in claim_mail.body

            # 3. Test Dispatch notification to Receiver
            auth.login("donor@test.com", "test1234")
            client.post(
                f"/donor/dispatch/{listing_id}",
                data={"pin": claimed_listing.pickup_pin},
                follow_redirects=True,
            )
            auth.logout()

            assert len(outbox) == 3
            dispatch_mail = outbox[2]
            assert "receiver1@test.com" in dispatch_mail.recipients
            assert "Food Dispatched" in dispatch_mail.subject

            # 4. Test Collection notification to Donor
            auth.login("receiver1@test.com", "test1234")
            client.post(f"/receiver/collect/{listing_id}", follow_redirects=True)
            auth.logout()

            assert len(outbox) == 4
            collect_mail = outbox[3]
            assert "donor@test.com" in collect_mail.recipients
            assert "Donation Completed" in collect_mail.subject
