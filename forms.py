from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, PasswordField,
    BooleanField, IntegerField, HiddenField,
)
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class ReviewForm(FlaskForm):
    """Client-facing review form (One-Minute Mode)."""
    q1 = TextAreaField(
        "What stood out?",
        validators=[DataRequired(), Length(min=5, max=500)],
        render_kw={
            "placeholder": "e.g., 'She explained every step and negotiated repairs we didn't expect.'",
            "rows": 3,
        },
    )
    rating = IntegerField(
        "Overall rating",
        validators=[Optional(), NumberRange(min=1, max=5)],
        default=5,
    )
    consent = BooleanField(
        "I'm OK with this being used in marketing.",
        default=True,
    )
    # honeypot
    website = HiddenField(validators=[Optional()])


class FallbackContextForm(FlaskForm):
    """Fallback mode — gather minimal context when no token."""
    transaction_type = HiddenField(validators=[DataRequired()])
    city = StringField(
        "City or neighborhood",
        validators=[DataRequired(), Length(max=120)],
        render_kw={"placeholder": "e.g., 'Austin' or 'Westlake Hills'"},
    )


class AdminLoginForm(FlaskForm):
    password = PasswordField("Admin Password", validators=[DataRequired()])


class AgentProfileForm(FlaskForm):
    agent_name = StringField("Agent Name", validators=[DataRequired(), Length(max=120)])
    brokerage = StringField("Brokerage", validators=[Optional(), Length(max=200)])
    market_city = StringField("Market City", validators=[Optional(), Length(max=120)])
    brand_color = StringField(
        "Brand Color (hex)",
        validators=[Optional(), Length(max=7)],
        render_kw={"placeholder": "#2563eb"},
    )
    logo_url = StringField("Logo URL", validators=[Optional(), Length(max=500)])
    zillow_url = StringField("Zillow Review Page URL", validators=[Optional(), Length(max=500)])
    google_review_url = StringField(
        "Google Write-a-Review URL",
        validators=[Optional(), Length(max=500)],
    )
    google_place_id = StringField(
        "Google Place ID (alternative)",
        validators=[Optional(), Length(max=200)],
        render_kw={"placeholder": "ChIJ..."},
    )


class CreateLinkForm(FlaskForm):
    transaction_type = SelectField(
        "Transaction Type",
        choices=[("Buy", "Buy"), ("Sell", "Sell")],
        validators=[DataRequired()],
    )
    property_nickname = StringField(
        "Property Nickname",
        validators=[Optional(), Length(max=200)],
        render_kw={"placeholder": "e.g., Oak St. ranch"},
    )
    city = StringField(
        "City",
        validators=[DataRequired(), Length(max=120)],
    )
    neighborhood = StringField(
        "Neighborhood (optional)",
        validators=[Optional(), Length(max=120)],
    )
    closed_month_year = StringField(
        "Closed Month/Year",
        validators=[Optional(), Length(max=40)],
        render_kw={"placeholder": "e.g., July 2025"},
    )
