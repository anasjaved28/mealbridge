# MealBridge v1 🍲

> **A simple food rescue website where donors post surplus cooked food, and verified nearby NGOs claim and pick it up.**

The whole product is a single loop:
$$\textbf{Post} \longrightarrow \textbf{See} \longrightarrow \textbf{Claim} \longrightarrow \textbf{Collect}$$

---

## 🚀 Key Features

1. **User Roles**:
   - **Donor**: Restaurants, caterers, hostel messes, or event hosts with surplus food.
   - **Receiver (NGO)**: Shelters, charities, and community kitchens. Requires manual admin approval before claiming meals.
   - **Admin**: Verifies and approves NGOs to maintain food safety and prevent abuse.
2. **Zero-Upload Food Catalog**:
   - Donors select from **20 predefined cooked food meals** (Biryani, Dal & Rice, Roti & Sabzi, Khichdi, etc.).
   - Pre-packaged stock illustrations ensure instant posting and clean presentation with no image upload overhead.
   - Auto-filled dietary tags (Veg / Non-Veg) with donor overrides.
3. **Atomic First-to-Claim Engine**:
   - Live city-filtered open feed for NGOs.
   - Atomic database update ensures the first NGO to claim wins the meal and eliminates race conditions.
4. **Full Pickup Coordination Loop**:
   - Claiming unlocks contact info (donor address, phone number).
   - Donor marks food **Dispatched** upon handover.
   - Receiver marks food **Collected** upon receipt to close the loop.
5. **Auto-Expiry**:
   - Listings past their "best before" time disappear automatically from the open feed.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.13 + Flask 3
- **ORM & Database**: Flask-SQLAlchemy 3 + SQLite (Production-ready for PostgreSQL via `DATABASE_URL`)
- **Authentication**: Flask-Login + Werkzeug Security (Scrypt password hashing)
- **Forms & CSRF**: Flask-WTF + WTForms + email-validator
- **Database Migrations**: Flask-Migrate (Alembic)
- **Styling & UI**: Mobile-first responsive CSS + Vanilla JS countdown ticker
- **Testing**: Pytest (13 automated test suites)

---

## 📁 Project Structure

```text
mealBridge/
├── config.py                        # App configurations (Dev, Testing, Prod)
├── run.py                           # App entry point
├── requirements.txt                 # Pinned dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore definitions
│
├── app/                             # Core Application
│   ├── __init__.py                  # App factory & blueprint registrations
│   ├── extensions.py                # db, login_manager, migrate, csrf
│   ├── models.py                    # User & Listing models + status constants
│   ├── catalog.py                   # 20 predefined meals, cities, and time choices
│   ├── utils.py                     # @role_required, time_left filter
│   │
│   ├── main/                        # Public index & role-based dashboard router
│   ├── auth/                        # Signup, Login, and Logout
│   ├── donor/                       # Donor dashboard, new listing form, dispatch action
│   ├── receiver/                    # Receiver feed, atomic claim, my claims, collect action
│   └── admin/                       # NGO approval and verification management
│
├── static/                          # Static Assets
│   ├── css/style.css                # Mobile-responsive design & cards
│   ├── js/countdown.js              # Real-time ticking time-left counter
│   └── img/food/                    # 20 Predefined food SVGs + default.svg
│
├── templates/                       # Jinja2 Layout & Views
│   ├── base.html                    # Layout shell with role-aware navbar
│   ├── index.html                   # Platform introduction
│   ├── partials/                    # listing_card.html, status_badge.html
│   ├── auth/                        # login.html, signup.html
│   ├── donor/                       # dashboard.html, new_listing.html
│   ├── receiver/                    # feed.html, pending.html, my_claims.html
│   ├── admin/                       # receivers.html
│   └── errors/                      # 403.html, 404.html, 500.html
│
├── scripts/                         # CLI & Automation Tools
│   ├── seed_dev.py                  # Database seeder with demo accounts & listings
│   ├── create_admin.py              # CLI tool to create/promote admin accounts
│   ├── cleanup_expired.py           # Background task to mark expired listings
│   └── generate_food_svgs.py        # Generates clean vector food illustrations
│
└── tests/                           # Pytest Test Suite
    ├── conftest.py                  # Pytest fixtures and mock client
    ├── test_auth.py                 # Auth and role access tests
    ├── test_listings.py             # Food posting and dispatch tests
    └── test_claim_flow.py           # Atomic claiming and full loop tests
```

---

## ⚡ Quickstart Setup

### 1. Set Up Environment & Install Dependencies

```bash
# Clone or open the project folder
cd mealBridge

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Seed Demo Data

Run the development seed script to initialize the database with 6 accounts across all roles and 8 realistic listings across all statuses:

```bash
python scripts/seed_dev.py
```

### 3. Run Development Server

```bash
python run.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser.

---

## 👥 Demo Accounts (Seeded)

All accounts are created with password: **`test1234`**

| Role | Email | City | Note |
|---|---|---|---|
| **Admin** | `admin@mealbridge.org` | Bengaluru | Full access to approve/reject NGO registrations |
| **Donor 1** | `donor1@restaurant.com` | Bengaluru | Restaurant donor with active listings |
| **Donor 2** | `donor2@caterer.com` | Mumbai | Mess/Caterer donor with active listings |
| **Receiver 1** | `ngo1@shelter.org` | Bengaluru | **Approved** NGO ready to claim meals in Bengaluru |
| **Receiver 2** | `ngo2@kitchen.org` | Mumbai | **Approved** NGO ready to claim meals in Mumbai |
| **Receiver 3** | `ngo3@newfoundation.org` | Bengaluru | **Pending** NGO awaiting admin review |

---

## 🧪 Running Automated Tests

Run the complete test suite:

```bash
pytest -v
```

All 13 test suites cover:
- Account registration rules (Donors auto-approved, Receivers pending by default).
- Role access restrictions and 403 barriers.
- Admin approval and rejection workflow.
- **Atomic race condition**: First NGO to claim wins, secondary claims gracefully rejected.
- City matching (NGOs only claim meals within their designated city).
- State transitions (`OPEN` $\rightarrow$ `CLAIMED` $\rightarrow$ `DISPATCHED` $\rightarrow$ `COLLECTED`).
