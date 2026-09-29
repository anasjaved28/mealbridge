import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db
from app.models import Listing, OPEN, EXPIRED, utc_now


def cleanup_expired_listings():
    app = create_app("development")
    with app.app_context():
        now = utc_now()
        count = (
            Listing.query.filter(
                Listing.status == OPEN,
                Listing.best_before <= now,
            ).update({Listing.status: EXPIRED}, synchronize_session=False)
        )
        db.session.commit()
        print(f"[{now.isoformat()}] Cleaned up {count} expired OPEN listing(s).")


if __name__ == "__main__":
    cleanup_expired_listings()
