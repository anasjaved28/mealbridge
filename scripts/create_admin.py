import sys
import argparse
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db
from app.models import User, ROLE_ADMIN


def create_admin(name, email, password, phone, city):
    app = create_app("development")
    with app.app_context():
        user = User.query.filter_by(email=email.strip().lower()).first()
        if user:
            print(f"User with email '{email}' already exists.")
            if user.role != ROLE_ADMIN:
                user.role = ROLE_ADMIN
                user.is_approved = True
                user.set_password(password)
                db.session.commit()
                print(f"Updated user '{user.name}' to role '{ROLE_ADMIN}'.")
            return

        admin = User(
            name=name.strip(),
            email=email.strip().lower(),
            phone=phone.strip(),
            city=city.strip(),
            role=ROLE_ADMIN,
            is_approved=True,
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Successfully created Admin user: {admin.name} ({admin.email})")


def main():
    parser = argparse.ArgumentParser(description="Create or promote an administrator in MealBridge.")
    parser.add_argument("--name", default="Admin", help="Administrator display name")
    parser.add_argument("--email", default="admin@mealbridge.org", help="Administrator email")
    parser.add_argument("--password", default="test1234", help="Administrator password")
    parser.add_argument("--phone", default="+91 99999 00000", help="Administrator contact phone")
    parser.add_argument("--city", default="Bengaluru", help="City")

    args = parser.parse_args()
    create_admin(args.name, args.email, args.password, args.phone, args.city)


if __name__ == "__main__":
    main()
