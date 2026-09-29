import pytest
from app import create_app
from app.extensions import db
from app.models import (
    User,
    Listing,
    ROLE_ADMIN,
    ROLE_DONOR,
    ROLE_RECEIVER,
    OPEN,
    CLAIMED,
    DISPATCHED,
    utc_now,
)
from datetime import timedelta


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, email="donor1@restaurant.com", password="test1234"):
        return self._client.post(
            "/auth/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    def logout(self):
        return self._client.get("/auth/logout", follow_redirects=True)


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        # Seed standard test actors
        admin = User(
            name="Admin Tester",
            email="admin@test.com",
            phone="+91 90000 00000",
            city="Bengaluru",
            role=ROLE_ADMIN,
            is_approved=True,
        )
        admin.set_password("test1234")

        donor = User(
            name="Donor Kitchen",
            email="donor@test.com",
            phone="+91 91111 11111",
            city="Bengaluru",
            role=ROLE_DONOR,
            is_approved=True,
        )
        donor.set_password("test1234")

        donor2 = User(
            name="Mumbai Donor",
            email="donor_mumbai@test.com",
            phone="+91 92222 22222",
            city="Mumbai",
            role=ROLE_DONOR,
            is_approved=True,
        )
        donor2.set_password("test1234")

        receiver = User(
            name="Approved NGO 1",
            email="receiver1@test.com",
            phone="+91 93333 33333",
            city="Bengaluru",
            role=ROLE_RECEIVER,
            is_approved=True,
        )
        receiver.set_password("test1234")

        receiver2 = User(
            name="Approved NGO 2",
            email="receiver2@test.com",
            phone="+91 94444 44444",
            city="Bengaluru",
            role=ROLE_RECEIVER,
            is_approved=True,
        )
        receiver2.set_password("test1234")

        unapproved_receiver = User(
            name="Unapproved Shelter",
            email="pending@test.com",
            phone="+91 95555 55555",
            city="Bengaluru",
            role=ROLE_RECEIVER,
            is_approved=False,
        )
        unapproved_receiver.set_password("test1234")

        db.session.add_all([admin, donor, donor2, receiver, receiver2, unapproved_receiver])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth(client):
    return AuthActions(client)
