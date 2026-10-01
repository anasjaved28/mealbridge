from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from app.catalog import FOODS, CITIES, QUANTITY_CHOICES, BEST_BEFORE_CHOICES, PACKAGING_CHOICES


class ListingForm(FlaskForm):
    food_key = SelectField(
        "Select Food Item",
        validators=[DataRequired()],
        choices=[(f["key"], f"{f['name']} ({'Veg' if f['is_veg'] else 'Non-Veg'})") for f in FOODS],
    )
    quantity = SelectField(
        "Estimated Quantity (Plates)",
        validators=[DataRequired()],
        coerce=int,
        choices=QUANTITY_CHOICES,
        validate_choice=False,
    )
    packaging_type = SelectField(
        "Packaging Type (Container / Packets)",
        validators=[DataRequired()],
        choices=PACKAGING_CHOICES,
        default="packets",
    )
    is_veg = BooleanField(
        "Vegetarian Meal",
        default=True,
    )
    city = SelectField(
        "Pickup City",
        validators=[DataRequired()],
        choices=[(city, city) for city in CITIES],
    )
    best_before_hours = SelectField(
        "Best Before / Consume Within",
        validators=[DataRequired()],
        coerce=int,
        choices=BEST_BEFORE_CHOICES,
    )
    address = TextAreaField(
        "Precise Pickup Address & Landmark",
        validators=[DataRequired(), Length(min=10, max=255)],
        render_kw={
            "rows": 3,
            "placeholder": "e.g., Sunshine Restaurant Back Gate, MG Road, opposite Metro Pillar 42, Bengaluru",
        },
    )
    submit = SubmitField("Post Food Listing")
