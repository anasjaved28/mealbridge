from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

# Status Constants
OPEN = "OPEN"
CLAIMED = "CLAIMED"
DISPATCHED = "DISPATCHED"
COLLECTED = "COLLECTED"
EXPIRED = "EXPIRED"

VALID_STATUSES = [OPEN, CLAIMED, DISPATCHED, COLLECTED, EXPIRED]
ROLE_DONOR = "donor"
ROLE_RECEIVER = "receiver"
ROLE_ADMIN = "admin"
ROLES = [ROLE_DONOR, ROLE_RECEIVER, ROLE_ADMIN]


def utc_now():
    """Return timezone-naive UTC datetime for consistent database storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(50), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default=ROLE_DONOR)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    # Relationships
    donated_listings = db.relationship(
        "Listing",
        back_populates="donor",
        foreign_keys="Listing.donor_id",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    claimed_listings = db.relationship(
        "Listing",
        back_populates="claimed_by",
        foreign_keys="Listing.claimed_by_id",
        lazy="dynamic",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Default is_approved: True for donors and admins, False for receivers
        if "is_approved" not in kwargs:
            if self.role in [ROLE_DONOR, ROLE_ADMIN]:
                self.is_approved = True
            else:
                self.is_approved = False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_donor(self):
        return self.role == ROLE_DONOR

    @property
    def is_receiver(self):
        return self.role == ROLE_RECEIVER

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)
    food_key = db.Column(db.String(50), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # in plates
    is_veg = db.Column(db.Boolean, nullable=False, default=True)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50), nullable=False, index=True)
    best_before = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=OPEN, index=True)
    packaging_type = db.Column(db.String(50), nullable=False, default="packets")
    pickup_pin = db.Column(db.String(4), nullable=True)

    donor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    claimed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    claimed_at = db.Column(db.DateTime, nullable=True)
    dispatched_at = db.Column(db.DateTime, nullable=True)
    collected_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    donor = db.relationship("User", foreign_keys=[donor_id], back_populates="donated_listings")
    claimed_by = db.relationship("User", foreign_keys=[claimed_by_id], back_populates="claimed_listings")

    @property
    def is_open(self):
        return self.status == OPEN

    @property
    def is_claimed(self):
        return self.status == CLAIMED

    @property
    def is_dispatched(self):
        return self.status == DISPATCHED

    @property
    def is_collected(self):
        return self.status == COLLECTED

    @property
    def has_expired(self):
        return utc_now() >= self.best_before

    def __repr__(self):
        return f"<Listing {self.id}: {self.food_name} ({self.quantity} plates) - {self.status}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
