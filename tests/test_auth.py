from app.models import User, ROLE_DONOR, ROLE_RECEIVER, ROLE_ADMIN
from app.extensions import db


def test_signup_donor(client, app):
    response = client.post(
        "/auth/signup",
        data={
            "name": "Fresh Harvest Mess",
            "email": "fresh@harvest.org",
            "phone": "+91 98765 00000",
            "city": "Bengaluru",
            "role": ROLE_DONOR,
            "password": "securepassword",
            "password_confirm": "securepassword",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email="fresh@harvest.org").first()
        assert user is not None
        assert user.role == ROLE_DONOR
        assert user.is_approved is True  # Donors approved by default


def test_signup_receiver_requires_approval(client, app):
    response = client.post(
        "/auth/signup",
        data={
            "name": "Community Food Shelter",
            "email": "shelter@community.org",
            "phone": "+91 98765 11111",
            "city": "Bengaluru",
            "role": ROLE_RECEIVER,
            "password": "securepassword",
            "password_confirm": "securepassword",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email="shelter@community.org").first()
        assert user is not None
        assert user.role == ROLE_RECEIVER
        assert user.is_approved is False  # Receivers start unapproved


def test_login_and_logout(client, auth):
    response = auth.login("donor@test.com", "test1234")
    assert response.status_code == 200
    assert b"Donor Food Dashboard" in response.data or b"Dashboard" in response.data

    logout_resp = auth.logout()
    assert b"logged out" in logout_resp.data


def test_unapproved_receiver_redirected_to_pending(client, auth):
    response = auth.login("pending@test.com", "test1234")
    # Redirects to /receiver/pending
    assert response.status_code == 200
    assert b"Account Awaiting Admin Approval" in response.data or b"Pending" in response.data

    # Attempting to access feed directly should redirect to pending
    feed_resp = client.get("/receiver/feed", follow_redirects=True)
    assert b"Account Awaiting Admin Approval" in feed_resp.data


def test_receiver_cannot_access_admin(client, auth):
    auth.login("receiver1@test.com", "test1234")
    response = client.get("/admin/receivers")
    assert response.status_code == 403


def test_admin_approval_flow(client, auth, app):
    # Log in as admin
    auth.login("admin@test.com", "test1234")
    res = client.get("/admin/receivers")
    assert res.status_code == 200
    assert b"Unapproved Shelter" in res.data

    with app.app_context():
        pending_user = User.query.filter_by(email="pending@test.com").first()
        user_id = pending_user.id
        assert pending_user.is_approved is False

    # Approve receiver
    approve_resp = client.post(f"/admin/approve/{user_id}", follow_redirects=True)
    assert approve_resp.status_code == 200

    with app.app_context():
        updated_user = db.session.get(User, user_id)
        assert updated_user.is_approved is True
