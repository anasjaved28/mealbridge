import sys
from pathlib import Path
from datetime import timedelta

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
    COLLECTED,
    EXPIRED,
    utc_now,
)
from app.catalog import get_food


def seed_database():
    app = create_app("development")

    with app.app_context():
        print("Resetting database...")
        db.drop_all()
        db.create_all()

        print("Seeding Users...")
        # 1 Admin
        admin = User(
            name="Platform Administrator",
            email="admin@mealbridge.org",
            phone="+91 99999 00000",
            city="Bengaluru",
            role=ROLE_ADMIN,
            is_approved=True,
        )
        admin.set_password("test1234")
        db.session.add(admin)

        # 2 Donors
        donor1 = User(
            name="Grand Royal Palace Caterers",
            email="donor1@restaurant.com",
            phone="+91 98888 11111",
            city="Bengaluru",
            role=ROLE_DONOR,
            is_approved=True,
        )
        donor1.set_password("test1234")
        db.session.add(donor1)

        donor2 = User(
            name="Campus Central Mess",
            email="donor2@caterer.com",
            phone="+91 98888 22222",
            city="Mumbai",
            role=ROLE_DONOR,
            is_approved=True,
        )
        donor2.set_password("test1234")
        db.session.add(donor2)

        # 2 Approved Receivers
        receiver1 = User(
            name="Robin Hood Care Foundation",
            email="ngo1@shelter.org",
            phone="+91 97777 11111",
            city="Bengaluru",
            role=ROLE_RECEIVER,
            is_approved=True,
        )
        receiver1.set_password("test1234")
        db.session.add(receiver1)

        receiver2 = User(
            name="Hope Community Kitchen",
            email="ngo2@kitchen.org",
            phone="+91 97777 22222",
            city="Mumbai",
            role=ROLE_RECEIVER,
            is_approved=True,
        )
        receiver2.set_password("test1234")
        db.session.add(receiver2)

        # 1 Unapproved Receiver
        receiver3 = User(
            name="Rising Star Youth Shelter",
            email="ngo3@newfoundation.org",
            phone="+91 97777 33333",
            city="Bengaluru",
            role=ROLE_RECEIVER,
            is_approved=False,
        )
        receiver3.set_password("test1234")
        db.session.add(receiver3)

        db.session.commit()
        print("Users seeded successfully.")

        print("Seeding Listings...")
        now = utc_now()

        # 8 Listings across cities and statuses
        listings_data = [
            # 1: Open in Bengaluru
            {
                "food_key": "biryani",
                "quantity": 50,
                "is_veg": False,
                "address": "Gate 3, Royal Palace Banquet, Indiranagar",
                "city": "Bengaluru",
                "best_before": now + timedelta(hours=4),
                "status": OPEN,
                "donor_id": donor1.id,
                "claimed_by_id": None,
                "created_at": now - timedelta(minutes=30),
            },
            # 2: Open in Bengaluru
            {
                "food_key": "dal_rice",
                "quantity": 30,
                "is_veg": True,
                "address": "Kitchen Annex, Koramangala 4th Block",
                "city": "Bengaluru",
                "best_before": now + timedelta(hours=3),
                "status": OPEN,
                "donor_id": donor1.id,
                "claimed_by_id": None,
                "created_at": now - timedelta(minutes=45),
            },
            # 3: Claimed in Bengaluru (Awaiting Dispatch)
            {
                "food_key": "paneer_curry",
                "quantity": 40,
                "is_veg": True,
                "address": "Indiranagar 100ft Road, near Metro",
                "city": "Bengaluru",
                "best_before": now + timedelta(hours=2),
                "status": CLAIMED,
                "donor_id": donor1.id,
                "claimed_by_id": receiver1.id,
                "created_at": now - timedelta(hours=1),
                "claimed_at": now - timedelta(minutes=20),
            },
            # 4: Dispatched in Bengaluru (Awaiting Collection)
            {
                "food_key": "khichdi",
                "quantity": 25,
                "is_veg": True,
                "address": "Indiranagar 100ft Road, near Metro",
                "city": "Bengaluru",
                "best_before": now + timedelta(hours=2),
                "status": DISPATCHED,
                "donor_id": donor1.id,
                "claimed_by_id": receiver1.id,
                "created_at": now - timedelta(hours=2),
                "claimed_at": now - timedelta(hours=1),
                "dispatched_at": now - timedelta(minutes=10),
            },
            # 5: Collected in Bengaluru (Completed loop)
            {
                "food_key": "veg_pulao",
                "quantity": 75,
                "is_veg": True,
                "address": "Indiranagar 100ft Road, near Metro",
                "city": "Bengaluru",
                "best_before": now + timedelta(hours=5),
                "status": COLLECTED,
                "donor_id": donor1.id,
                "claimed_by_id": receiver1.id,
                "created_at": now - timedelta(hours=5),
                "claimed_at": now - timedelta(hours=4),
                "dispatched_at": now - timedelta(hours=3),
                "collected_at": now - timedelta(hours=2),
            },
            # 6: Open in Mumbai
            {
                "food_key": "pav_bhaji",
                "quantity": 100,
                "is_veg": True,
                "address": "Mess Hall 4, Powai Campus",
                "city": "Mumbai",
                "best_before": now + timedelta(hours=6),
                "status": OPEN,
                "donor_id": donor2.id,
                "claimed_by_id": None,
                "created_at": now - timedelta(minutes=15),
            },
            # 7: Claimed in Mumbai
            {
                "food_key": "chole_bhature",
                "quantity": 50,
                "is_veg": True,
                "address": "Hostel 2 Dining Wing, Powai",
                "city": "Mumbai",
                "best_before": now + timedelta(hours=3),
                "status": CLAIMED,
                "donor_id": donor2.id,
                "claimed_by_id": receiver2.id,
                "created_at": now - timedelta(hours=1),
                "claimed_at": now - timedelta(minutes=30),
            },
            # 8: Expired listing in Bengaluru
            {
                "food_key": "sandwich_meal",
                "quantity": 20,
                "is_veg": True,
                "address": "Cafeteria Gate B, Electronic City",
                "city": "Bengaluru",
                "best_before": now - timedelta(hours=1),  # In the past
                "status": EXPIRED,
                "donor_id": donor1.id,
                "claimed_by_id": None,
                "created_at": now - timedelta(hours=6),
            },
        ]

        for item in listings_data:
            food_info = get_food(item["food_key"])
            listing = Listing(
                food_key=item["food_key"],
                food_name=food_info["name"],
                quantity=item["quantity"],
                is_veg=item["is_veg"],
                address=item["address"],
                city=item["city"],
                best_before=item["best_before"],
                status=item["status"],
                donor_id=item["donor_id"],
                claimed_by_id=item["claimed_by_id"],
                created_at=item["created_at"],
                claimed_at=item.get("claimed_at"),
                dispatched_at=item.get("dispatched_at"),
                collected_at=item.get("collected_at"),
            )
            db.session.add(listing)

        db.session.commit()
        print("8 listings seeded across Open, Claimed, Dispatched, Collected, and Expired states.")
        print("\nAll accounts password: 'test1234'")
        print("  - Admin:    admin@mealbridge.org")
        print("  - Donor 1:  donor1@restaurant.com (Bengaluru)")
        print("  - Donor 2:  donor2@caterer.com (Mumbai)")
        print("  - Receiver: ngo1@shelter.org (Approved, Bengaluru)")
        print("  - Receiver: ngo2@kitchen.org (Approved, Mumbai)")
        print("  - Receiver: ngo3@newfoundation.org (Unapproved, Bengaluru)")


if __name__ == "__main__":
    seed_database()
