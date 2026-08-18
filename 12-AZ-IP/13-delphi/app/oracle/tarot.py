"""
DelPhi — Tarot Oracle Engine
φ²-weighted Celtic Cross, Three-Card, and Single-Card readings.
Adapted from apps/tarot-oracle/oracle.py.
"""
from __future__ import annotations

import hashlib
from datetime import date as _date_cls
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# Manifold constants
# ---------------------------------------------------------------------------
PHI0 = 1.6180339887448950   # golden ratio — FTUM radion fixed point
ALPHA = 1.0 / PHI0 ** 2    # α = φ₀⁻²  ≈ 0.38197

# ---------------------------------------------------------------------------
# Deck
# ---------------------------------------------------------------------------
MAJOR_ARCANA: list[str] = [
    "The Fool", "The Magician", "The High Priestess", "The Empress",
    "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
    "Strength", "The Hermit", "Wheel of Fortune", "Justice",
    "The Hanged Man", "Death", "Temperance", "The Devil",
    "The Tower", "The Star", "The Moon", "The Sun",
    "Judgement", "The World",
]

MINOR_ARCANA: list[str] = []
for _suit in ("Wands", "Cups", "Swords", "Pentacles"):
    MINOR_ARCANA += [f"Ace of {_suit}"]
    MINOR_ARCANA += [f"{n} of {_suit}" for n in range(2, 11)]
    MINOR_ARCANA += [
        f"Page of {_suit}", f"Knight of {_suit}",
        f"Queen of {_suit}", f"King of {_suit}",
    ]

DECK: list[str] = MAJOR_ARCANA + MINOR_ARCANA  # 22 + 56 = 78

assert len(DECK) == 78
assert len(MAJOR_ARCANA) == 22
assert len(MINOR_ARCANA) == 56

# ---------------------------------------------------------------------------
# Spread positions
# ---------------------------------------------------------------------------
CELTIC_CROSS_POSITIONS = [
    {"number": 1, "name": "Present", "subtitle": "The Situation — Ψ_n",
     "manifold": "The current state of the information field."},
    {"number": 2, "name": "Challenge", "subtitle": "What Crosses — ∇_μ J^μ_inf = 0",
     "manifold": "The conservation constraint — tension that must be resolved."},
    {"number": 3, "name": "Root", "subtitle": "Foundation — T operator",
     "manifold": "The topological substrate — the winding number."},
    {"number": 4, "name": "Past", "subtitle": "What Passes — I operator",
     "manifold": "Information absorbed permanently into the record."},
    {"number": 5, "name": "Crown", "subtitle": "What May Be — H operator",
     "manifold": "The higher-dimensional projection."},
    {"number": 6, "name": "Future", "subtitle": "What Comes — Ψ_{n+1}",
     "manifold": "The next FTUM step — the attractor basin."},
    {"number": 7, "name": "Self", "subtitle": "Your Attitude — φ₀",
     "manifold": "The seeker as mediating field."},
    {"number": 8, "name": "Environment", "subtitle": "External Influences — KK spectrum",
     "manifold": "The Kaluza-Klein modes surrounding you."},
    {"number": 9, "name": "Hopes & Fears", "subtitle": "The Geodesic Arc",
     "manifold": "Tension between desired attractor and feared repeller."},
    {"number": 10, "name": "Outcome", "subtitle": "Fixed Point — U·Ψ_n = Ψ_{n+1}",
     "manifold": "The convergence point of the U-operator."},
]

THREE_CARD_POSITIONS = [
    {"number": 1, "name": "Past", "subtitle": "What was", "manifold": "The prior state of the field."},
    {"number": 2, "name": "Present", "subtitle": "What is", "manifold": "The current field state Ψ_n."},
    {"number": 3, "name": "Future", "subtitle": "What will be", "manifold": "The next attractor Ψ_{n+1}."},
]

SINGLE_CARD_POSITIONS = [
    {"number": 1, "name": "Oracle", "subtitle": "The Message", "manifold": "The field speaks."},
]

# ---------------------------------------------------------------------------
# Card metadata
# ---------------------------------------------------------------------------
CARD_KEYWORDS: dict[str, str] = {
    "The Fool": "new beginnings, open potential, leap of faith",
    "The Magician": "will, mastery, manifesting intent into form",
    "The High Priestess": "intuition, hidden knowledge, the unseen current",
    "The Empress": "abundance, fertility, creative generation",
    "The Emperor": "authority, structure, ordered power",
    "The Hierophant": "institution, transmission of wisdom, legitimate influence",
    "The Lovers": "alignment, meaningful choice, union of opposites",
    "The Chariot": "directed will, momentum, victory through discipline",
    "Strength": "inner courage, patience, grace under pressure",
    "The Hermit": "inner guidance, solitude, the lantern carried alone",
    "Wheel of Fortune": "turning point, cyclic force, fate meeting readiness",
    "Justice": "balance, accountability, clear-eyed consequence",
    "The Hanged Man": "suspension, willing sacrifice, the view from a new angle",
    "Death": "transformation, necessary ending, passage to next form",
    "Temperance": "integration, flow, the middle path held steady",
    "The Devil": "binding, shadow, the pattern that traps by attachment",
    "The Tower": "sudden revelation, disruption that clears the false structure",
    "The Star": "hope restored, guidance after storm, faith in the signal",
    "The Moon": "the unconscious, uncertain navigation, what stirs beneath",
    "The Sun": "clarity, vitality, full expression in the open field",
    "Judgement": "reckoning, awakening call, answering to the larger arc",
    "The World": "completion, full-cycle integration, the fixed point reached",
}

SUIT_KEYWORDS: dict[str, str] = {
    "Wands": "fire, will, creative drive",
    "Cups": "water, feeling, relational depth",
    "Swords": "air, mind, clarity and conflict",
    "Pentacles": "earth, body, material form",
}

RANK_KEYWORDS: dict[str, str] = {
    "Ace": "pure potential, seed form",
    "2": "balance, duality, choice",
    "3": "initial growth, collaboration",
    "4": "stability, consolidation",
    "5": "disruption, challenge, conflict",
    "6": "harmony, flow, generosity",
    "7": "assessment, perseverance, inner work",
    "8": "movement, efficiency, acceleration",
    "9": "near-completion, integration, solitude",
    "10": "fullness, culmination, the end of a cycle",
    "Page": "beginner mind, message, curiosity",
    "Knight": "directed motion, quest, the moving field",
    "Queen": "mature receptivity, mastery of the inner realm",
    "King": "authority, mastery of the outer realm",
}

MAJOR_ARCANA_DETAILS: dict[str, dict] = {
    "The Fool": {"number": 0, "element": "Air", "upright": "New beginnings, innocence, adventure, idealism", "reversed": "Recklessness, naivety, foolishness, risk"},
    "The Magician": {"number": 1, "element": "Air", "upright": "Willpower, manifestation, skill, resourcefulness", "reversed": "Manipulation, poor planning, untapped talents"},
    "The High Priestess": {"number": 2, "element": "Water", "upright": "Intuition, sacred knowledge, divine feminine", "reversed": "Secrets, disconnection from intuition, withdrawal"},
    "The Empress": {"number": 3, "element": "Earth", "upright": "Femininity, beauty, nature, nurturing, abundance", "reversed": "Creative block, dependence, smothering"},
    "The Emperor": {"number": 4, "element": "Fire", "upright": "Authority, establishment, structure, father figure", "reversed": "Domination, excessive control, lack of discipline"},
    "The Hierophant": {"number": 5, "element": "Earth", "upright": "Spiritual wisdom, religious beliefs, conformity, tradition", "reversed": "Personal beliefs, freedom, challenging status quo"},
    "The Lovers": {"number": 6, "element": "Air", "upright": "Love, harmony, relationships, values alignment", "reversed": "Self-love, disharmony, imbalance, misalignment"},
    "The Chariot": {"number": 7, "element": "Water", "upright": "Control, willpower, success, action, determination", "reversed": "Self-discipline, opposition, lack of direction"},
    "Strength": {"number": 8, "element": "Fire", "upright": "Strength, courage, patience, control, compassion", "reversed": "Inner strength, self-doubt, low energy, raw emotion"},
    "The Hermit": {"number": 9, "element": "Earth", "upright": "Soul-searching, introspection, inner guidance, solitude", "reversed": "Isolation, loneliness, withdrawal"},
    "Wheel of Fortune": {"number": 10, "element": "Fire", "upright": "Good luck, karma, life cycles, destiny, turning point", "reversed": "Bad luck, lack of control, clinging to control"},
    "Justice": {"number": 11, "element": "Air", "upright": "Justice, fairness, truth, cause and effect, law", "reversed": "Unfairness, lack of accountability, dishonesty"},
    "The Hanged Man": {"number": 12, "element": "Water", "upright": "Pause, surrender, letting go, new perspectives", "reversed": "Delays, resistance, stalling, indecision"},
    "Death": {"number": 13, "element": "Water", "upright": "Endings, change, transformation, transition", "reversed": "Resistance to change, personal transformation, inner purging"},
    "Temperance": {"number": 14, "element": "Fire", "upright": "Balance, moderation, patience, purpose, meaning", "reversed": "Imbalance, excess, self-healing, realignment"},
    "The Devil": {"number": 15, "element": "Earth", "upright": "Shadow self, attachment, addiction, restriction, sexuality", "reversed": "Releasing limiting beliefs, exploring dark thoughts, detachment"},
    "The Tower": {"number": 16, "element": "Fire", "upright": "Sudden change, upheaval, chaos, revelation, awakening", "reversed": "Personal transformation, fear of change, averting disaster"},
    "The Star": {"number": 17, "element": "Air", "upright": "Hope, faith, purpose, renewal, spirituality", "reversed": "Lack of faith, despair, self-trust, disconnection"},
    "The Moon": {"number": 18, "element": "Water", "upright": "Illusion, fear, the unconscious, intuition, confusion", "reversed": "Release of fear, repressed emotion, inner confusion"},
    "The Sun": {"number": 19, "element": "Fire", "upright": "Positivity, fun, warmth, success, vitality", "reversed": "Inner child, feeling down, overly optimistic"},
    "Judgement": {"number": 20, "element": "Fire", "upright": "Judgement, rebirth, inner calling, absolution", "reversed": "Self-doubt, inner critic, ignoring the call"},
    "The World": {"number": 21, "element": "Earth", "upright": "Completion, integration, accomplishment, travel", "reversed": "Seeking personal closure, short-cuts, delays"},
}

SUIT_ELEMENTS: dict[str, str] = {
    "Wands": "Fire", "Cups": "Water", "Swords": "Air", "Pentacles": "Earth"
}

ELEMENT_COLORS: dict[str, tuple] = {
    "Fire": (180, 60, 40), "Water": (40, 80, 160),
    "Air": (160, 200, 220), "Earth": (100, 140, 60),
}


def card_element(card_name: str) -> str:
    if card_name in MAJOR_ARCANA_DETAILS:
        return MAJOR_ARCANA_DETAILS[card_name]["element"]
    parts = card_name.split(" of ")
    if len(parts) == 2:
        return SUIT_ELEMENTS.get(parts[1], "Air")
    return "Air"


def card_keywords(card_name: str) -> str:
    if card_name in CARD_KEYWORDS:
        return CARD_KEYWORDS[card_name]
    parts = card_name.split(" of ")
    if len(parts) == 2:
        rank, suit = parts
        return f"{SUIT_KEYWORDS.get(suit, '')} / {RANK_KEYWORDS.get(rank, '')}"
    return card_name


def card_upright_meaning(card_name: str) -> str:
    if card_name in MAJOR_ARCANA_DETAILS:
        return MAJOR_ARCANA_DETAILS[card_name]["upright"]
    parts = card_name.split(" of ")
    if len(parts) == 2:
        rank, suit = parts
        return f"{SUIT_KEYWORDS.get(suit, 'unknown')}; {RANK_KEYWORDS.get(rank, 'unknown')}"
    return "Unknown meaning"


def card_reversed_meaning(card_name: str) -> str:
    if card_name in MAJOR_ARCANA_DETAILS:
        return MAJOR_ARCANA_DETAILS[card_name]["reversed"]
    parts = card_name.split(" of ")
    if len(parts) == 2:
        rank, suit = parts
        return f"Reversed {suit.lower()} energy; blocked {RANK_KEYWORDS.get(rank, 'potential')}"
    return "Reversed meaning unknown"


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def build_seed(question: str, user_id: str, reading_date: str) -> tuple[int, str]:
    """Deterministic seed: sha256(φ₀ ‖ α ‖ question ‖ user_id ‖ date) mod 2³²."""
    seed_str = f"{PHI0:.15f}{ALPHA:.15f}{question}{user_id}{reading_date}"
    h = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()
    return int(h, 16) % (2 ** 32), h


# ---------------------------------------------------------------------------
# Draw functions
# ---------------------------------------------------------------------------

def _draw_cards(seed_int: int, n: int) -> list[int]:
    """Draw n unique card indices with φ²-weighted Major Arcana probability."""
    rng = np.random.default_rng(seed_int)
    weights = np.ones(78)
    weights[:22] *= PHI0 ** 2
    weights /= weights.sum()
    return [int(i) for i in rng.choice(78, size=n, replace=False, p=weights)]


def draw_celtic_cross(seed_int: int) -> list[dict]:
    """10-card Celtic Cross draw with φ²-weighted Major Arcana probability."""
    indices = _draw_cards(seed_int, 10)
    cards = []
    for pos, idx in zip(CELTIC_CROSS_POSITIONS, indices):
        cards.append(_make_card_entry(idx, pos))
    return cards


def draw_three_card(seed_int: int) -> list[dict]:
    """Past/Present/Future three-card spread."""
    indices = _draw_cards(seed_int, 3)
    cards = []
    for pos, idx in zip(THREE_CARD_POSITIONS, indices):
        cards.append(_make_card_entry(idx, pos))
    return cards


def draw_single_card(seed_int: int) -> list[dict]:
    """Single card oracle draw."""
    indices = _draw_cards(seed_int, 1)
    return [_make_card_entry(indices[0], SINGLE_CARD_POSITIONS[0])]


def _make_card_entry(idx: int, pos: dict) -> dict:
    name = DECK[idx]
    arcana = "Major" if idx < 22 else "Minor"
    suit = None
    rank = None
    if arcana == "Minor":
        parts = name.split(" of ")
        if len(parts) == 2:
            rank, suit = parts
    roman = None
    if arcana == "Major" and name in MAJOR_ARCANA_DETAILS:
        roman = _to_roman(MAJOR_ARCANA_DETAILS[name]["number"])
    return {
        "position_number": pos["number"],
        "position_name": pos["name"],
        "position_subtitle": pos["subtitle"],
        "manifold_analog": pos["manifold"],
        "card_index": idx,
        "card_name": name,
        "arcana": arcana,
        "suit": suit,
        "rank": rank,
        "roman_numeral": roman,
        "element": card_element(name),
        "keywords": card_keywords(name),
        "upright_meaning": card_upright_meaning(name),
        "reversed_meaning": card_reversed_meaning(name),
    }


def _to_roman(n: int) -> str:
    vals = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    result = ""
    for v, r in vals:
        while n >= v:
            result += r
            n -= v
    return result or "0"


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------

def synthesize_celtic_cross(cards: list[dict], question: str) -> str:
    present = cards[0]["card_name"]
    challenge = cards[1]["card_name"]
    outcome = cards[9]["card_name"]
    future = cards[5]["card_name"]
    crown = cards[4]["card_name"]
    majors = [c for c in cards if c["arcana"] == "Major"]
    major_density = len(majors) / 10.0
    density_str = "high" if major_density >= 0.5 else "moderate" if major_density >= 0.3 else "low"

    para1 = (
        f"The field opens at {present}, with {challenge} crossing it — "
        f"a tension between the current state (Ψ_n) and the conservation constraint. "
        f"The crown position ({crown}) names the available higher-dimensional resource."
    )
    para2 = (
        f"The trajectory runs toward {future} before converging on {outcome} as the "
        f"fixed point. Major Arcana density: {major_density:.0%} ({len(majors)}/10) — {density_str} "
        f"KK excitation. The U-operator for '{question}' converges to: {outcome}."
    )
    return para1 + "\n\n" + para2


def synthesize_three_card(cards: list[dict], question: str) -> str:
    past, present, future = cards[0]["card_name"], cards[1]["card_name"], cards[2]["card_name"]
    return (
        f"The arc from {past} (past) through {present} (present) toward {future} (future) "
        f"describes the geodesic trajectory of '{question}'. "
        f"The field has moved through {card_keywords(past)}, "
        f"now rests in {card_keywords(present)}, "
        f"and curves toward {card_keywords(future)}."
    )


def synthesize_single_card(cards: list[dict], question: str) -> str:
    card = cards[0]["card_name"]
    return (
        f"The oracle speaks through {card}: {card_keywords(card)}. "
        f"For the question '{question}', this single signal from the field carries "
        f"{cards[0]['upright_meaning']}."
    )


# ---------------------------------------------------------------------------
# Full reading record
# ---------------------------------------------------------------------------

def build_reading(
    question: str,
    user_id: str,
    reading_date: Optional[str] = None,
    spread_type: str = "celtic_cross",
) -> dict:
    """Build a complete tarot reading record."""
    if reading_date is None:
        reading_date = str(_date_cls.today())
    seed_int, seed_hex = build_seed(question, user_id, reading_date)

    if spread_type == "celtic_cross":
        cards = draw_celtic_cross(seed_int)
        synthesis = synthesize_celtic_cross(cards, question)
    elif spread_type == "three_card":
        cards = draw_three_card(seed_int)
        synthesis = synthesize_three_card(cards, question)
    else:
        cards = draw_single_card(seed_int)
        synthesis = synthesize_single_card(cards, question)

    major_count = sum(1 for c in cards if c["arcana"] == "Major")
    return {
        "spread_type": spread_type,
        "question": question,
        "user_id": user_id,
        "reading_date": reading_date,
        "seed_int": seed_int,
        "seed_hex": seed_hex,
        "phi0": PHI0,
        "alpha": ALPHA,
        "phi_squared": PHI0 ** 2,
        "cards": cards,
        "synthesis": synthesis,
        "major_count": major_count,
        "minor_count": len(cards) - major_count,
        "major_density": round(major_count / max(len(cards), 1), 3),
    }


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
