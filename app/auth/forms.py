from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User, ROLE_DONOR, ROLE_RECEIVER
from app.catalog import CITIES


class SignupForm(FlaskForm):
    name = StringField(
        "Full Name or Organization Name",
        validators=[DataRequired(), Length(min=2, max=120)],
        render_kw={"placeholder": "e.g., Sunshine Restaurant or Robin Hood Army"},
    )
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={"placeholder": "contact@organization.org"},
    )
    phone = StringField(
        "Phone Number",
        validators=[DataRequired(), Length(min=7, max=20)],
        render_kw={"placeholder": "+91 98765 43210"},
    )
    city = SelectField(
        "City",
        validators=[DataRequired()],
        choices=[(city, city) for city in CITIES],
    )
    role = SelectField(
        "I am registering as",
        validators=[DataRequired()],
        choices=[
            (ROLE_DONOR, "Food Donor (Restaurant, Mess, Caterer, Event Host)"),
            (ROLE_RECEIVER, "Food Receiver (NGO, Shelter, Community Kitchen)"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6, message="Password must be at least 6 characters.")],
        render_kw={"placeholder": "••••••••"},
    )
    password_confirm = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "••••••••"},
    )
    submit = SubmitField("Create Account")

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data.strip().lower()).first()
        if user:
            raise ValidationError("This email is already registered. Please log in.")


class LoginForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "you@domain.com"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "••••••••"},
    )
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")
