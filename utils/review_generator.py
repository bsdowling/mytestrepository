"""
Server-side review generator — no external API calls.

Produces 1 long (150-220 words) and 2 concise (60-90 words) review variants
from client input + prefilled context.
"""

import random
import textwrap


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pick(options):
    """Return a random choice from a list."""
    return random.choice(options)


def _cap(s):
    """Capitalize the first letter without lowercasing the rest."""
    if not s:
        return s
    return s[0].upper() + s[1:]


def _transaction_verb(tx_type):
    """Return past-tense verb for transaction type."""
    if tx_type and tx_type.lower().startswith("sell"):
        return "sold"
    return "bought"


def _transaction_gerund(tx_type):
    if tx_type and tx_type.lower().startswith("sell"):
        return "selling"
    return "buying"


def _transaction_noun(tx_type):
    if tx_type and tx_type.lower().startswith("sell"):
        return "sell"
    return "buy"


# ---------------------------------------------------------------------------
# Sentence pools (variety across variants)
# ---------------------------------------------------------------------------

_HOOK_TEMPLATES = [
    "We just {verb} our home in {location} with {agent}, and the whole experience was outstanding.",
    "After {gerund} in {location} with {agent}, we can honestly say it was one of the smoothest real-estate transactions we've been through.",
    "Working with {agent} to {noun} our place in {location} was a genuinely great experience from start to finish.",
    "{agent} helped us {noun} in {location}, and we couldn't be happier with how everything turned out.",
    "Our {gerund} journey in {location} with {agent} was better than we ever expected.",
]

_BRIDGE_TEMPLATES = [
    "From our very first conversation, {agent} made the process feel straightforward and stress-free.",
    "{agent} was incredibly communicative throughout the entire process.",
    "What really set {agent} apart was how responsive and knowledgeable they were at every step.",
    "Right from the start, {agent} took the time to understand exactly what we needed.",
    "{agent} brought a level of professionalism and care that made all the difference.",
]

_STRENGTH_TEMPLATES = [
    "Their knowledge of the {location} market gave us real confidence in every decision.",
    "They kept us informed at every turn, breaking down complex details into simple next steps.",
    "Whenever a question came up — day or evening — we got a thoughtful, timely response.",
    "They navigated the negotiation process with skill and always had our best interests in mind.",
    "Their attention to detail meant nothing fell through the cracks, even on a tight timeline.",
    "We appreciated how they combined deep local expertise with genuine care for our goals.",
]

_RESULT_TEMPLATES = [
    "The closing went smoothly, and we felt confident throughout.",
    "Everything came together on time and without any last-minute surprises.",
    "We closed with confidence, knowing every detail had been handled.",
    "The entire transaction moved at a comfortable pace, and we never felt rushed or in the dark.",
    "In the end, the process was far less stressful than we had anticipated.",
]

_RECOMMENDATION_BUY_SELL = [
    "We'd absolutely recommend {agent} to anyone {gerund} in {market}.",
    "If you're looking to {noun} in {market}, {agent} is the person to call.",
    "We've already recommended {agent} to friends and family — that's how confident we are.",
    "For anyone {gerund} in the {market} area, {agent} is hands-down the best choice.",
    "We wouldn't hesitate to work with {agent} again or recommend them to anyone in {market}.",
]

_CLOSING_EXTRAS = [
    "Five stars all the way!",
    "Truly a five-star experience.",
    "We're so grateful for everything.",
    "Thank you, {agent}, for making this so easy!",
    "Highly recommended.",
    "",
]

_DETAIL_SENTENCES = [
    "We never felt like just another transaction — {agent} genuinely cared about finding the right fit for our family.",
    "Even after the offer was accepted, {agent} stayed on top of inspections, appraisals, and every deadline in between.",
    "What impressed us most was how {agent} turned what could have been an overwhelming process into something we actually enjoyed.",
    "Friends who've been through similar transactions were surprised at how smooth ours went, and we give {agent} full credit for that.",
    "From the initial consultation to the final walkthrough, {agent} was thorough, transparent, and always one step ahead.",
    "They explained each document and each step so clearly that we always knew exactly where we stood.",
    "Looking back, we realize how many potential headaches {agent} quietly handled before they ever reached us.",
    "We were especially grateful for their patience in answering every single question we had, no matter how small.",
]


# ---------------------------------------------------------------------------
# Blending the client's Q1 answer
# ---------------------------------------------------------------------------

_Q1_BLEND = [
    "Specifically, {q1_lower}",
    "For us, what really stood out: {q1_lower}",
    "One thing that made a real impression — {q1_lower}",
    "In particular, {q1_lower}",
    "What we'll remember most is that {q1_lower}",
]


def _blend_q1(q1_raw):
    """Wrap the client's standout sentence naturally."""
    q1 = q1_raw.strip().rstrip(".")
    # If the sentence already starts with a capital and reads like a full
    # thought, use a blending template; otherwise use it directly.
    template = _pick(_Q1_BLEND)
    return template.format(q1_lower=q1[0].lower() + q1[1:] if q1 else q1) + "."


# ---------------------------------------------------------------------------
# Property mention helper
# ---------------------------------------------------------------------------

def _property_mention(property_nickname, closed_month_year):
    parts = []
    if property_nickname:
        parts.append(f"our {property_nickname} property")
    if closed_month_year:
        parts.append(f"closing in {closed_month_year}")
    if parts:
        return " (" + ", ".join(parts) + ")"
    return ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_review(inputs, context, profile, tone="Warm"):
    """
    Generate 3 review variants.

    Parameters
    ----------
    inputs : dict
        q1 : str          — client's standout sentence (required)
        rating : int|None  — 1-5 star rating (optional)
    context : dict
        transaction_type : str
        city : str
        neighborhood : str
        property_nickname : str
        closed_month_year : str
    profile : dict
        agent_name : str
        brokerage : str
        market_city : str

    Returns
    -------
    list[dict]  — [{"label": str, "text": str, "word_count": int}, ...]
    """
    agent = profile.get("agent_name", "our agent")
    market = profile.get("market_city", "") or context.get("city", "the area")
    city = context.get("city", "") or market
    neighborhood = context.get("neighborhood", "")
    location = f"{neighborhood}, {city}" if neighborhood else city
    tx = context.get("transaction_type", "Buy")
    prop_note = _property_mention(
        context.get("property_nickname", ""),
        context.get("closed_month_year", ""),
    )
    q1 = inputs.get("q1", "")
    rating = inputs.get("rating")

    verb = _transaction_verb(tx)
    gerund = _transaction_gerund(tx)
    noun = _transaction_noun(tx)

    fmt = dict(
        agent=agent, location=location, market=market,
        verb=verb, gerund=gerund, noun=noun,
    )

    def _build(target_min, target_max, seed_offset=0):
        """Assemble a single variant aiming for target word range."""
        rng = random.Random(hash(q1) + seed_offset)

        def pick(pool):
            return rng.choice(pool).format(**fmt)

        sentences = []

        # 1. Hook
        hook = pick(_HOOK_TEMPLATES)
        if prop_note:
            hook = hook.rstrip(".") + prop_note + "."
        sentences.append(hook)

        # 2. Bridge
        sentences.append(pick(_BRIDGE_TEMPLATES))

        # 3. Q1 blend
        if q1:
            sentences.append(_blend_q1(q1))

        # 4. Strengths (add 1-3 depending on target length)
        shuffled_strengths = list(_STRENGTH_TEMPLATES)
        rng.shuffle(shuffled_strengths)
        strength_count = 3 if target_max > 120 else 1
        for s in shuffled_strengths[:strength_count]:
            sentences.append(s.format(**fmt))

        # 4b. Detail sentences (long variant only)
        if target_max > 120:
            shuffled_details = list(_DETAIL_SENTENCES)
            rng.shuffle(shuffled_details)
            for s in shuffled_details[:2]:
                sentences.append(s.format(**fmt))

        # 5. Result
        sentences.append(pick(_RESULT_TEMPLATES))

        # 6. Recommendation
        sentences.append(pick(_RECOMMENDATION_BUY_SELL))

        # 7. Closing extra (long variant only)
        if target_max > 120:
            extra = pick(_CLOSING_EXTRAS)
            if extra:
                sentences.append(extra.format(**fmt))

        # Rating mention for long variant
        if rating and int(rating) >= 4 and target_max > 120:
            sentences.insert(-1, f"A solid {rating}-star experience from beginning to end.")

        text = " ".join(sentences)
        wc = len(text.split())

        # Trim if over max: drop last non-essential sentence before recommendation
        while wc > target_max and len(sentences) > 4:
            sentences.pop(-3)
            text = " ".join(sentences)
            wc = len(text.split())

        return text, wc

    long_text, long_wc = _build(150, 220, seed_offset=0)
    concise1_text, c1_wc = _build(60, 90, seed_offset=42)
    concise2_text, c2_wc = _build(60, 90, seed_offset=99)

    return [
        {"label": "Detailed Review", "text": long_text, "word_count": long_wc},
        {"label": "Concise Review A", "text": concise1_text, "word_count": c1_wc},
        {"label": "Concise Review B", "text": concise2_text, "word_count": c2_wc},
    ]
