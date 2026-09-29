import os
from pathlib import Path

FOOD_SVGS = {
    "default.svg": {
        "title": "Cooked Meal",
        "bg": "#f8fafc",
        "accent": "#10b981",
        "emoji": "🍲",
        "subtitle": "Prepared Food",
    },
    "biryani.svg": {
        "title": "Dum Biryani",
        "bg": "#fffbeb",
        "accent": "#f59e0b",
        "emoji": "🍚",
        "subtitle": "Spiced Basmati Feast",
    },
    "dal_rice.svg": {
        "title": "Dal & Rice",
        "bg": "#fefce8",
        "accent": "#eab308",
        "emoji": "🍛",
        "subtitle": "Steamed Rice & Yellow Dal",
    },
    "roti_curry.svg": {
        "title": "Roti & Sabzi",
        "bg": "#fff7ed",
        "accent": "#ea580c",
        "emoji": "🫓",
        "subtitle": "Wheat Rotis & Curry",
    },
    "khichdi.svg": {
        "title": "Moong Khichdi",
        "bg": "#f7fee7",
        "accent": "#84cc16",
        "emoji": "🥣",
        "subtitle": "Warm Lentil & Rice",
    },
    "fried_rice.svg": {
        "title": "Fried Rice",
        "bg": "#f0fdf4",
        "accent": "#16a34a",
        "emoji": "🥢",
        "subtitle": "Veggie Stir-fry",
    },
    "paneer_curry.svg": {
        "title": "Paneer Masala",
        "bg": "#fff1f2",
        "accent": "#e11d48",
        "emoji": "🧀",
        "subtitle": "Rich Cottage Cheese Gravy",
    },
    "idli_sambar.svg": {
        "title": "Idli & Sambar",
        "bg": "#f8fafc",
        "accent": "#0284c7",
        "emoji": "⚪",
        "subtitle": "Steamed Rice Cakes",
    },
    "dosa_pack.svg": {
        "title": "Crisp Dosa",
        "bg": "#fffbeb",
        "accent": "#d97706",
        "emoji": "🥞",
        "subtitle": "With Sambar & Chutney",
    },
    "veg_pulao.svg": {
        "title": "Veg Pulao",
        "bg": "#f0fdfa",
        "accent": "#0d9488",
        "emoji": "🥕",
        "subtitle": "Garden Vegetable Rice",
    },
    "chole_bhature.svg": {
        "title": "Chole Bhature",
        "bg": "#fef2f2",
        "accent": "#dc2626",
        "emoji": "🥘",
        "subtitle": "Spiced Chickpea Curry",
    },
    "rajma_chawal.svg": {
        "title": "Rajma Chawal",
        "bg": "#faf5ff",
        "accent": "#9333ea",
        "emoji": "🫘",
        "subtitle": "Red Bean Curry & Rice",
    },
    "hakka_noodles.svg": {
        "title": "Hakka Noodles",
        "bg": "#fefce8",
        "accent": "#ca8a04",
        "emoji": "🍜",
        "subtitle": "Tossed Asian Noodles",
    },
    "pav_bhaji.svg": {
        "title": "Pav Bhaji",
        "bg": "#fff7ed",
        "accent": "#c2410c",
        "emoji": "🍞",
        "subtitle": "Mashed Spiced Veg & Buns",
    },
    "sambar_rice.svg": {
        "title": "Sambar Rice",
        "bg": "#fffbeb",
        "accent": "#b45309",
        "emoji": "🍲",
        "subtitle": "Lentil Tamarind Rice",
    },
    "mix_veg_sabzi.svg": {
        "title": "Mix Veg Curry",
        "bg": "#f0fdf4",
        "accent": "#15803d",
        "emoji": "🥗",
        "subtitle": "Seasonal Veggie Delight",
    },
    "poori_bhaji.svg": {
        "title": "Poori Bhaji",
        "bg": "#fff7ed",
        "accent": "#d97706",
        "emoji": "🟡",
        "subtitle": "Puffed Pooris & Aloo",
    },
    "samosa_snack.svg": {
        "title": "Samosa & Snacks",
        "bg": "#fffbeb",
        "accent": "#d97706",
        "emoji": "🥟",
        "subtitle": "Golden Crisp Savories",
    },
    "sandwich_meal.svg": {
        "title": "Club Sandwiches",
        "bg": "#f8fafc",
        "accent": "#2563eb",
        "emoji": "🥪",
        "subtitle": "Fresh Sandwich Platter",
    },
    "sweets_mithai.svg": {
        "title": "Mithai & Halwa",
        "bg": "#fdf4ff",
        "accent": "#c026d3",
        "emoji": "🍬",
        "subtitle": "Fresh Festive Desserts",
    },
    "egg_curry_rice.svg": {
        "title": "Egg Curry & Rice",
        "bg": "#fef2f2",
        "accent": "#b91c1c",
        "emoji": "🥚",
        "subtitle": "Savory Egg Gravy with Rice",
    },
}

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 250" width="100%" height="100%">
  <defs>
    <linearGradient id="grad-{name}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg}" />
      <stop offset="100%" stop-color="#ffffff" />
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#grad-{name})" />
  <circle cx="200" cy="95" r="55" fill="#ffffff" stroke="{accent}" stroke-width="3" stroke-dasharray="4 2" />
  <circle cx="200" cy="95" r="48" fill="{bg}" />
  <text x="200" y="112" font-size="44" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto">{emoji}</text>
  <text x="200" y="178" font-size="18" font-weight="700" text-anchor="middle" fill="#1e293b" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto">{title}</text>
  <text x="200" y="202" font-size="12" font-weight="500" text-anchor="middle" fill="#64748b" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto">{subtitle}</text>
  <rect x="160" y="215" width="80" height="4" rx="2" fill="{accent}" />
</svg>"""


def main():
    dest_dir = Path(__file__).resolve().parent.parent / "app" / "static" / "img" / "food"
    # Also check static/img/food relative to root
    dest_dir_root = Path(__file__).resolve().parent.parent / "static" / "img" / "food"

    for d in [dest_dir, dest_dir_root]:
        d.mkdir(parents=True, exist_ok=True)
        for filename, data in FOOD_SVGS.items():
            content = SVG_TEMPLATE.format(
                name=filename.replace(".svg", ""),
                bg=data["bg"],
                accent=data["accent"],
                emoji=data["emoji"],
                title=data["title"],
                subtitle=data["subtitle"],
            )
            filepath = d / filename
            filepath.write_text(content, encoding="utf-8")
            print(f"Generated {filepath}")


if __name__ == "__main__":
    main()
