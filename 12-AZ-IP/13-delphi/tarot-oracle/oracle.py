#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# TarotOracle — Unitary Manifold–seeded Celtic Cross reading engine
# AxiomZero Technologies / ThomasCory Walker-Pearson  2026
"""
oracle.py
=========
φ²-weighted, deterministically seeded Celtic Cross tarot engine.

Seed construction
-----------------
  seed_str = f"{PHI0:.15f}{ALPHA:.15f}{question}{user_id}{date}"
  seed_int = sha256(seed_str) mod 2³²   ← numpy-compatible

The golden ratio φ₀ = 1.618… is not arbitrary — it is the FTUM fixed-point
value of the radion field.  α = φ₀⁻² = 0.381… is the nonminimal coupling
derived from the Kaluza-Klein cross-block curvature.

Draw weighting
--------------
  Major Arcana (cards 0–21, 22 total)  weight = φ²  ≈ 2.618
  Minor Arcana (cards 22–77, 56 total) weight = 1.0

This encodes the KK spectral excitation density: higher-dimensional modes
(Major Arcana) carry more energy per degree of freedom than the mundane
four-dimensional ones (Minor Arcana).

Usage
-----
  python oracle.py --question "What should I focus on?" --user "tcwp"
  python oracle.py --question "Will I influence my managers?" --user "tcwp" --date 2026-04-22
  python oracle.py --reading readings/reading_002.json    # replay / display saved
"""

import argparse
import hashlib
import json
import sys
import textwrap
from datetime import date as _date_cls
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Manifold constants
# ---------------------------------------------------------------------------
PHI0 = 1.6180339887448950   # golden ratio — FTUM radion fixed point
ALPHA = 1.0 / PHI0 ** 2    # α = φ₀⁻²  ≈ 0.38197

# ---------------------------------------------------------------------------
# Deck
# ---------------------------------------------------------------------------
MAJOR_ARCANA = [
    "The Fool",            # 0
    "The Magician",        # 1
    "The High Priestess",  # 2
    "The Empress",         # 3
    "The Emperor",         # 4
    "The Hierophant",      # 5
    "The Lovers",          # 6
    "The Chariot",         # 7
    "Strength",            # 8
    "The Hermit",          # 9
    "Wheel of Fortune",    # 10
    "Justice",             # 11
    "The Hanged Man",      # 12
    "Death",               # 13
    "Temperance",          # 14
    "The Devil",           # 15
    "The Tower",           # 16
    "The Star",            # 17
    "The Moon",            # 18
    "The Sun",             # 19
    "Judgement",           # 20
    "The World",           # 21
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

assert len(DECK) == 78, f"Deck length mismatch: {len(DECK)}"
assert len(MAJOR_ARCANA) == 22
assert len(MINOR_ARCANA) == 56

# ---------------------------------------------------------------------------
# Celtic Cross positions → Unitary Manifold analog
# ---------------------------------------------------------------------------
POSITIONS = [
    {
        "number": 1,
        "name": "Present",
        "subtitle": "The Situation — Ψ_n",
        "manifold": "The current state of the information field. Where the seeker stands in the FTUM cycle.",
    },
    {
        "number": 2,
        "name": "Challenge",
        "subtitle": "What Crosses — ∇_μ J^μ_inf = 0",
        "manifold": "The conservation constraint. The tension that must be resolved for the field to advance.",
    },
    {
        "number": 3,
        "name": "Root",
        "subtitle": "Foundation — T operator (topological invariant)",
        "manifold": "The topological substrate. What is fixed and cannot be changed — the winding number.",
    },
    {
        "number": 4,
        "name": "Past",
        "subtitle": "What Passes — I operator (irreversible sector)",
        "manifold": "Information absorbed permanently into the record. The Second Law in the personal field.",
    },
    {
        "number": 5,
        "name": "Crown",
        "subtitle": "What May Be — H operator (holographic projection)",
        "manifold": "The higher-dimensional projection. What the boundary encodes about the interior.",
    },
    {
        "number": 6,
        "name": "Future",
        "subtitle": "What Comes — Ψ_{n+1}",
        "manifold": "The next FTUM step. The attractor basin toward which the trajectory curves.",
    },
    {
        "number": 7,
        "name": "Self",
        "subtitle": "Your Attitude — φ₀ (radion / mediating field)",
        "manifold": "The seeker as mediating field — how you couple the 4D and 5D sectors.",
    },
    {
        "number": 8,
        "name": "Environment",
        "subtitle": "External Influences — KK excitation spectrum",
        "manifold": "The Kaluza-Klein modes surrounding you — the field density of your context.",
    },
    {
        "number": 9,
        "name": "Hopes & Fears",
        "subtitle": "The Geodesic Arc — trajectory of desire and resistance",
        "manifold": "The geodesic tension between desired attractor and feared repeller in the manifold.",
    },
    {
        "number": 10,
        "name": "Outcome",
        "subtitle": "Fixed Point — U·Ψ_n = Ψ_{n+1}",
        "manifold": "The convergence point of the U-operator. What the field stabilises to if the arc completes.",
    },
]

# ---------------------------------------------------------------------------
# Interpretation helpers
# ---------------------------------------------------------------------------

CARD_KEYWORDS: dict[str, str] = {
    # Major Arcana
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


def card_keywords(card_name: str) -> str:
    if card_name in CARD_KEYWORDS:
        return CARD_KEYWORDS[card_name]
    parts = card_name.split(" of ")
    if len(parts) == 2:
        rank, suit = parts
        return f"{SUIT_KEYWORDS.get(suit, '')} / {RANK_KEYWORDS.get(rank, '')}"
    return card_name


def interpret_position(card: dict) -> str:
    cn = card["card_name"]
    pn = card["position_name"]
    kw = card_keywords(cn)
    return f"{cn} ({kw}) in {pn}."


def synthesize(cards: list[dict], question: str) -> str:
    present = cards[0]["card_name"]
    challenge = cards[1]["card_name"]
    outcome = cards[9]["card_name"]
    future = cards[5]["card_name"]
    crown = cards[4]["card_name"]
    majors = [c["card_name"] for c in cards if c["arcana"] == "Major"]
    major_density = len(majors) / 10.0
    density_str = (
        "high" if major_density >= 0.5
        else "moderate" if major_density >= 0.3
        else "low"
    )
    density_meaning = {
        "high": "large-scale structural forces dominate the personal field",
        "moderate": "structural forces are present but personal-scale dynamics carry weight too",
        "low": "the reading operates in the everyday field, not the large-arc forces",
    }[density_str]

    para1 = (
        f"The field opens at {present}, with {challenge} crossing it — "
        f"a tension between the current state (Ψ_n) and the conservation constraint "
        f"(∇_μ J^μ_inf = 0) that must be resolved before the arc completes. "
        f"The crown position ({crown}) names the available higher-dimensional resource: "
        f"the H-operator projection that can be drawn down if the seeker is willing to "
        f"work at the boundary, not just the interior."
    )

    para2 = (
        f"The trajectory runs toward {future} before converging on {outcome} as the "
        f"fixed point. Major Arcana density is {major_density:.0%} ({len(majors)}/10) "
        f"— {density_str} KK excitation. At {density_str} density, the manifold is "
        f"{density_meaning}. "
        f"The U-operator for '{question}' converges to: **{outcome}**."
    )

    return para1 + "\n\n" + para2


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def build_seed(question: str, user_id: str, reading_date: str) -> tuple[int, str]:
    """Deterministic seed: sha256(φ₀ ‖ α ‖ question ‖ user_id ‖ date) mod 2³²."""
    seed_str = f"{PHI0:.15f}{ALPHA:.15f}{question}{user_id}{reading_date}"
    h = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()
    return int(h, 16) % (2 ** 32), h


# ---------------------------------------------------------------------------
# Draw
# ---------------------------------------------------------------------------

def draw_celtic_cross(seed_int: int) -> list[dict]:
    """10-card Celtic Cross draw with φ²-weighted Major Arcana probability."""
    rng = np.random.default_rng(seed_int)
    weights = np.ones(78)
    weights[:22] *= PHI0 ** 2
    weights /= weights.sum()
    indices = rng.choice(78, size=10, replace=False, p=weights)
    cards = []
    for pos, idx in zip(POSITIONS, indices):
        idx = int(idx)
        cards.append({
            "position_number": pos["number"],
            "position_name": pos["name"],
            "position_subtitle": pos["subtitle"],
            "manifold_analog": pos["manifold"],
            "card_index": idx,
            "card_name": DECK[idx],
            "arcana": "Major" if idx < 22 else "Minor",
        })
    return cards


# ---------------------------------------------------------------------------
# Session record
# ---------------------------------------------------------------------------

def build_record(
    question: str,
    user_id: str,
    reading_date: str,
    reading_id: str,
    cards: list[dict],
    seed_int: int,
    seed_hex: str,
) -> dict:
    interpretation = {
        "per_position": {
            str(c["position_number"]): interpret_position(c)
            for c in cards
        },
        "synthesis": synthesize(cards, question),
    }
    major_count = sum(1 for c in cards if c["arcana"] == "Major")
    return {
        "schema_version": "1.0",
        "id": reading_id,
        "timestamp": reading_date,
        "user_id": user_id,
        "question": question,
        "seed": {
            "phi0": PHI0,
            "alpha": ALPHA,
            "phi_squared": PHI0 ** 2,
            "seed_int": seed_int,
            "seed_hex": seed_hex,
        },
        "draw": cards,
        "interpretation": interpretation,
        "manifold_metadata": {
            "major_count": major_count,
            "minor_count": 10 - major_count,
            "major_density": round(major_count / 10.0, 3),
            "phi_weight": round(PHI0 ** 2, 6),
        },
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_text(record: dict) -> str:
    lines: list[str] = []

    def a(s: str = "") -> None:
        lines.append(s)

    a("=" * 70)
    a(f"  TAROT ORACLE — {record['id']}")
    a(f"  {record['timestamp']}  ·  user: {record['user_id']}")
    a("=" * 70)
    a()
    a(f"  Question: {record['question']}")
    a()
    a(f"  Seed (sha256 mod 2³²): {record['seed']['seed_int']}")
    a(f"  φ₀ = {record['seed']['phi0']:.15f}")
    a(f"  α  = {record['seed']['alpha']:.15f}")
    a(f"  φ²-weight on Major Arcana = {record['seed']['phi_squared']:.6f}")
    a()
    a("─" * 70)
    a("  CELTIC CROSS DRAW")
    a("─" * 70)
    for c in record["draw"]:
        tag = "[MAJOR]" if c["arcana"] == "Major" else "[minor]"
        a(f"  {c['position_number']:>2}. {c['position_name']:<18} {tag}  {c['card_name']}")
        a(f"      ↳ {c['position_subtitle']}")
        a()
    a("─" * 70)
    meta = record["manifold_metadata"]
    a(f"  Major Arcana: {meta['major_count']}/10  "
      f"({meta['major_density']:.0%} KK excitation density)")
    a("─" * 70)
    a()
    a("  POSITION INTERPRETATIONS")
    a()
    for c in record["draw"]:
        a(f"  {c['position_number']}. {c['position_name']}")
        a(f"     {record['interpretation']['per_position'][str(c['position_number'])]}")
        a(f"     Manifold: {c['manifold_analog']}")
        a()
    a("─" * 70)
    a("  SYNTHESIS — GEODESIC ARC  Ψ_n → Ψ_{n+1}")
    a("─" * 70)
    a()
    for para in record["interpretation"]["synthesis"].split("\n\n"):
        a(textwrap.fill(para, width=68, initial_indent="  ", subsequent_indent="  "))
        a()
    a("=" * 70)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def next_reading_id(readings_dir: Path) -> str:
    existing = sorted(readings_dir.glob("reading_*.json"))
    return f"READING_{len(existing) + 1:03d}"


def save_record(record: dict, readings_dir: Path) -> Path:
    readings_dir.mkdir(parents=True, exist_ok=True)
    path = readings_dir / f"{record['id'].lower()}.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
    return path


def load_record(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unitary Manifold–seeded Celtic Cross tarot oracle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python oracle.py --question "What should I focus on?" --user tcwp
              python oracle.py --question "Will I influence my managers?" \\
                               --user tcwp --date 2026-04-22
              python oracle.py --reading readings/reading_002.json
        """),
    )
    parser.add_argument("--question", "-q", help="The question for the reading")
    parser.add_argument("--user", "-u", default="anonymous", help="User ID (default: anonymous)")
    parser.add_argument("--date", "-d", default=None,
                        help="Reading date YYYY-MM-DD (default: today)")
    parser.add_argument("--reading", "-r", help="Path to a saved JSON record to display")
    parser.add_argument("--json", action="store_true", help="Also print raw JSON")
    parser.add_argument("--no-save", action="store_true",
                        help="Do not save the record to disk")
    args = parser.parse_args()

    readings_dir = Path(__file__).parent / "readings"

    if args.reading:
        record = load_record(Path(args.reading))
        print(render_text(record))
        if args.json:
            print(json.dumps(record, indent=2))
        return

    if not args.question:
        parser.error("--question is required when not replaying a saved reading")

    reading_date = args.date or str(_date_cls.today())
    reading_id = next_reading_id(readings_dir)
    seed_int, seed_hex = build_seed(args.question, args.user, reading_date)
    cards = draw_celtic_cross(seed_int)
    record = build_record(
        question=args.question,
        user_id=args.user,
        reading_date=reading_date,
        reading_id=reading_id,
        cards=cards,
        seed_int=seed_int,
        seed_hex=seed_hex,
    )

    print(render_text(record))

    if not args.no_save:
        path = save_record(record, readings_dir)
        print(f"\n  [saved → {path}]")

    if args.json:
        print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
