from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class AgentProfile(db.Model):
    __tablename__ = "agent_profile"
    id = db.Column(db.Integer, primary_key=True)
    agent_name = db.Column(db.String(120), nullable=False, default="")
    brokerage = db.Column(db.String(200), default="")
    market_city = db.Column(db.String(120), default="")
    brand_color = db.Column(db.String(7), default="#2563eb")  # hex
    logo_url = db.Column(db.String(500), default="")
    zillow_url = db.Column(db.String(500), default="")
    google_review_url = db.Column(db.String(500), default="")
    google_place_id = db.Column(db.String(200), default="")

    def get_google_url(self):
        if self.google_review_url:
            return self.google_review_url
        if self.google_place_id:
            return f"https://search.google.com/local/writereview?placeid={self.google_place_id}"
        return ""


class ReviewRequest(db.Model):
    __tablename__ = "review_request"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(16), unique=True, nullable=False, index=True)
    transaction_type = db.Column(db.String(10), nullable=False)  # Buy or Sell
    property_nickname = db.Column(db.String(200), default="")
    city = db.Column(db.String(120), nullable=False)
    neighborhood = db.Column(db.String(120), default="")
    closed_month_year = db.Column(db.String(40), default="")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )


class SubmissionLog(db.Model):
    __tablename__ = "submission_log"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    token_id = db.Column(db.String(16), default="")
    city = db.Column(db.String(120), default="")
    transaction_type = db.Column(db.String(10), default="")
    word_count = db.Column(db.Integer, default=0)
    overall_rating = db.Column(db.Integer, default=0)
    ip_hash = db.Column(db.String(64), default="")
    consent = db.Column(db.Boolean, default=True)
