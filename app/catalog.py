from flask import url_for

# 20 Predefined cooked food items
FOODS = [
    {
        "key": "biryani",
        "name": "Dum Biryani",
        "image": "biryani.svg",
        "is_veg": False,
        "description": "Fragrant basmati rice cooked with spices and herbs.",
    },
    {
        "key": "dal_rice",
        "name": "Dal & Steamed Rice",
        "image": "dal_rice.svg",
        "is_veg": True,
        "description": "Comforting yellow dal paired with freshly steamed basmati rice.",
    },
    {
        "key": "roti_curry",
        "name": "Roti & Sabzi Thali",
        "image": "roti_curry.svg",
        "is_veg": True,
        "description": "Fresh whole wheat rotis served with seasonal vegetable curry.",
    },
    {
        "key": "khichdi",
        "name": "Moong Dal Khichdi",
        "image": "khichdi.svg",
        "is_veg": True,
        "description": "Nutritious, warm, and wholesome lentil and rice pot.",
    },
    {
        "key": "fried_rice",
        "name": "Vegetable Fried Rice",
        "image": "fried_rice.svg",
        "is_veg": True,
        "description": "Wok-tossed rice with chopped garden vegetables and light seasoning.",
    },
    {
        "key": "paneer_curry",
        "name": "Paneer Masala & Roti",
        "image": "paneer_curry.svg",
        "is_veg": True,
        "description": "Rich paneer curry in spiced tomato gravy with rotis.",
    },
    {
        "key": "idli_sambar",
        "name": "Idli & Sambar",
        "image": "idli_sambar.svg",
        "is_veg": True,
        "description": "Steamed fluffy rice cakes with hot vegetable lentil stew.",
    },
    {
        "key": "dosa_pack",
        "name": "Crispy Dosa Platter",
        "image": "dosa_pack.svg",
        "is_veg": True,
        "description": "Cooked dosa servings with coconut chutney and sambar.",
    },
    {
        "key": "veg_pulao",
        "name": "Vegetable Pulao",
        "image": "veg_pulao.svg",
        "is_veg": True,
        "description": "Aromatic spiced rice cooked with green peas, carrots, and spices.",
    },
    {
        "key": "chole_bhature",
        "name": "Chole & Bhature",
        "image": "chole_bhature.svg",
        "is_veg": True,
        "description": "Tangy chickpea curry served with golden fried bhature.",
    },
    {
        "key": "rajma_chawal",
        "name": "Rajma Chawal",
        "image": "rajma_chawal.svg",
        "is_veg": True,
        "description": "North Indian red kidney bean curry with steamed white rice.",
    },
    {
        "key": "hakka_noodles",
        "name": "Vegetable Hakka Noodles",
        "image": "hakka_noodles.svg",
        "is_veg": True,
        "description": "Stir-fried noodles loaded with shredded cabbage, bell pepper, and carrots.",
    },
    {
        "key": "pav_bhaji",
        "name": "Pav Bhaji",
        "image": "pav_bhaji.svg",
        "is_veg": True,
        "description": "Buttery mashed spiced vegetables with toasted soft bread rolls.",
    },
    {
        "key": "sambar_rice",
        "name": "South Indian Sambar Rice",
        "image": "sambar_rice.svg",
        "is_veg": True,
        "description": "Tangy tamarind and lentil rice tempered with mustard seeds and curry leaves.",
    },
    {
        "key": "mix_veg_sabzi",
        "name": "Mixed Vegetable Curry",
        "image": "mix_veg_sabzi.svg",
        "is_veg": True,
        "description": "Dry or homestyle gravy mixed vegetable prep.",
    },
    {
        "key": "poori_bhaji",
        "name": "Poori & Aloo Sabzi",
        "image": "poori_bhaji.svg",
        "is_veg": True,
        "description": "Puffed whole wheat pooris with spiced potato curry.",
    },
    {
        "key": "samosa_snack",
        "name": "Samosa & Savory Snacks",
        "image": "samosa_snack.svg",
        "is_veg": True,
        "description": "Crisp golden samosas and savory party snacks.",
    },
    {
        "key": "sandwich_meal",
        "name": "Club Sandwiches",
        "image": "sandwich_meal.svg",
        "is_veg": True,
        "description": "Freshly prepared vegetable and cheese club sandwiches.",
    },
    {
        "key": "sweets_mithai",
        "name": "Assorted Halwa / Mithai",
        "image": "sweets_mithai.svg",
        "is_veg": True,
        "description": "Freshly prepared festival sweets, halwa, or dessert boxes.",
    },
    {
        "key": "egg_curry_rice",
        "name": "Egg Curry & Rice",
        "image": "egg_curry_rice.svg",
        "is_veg": False,
        "description": "Hard-boiled eggs simmered in onion-tomato gravy with rice.",
    },
]

FOODS_BY_KEY = {food["key"]: food for food in FOODS}


def get_food(key):
    """Retrieve food metadata by key, returning a fallback if not found."""
    return FOODS_BY_KEY.get(
        key,
        {
            "key": "default",
            "name": "Cooked Meal",
            "image": "default.svg",
            "is_veg": True,
            "description": "Nutritious cooked food ready for pickup.",
        },
    )


CITIES = [
    "Bengaluru",
    "Mumbai",
    "Delhi NCR",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Lucknow",
    "Chandigarh",
    "Indore",
    "Kochi",
    "Bhopal",
    "Patna",
]

QUANTITY_CHOICES = [
    (10, "10 plates (serves ~10)"),
    (20, "20 plates (serves ~20)"),
    (25, "25 plates (serves ~25)"),
    (30, "30 plates (serves ~30)"),
    (40, "40 plates (serves ~40)"),
    (50, "50 plates (serves ~50)"),
    (75, "75 plates (serves ~75)"),
    (100, "100 plates (serves ~100)"),
    (150, "150 plates (large gathering)"),
    (200, "200 plates (event/caterer)"),
    (300, "300+ plates (bulk)"),
]

BEST_BEFORE_CHOICES = [
    (2, "2 hours (consume soon)"),
    (3, "3 hours"),
    (4, "4 hours (recommended)"),
    (6, "6 hours"),
    (8, "8 hours"),
    (12, "12 hours (properly kept)"),
    (24, "24 hours (refrigerated)"),
]

PACKAGING_PACKETS = "packets"
PACKAGING_VESSELS = "vessels"
PACKAGING_TRAYS = "trays"

PACKAGING_CHOICES = [
    (PACKAGING_PACKETS, "Individual Packets / Foil Boxes (ready to hand out)"),
    (PACKAGING_VESSELS, "Large Catering Vessels (bring own containers)"),
    (PACKAGING_TRAYS, "Disposable Trays"),
]

PACKAGING_LABELS = {
    "packets": "📦 Packets / Foil Boxes",
    "vessels": "🍲 Large Vessels (Bring Containers)",
    "trays": "🍱 Disposable Trays",
}


def get_packaging_label(key):
    return PACKAGING_LABELS.get(key, "📦 Meal Packets")


def food_image(key):
    """Jinja helper returning the static asset URL for a food image."""
    food = get_food(key)
    image_filename = food.get("image", "default.svg")
    return url_for("static", filename=f"img/food/{image_filename}")
