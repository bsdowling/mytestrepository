"""
One-Minute Review — Flask application.
Mobile-first web app for generating polished real-estate reviews.
"""

import csv
import hashlib
import io
import json
import os
import secrets
import time
from functools import wraps

import bleach
from dotenv import load_dotenv
from flask import (
    Flask, render_template, redirect, url_for, request,
    flash, session, jsonify, Response, abort,
)

from models import db, AgentProfile, ReviewRequest, SubmissionLog
from forms import (
    ReviewForm, FallbackContextForm, AdminLoginForm,
    AgentProfileForm, CreateLinkForm,
)
from utils.review_generator import generate_review

load_dotenv()

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-fallback-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
SALT = os.getenv("SALT", "default-salt")

db.init_app(app)

with app.app_context():
    db.create_all()
    # Ensure at least one agent profile row exists
    if not AgentProfile.query.first():
        db.session.add(AgentProfile(
            agent_name="Britt Dowling",
            market_city="Montgomery, Alabama",
            experience_url="https://www.experience.com/rest/survey/showsurveypage/britt-dowling-montgomery-alabama-realtor",
            google_review_url="https://g.page/r/CWNhy9ZilaoPEAI/review",
        ))
        db.session.commit()

# ---------------------------------------------------------------------------
# Rate-limiting (in-memory per IP)
# ---------------------------------------------------------------------------

_rate_store: dict[str, list[float]] = {}
RATE_LIMIT = 15  # requests per window
RATE_WINDOW = 60  # seconds


def _rate_limited(ip: str) -> bool:
    now = time.time()
    hits = _rate_store.get(ip, [])
    hits = [t for t in hits if now - t < RATE_WINDOW]
    if len(hits) >= RATE_LIMIT:
        return True
    hits.append(now)
    _rate_store[ip] = hits
    return False


def _hash_ip(ip: str) -> str:
    return hashlib.sha256((SALT + ip).encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Sanitize helper
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    return bleach.clean(text or "", strip=True)


# ---------------------------------------------------------------------------
# Admin auth helpers
# ---------------------------------------------------------------------------

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


def _get_profile() -> AgentProfile:
    return AgentProfile.query.first()


# ---------------------------------------------------------------------------
# Routes — Client
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Landing page — check for token or show fallback."""
    token = request.args.get("t")
    if token:
        return redirect(url_for("review_page", token=token))
    return render_template("fallback.html", form=FallbackContextForm())


@app.route("/r/<token>")
def review_page(token):
    """One-Minute Mode — pre-filled context from token."""
    rr = ReviewRequest.query.filter_by(token=token).first_or_404()
    profile = _get_profile()
    form = ReviewForm()
    return render_template(
        "review.html",
        form=form,
        rr=rr,
        profile=profile,
        token=token,
    )


@app.route("/generate", methods=["POST"])
def generate():
    """Generate reviews (AJAX or form POST)."""
    ip = request.remote_addr or "unknown"
    if _rate_limited(ip):
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(error="Too many requests. Please wait a minute."), 429
        flash("Too many requests. Please wait a minute.", "error")
        return redirect(request.referrer or url_for("index"))

    form = ReviewForm()
    if not form.validate_on_submit():
        errors = {field: errs for field, errs in form.errors.items() if field != "csrf_token"}
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(error="Validation failed", details=errors), 400
        flash("Please fix the errors below.", "error")
        return redirect(request.referrer or url_for("index"))

    # Honeypot check
    if form.website.data:
        # Bot detected — silently accept
        return jsonify(variants=[]) if request.is_json else redirect(url_for("index"))

    q1 = _clean(form.q1.data)
    rating = form.rating.data
    consent = form.consent.data

    # Gather context
    token = request.form.get("token", "")
    rr = None
    if token:
        rr = ReviewRequest.query.filter_by(token=token).first()

    if rr:
        context = {
            "transaction_type": rr.transaction_type,
            "city": rr.city,
            "neighborhood": rr.neighborhood or "",
            "property_nickname": rr.property_nickname or "",
            "closed_month_year": rr.closed_month_year or "",
        }
    else:
        context = {
            "transaction_type": _clean(request.form.get("transaction_type", "Buy")),
            "city": _clean(request.form.get("city", "")),
            "neighborhood": "",
            "property_nickname": "",
            "closed_month_year": "",
        }

    profile_obj = _get_profile()
    profile = {
        "agent_name": profile_obj.agent_name,
        "brokerage": profile_obj.brokerage or "",
        "market_city": profile_obj.market_city or "",
    }

    inputs = {"q1": q1, "rating": rating}
    variants = generate_review(inputs, context, profile)

    # Log submission
    log = SubmissionLog(
        token_id=token,
        city=context.get("city", ""),
        transaction_type=context.get("transaction_type", ""),
        word_count=variants[0]["word_count"] if variants else 0,
        overall_rating=rating or 0,
        ip_hash=_hash_ip(ip),
        consent=consent,
    )
    db.session.add(log)
    db.session.commit()

    # Return results
    result = {
        "variants": variants,
        "experience_url": profile_obj.experience_url or "",
        "google_url": profile_obj.get_google_url(),
        "agent_name": profile_obj.agent_name,
    }

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(result)

    # Non-JS fallback: render results page
    return render_template(
        "results.html",
        variants=variants,
        profile=profile_obj,
        token=token,
        context=context,
    )


@app.route("/fallback-generate", methods=["POST"])
def fallback_generate():
    """Handle fallback mode: gather context then show review form."""
    ip = request.remote_addr or "unknown"
    if _rate_limited(ip):
        flash("Too many requests. Please wait a minute.", "error")
        return redirect(url_for("index"))

    form = FallbackContextForm()
    if not form.validate_on_submit():
        flash("Please fill in the required fields.", "error")
        return redirect(url_for("index"))

    profile = _get_profile()
    review_form = ReviewForm()
    return render_template(
        "review.html",
        form=review_form,
        rr=None,
        profile=profile,
        token="",
        fallback_tx=_clean(form.transaction_type.data),
        fallback_city=_clean(form.city.data),
    )


# ---------------------------------------------------------------------------
# Routes — Admin
# ---------------------------------------------------------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.password.data == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid password.", "error")
    return render_template("admin_login.html", form=form)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))


@app.route("/admin/dashboard", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    profile = _get_profile()
    profile_form = AgentProfileForm(obj=profile)
    link_form = CreateLinkForm()
    links = ReviewRequest.query.order_by(ReviewRequest.created_at.desc()).all()
    return render_template(
        "admin.html",
        profile_form=profile_form,
        link_form=link_form,
        profile=profile,
        links=links,
    )


@app.route("/admin/profile", methods=["POST"])
@admin_required
def admin_update_profile():
    profile = _get_profile()
    form = AgentProfileForm()
    if form.validate_on_submit():
        profile.agent_name = _clean(form.agent_name.data)
        profile.brokerage = _clean(form.brokerage.data)
        profile.market_city = _clean(form.market_city.data)
        profile.brand_color = _clean(form.brand_color.data) or "#2563eb"
        profile.logo_url = _clean(form.logo_url.data)
        profile.experience_url = _clean(form.experience_url.data)
        profile.google_review_url = _clean(form.google_review_url.data)
        profile.google_place_id = _clean(form.google_place_id.data)
        db.session.commit()
        flash("Profile updated.", "success")
    else:
        flash("Please fix errors.", "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/create-link", methods=["POST"])
@admin_required
def admin_create_link():
    form = CreateLinkForm()
    if form.validate_on_submit():
        token = secrets.token_urlsafe(6)[:8]
        rr = ReviewRequest(
            token=token,
            transaction_type=_clean(form.transaction_type.data),
            property_nickname=_clean(form.property_nickname.data),
            city=_clean(form.city.data),
            neighborhood=_clean(form.neighborhood.data),
            closed_month_year=_clean(form.closed_month_year.data),
        )
        db.session.add(rr)
        db.session.commit()
        flash(f"Link created: /r/{token}", "success")
    else:
        flash("Please fix errors.", "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/export-csv")
@admin_required
def admin_export_csv():
    logs = SubmissionLog.query.order_by(SubmissionLog.timestamp.desc()).all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow([
        "timestamp", "token_id", "city", "transaction_type",
        "word_count", "overall_rating", "ip_hash", "consent",
    ])
    for log in logs:
        writer.writerow([
            log.timestamp.isoformat() if log.timestamp else "",
            log.token_id, log.city, log.transaction_type,
            log.word_count, log.overall_rating, log.ip_hash, log.consent,
        ])
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=submissions.csv"},
    )


# ---------------------------------------------------------------------------
# Download endpoints
# ---------------------------------------------------------------------------

@app.route("/download-txt", methods=["POST"])
def download_txt():
    text = request.form.get("text", "")
    return Response(
        text,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=review.txt"},
    )


@app.route("/download-json", methods=["POST"])
def download_json():
    data = request.form.get("data", "{}")
    return Response(
        data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=reviews.json"},
    )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
