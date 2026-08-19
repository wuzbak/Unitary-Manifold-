"""
DelPhi — Rune Oracle Engine
Elder Futhark 24-rune system: single, three-rune, and runic cross spreads.
"""
from __future__ import annotations

import hashlib
from datetime import date as _date_cls
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# Elder Futhark rune data
# ---------------------------------------------------------------------------

RUNES: list[dict] = [
    {
        "name": "Fehu", "symbol": "ᚠ", "phoneme": "F",
        "element": "Fire",
        "keywords": "wealth, cattle, abundance, prosperity, luck",
        "upright_meaning": "Wealth, prosperity, abundance, material gain, financial success, fertility, luck, hope",
        "reversed_meaning": "Loss of wealth, greed, financial failure, covetousness, stagnation",
        "description": "Fehu is the rune of movable wealth — cattle, gold, possessions. It signals abundance flowing in, new beginnings in the material realm.",
    },
    {
        "name": "Uruz", "symbol": "ᚢ", "phoneme": "U",
        "element": "Earth",
        "keywords": "strength, vitality, primal force, health, endurance",
        "upright_meaning": "Physical strength, speed, untamed potential, vitality, wild power, good health, courage",
        "reversed_meaning": "Weakness, illness, obsession, misdirected force, brutality",
        "description": "Uruz represents the wild ox — raw, untamed power. It speaks to primal vitality and the force of nature within us.",
    },
    {
        "name": "Thurisaz", "symbol": "ᚦ", "phoneme": "Th",
        "element": "Fire",
        "keywords": "thorn, protection, gateway, chaos, conflict",
        "upright_meaning": "Protection, strong force, directed energy, conflict, catharsis, reactive force",
        "reversed_meaning": "Danger, defenselessness, compulsion, betrayal",
        "description": "Thurisaz is the thorn — a gateway or force of protection. It represents Thor's hammer and the capacity to drive away evil.",
    },
    {
        "name": "Ansuz", "symbol": "ᚨ", "phoneme": "A",
        "element": "Air",
        "keywords": "communication, wisdom, divine message, inspiration, Odin",
        "upright_meaning": "Signals, messages, divine inspiration, communication, revelation, wisdom, truth",
        "reversed_meaning": "Miscommunication, manipulation, deceit, blocked wisdom",
        "description": "Ansuz is the rune of Odin — divine communication, the breath of life, inspiration and sacred wisdom flowing from above.",
    },
    {
        "name": "Raidho", "symbol": "ᚱ", "phoneme": "R",
        "element": "Air",
        "keywords": "journey, travel, movement, rhythm, rightness",
        "upright_meaning": "Journey, travel, movement, rhythm, quest, right action, alignment",
        "reversed_meaning": "Crisis, stagnation, feeling stuck, disrupted journey",
        "description": "Raidho is the chariot wheel — movement along the right path. It governs journeys both physical and spiritual.",
    },
    {
        "name": "Kenaz", "symbol": "ᚲ", "phoneme": "K",
        "element": "Fire",
        "keywords": "torch, knowledge, clarity, creativity, enlightenment",
        "upright_meaning": "Vision, revelation, knowledge, creativity, ability, illumination, insight",
        "reversed_meaning": "Disease, darkness, instability, loss of direction",
        "description": "Kenaz is the torch or beacon — light in darkness. It represents the knowledge that illuminates and guides creative action.",
    },
    {
        "name": "Gebo", "symbol": "ᚷ", "phoneme": "G",
        "element": "Air",
        "keywords": "gift, generosity, partnership, exchange, balance",
        "upright_meaning": "Gifts, exchange, partnerships, generosity, interconnection, hospitality",
        "reversed_meaning": "Greed, loneliness, dependence, over-giving, imbalance (Gebo has no reversal in some traditions)",
        "description": "Gebo is the gift — the sacred exchange between equals. It represents the bonds of partnership and the obligations of generosity.",
    },
    {
        "name": "Wunjo", "symbol": "ᚹ", "phoneme": "W",
        "element": "Earth",
        "keywords": "joy, pleasure, harmony, fellowship, well-being",
        "upright_meaning": "Joy, comfort, pleasure, fellowship, harmony, prosperity, optimism",
        "reversed_meaning": "Alienation, sorrow, strife, rage, recklessness",
        "description": "Wunjo is the rune of joy and belonging — the happiness that comes from harmony with one's clan and the natural order.",
    },
    {
        "name": "Hagalaz", "symbol": "ᚺ", "phoneme": "H",
        "element": "Water",
        "keywords": "hail, disruption, wrath of nature, uncontrolled forces",
        "upright_meaning": "Wrath of nature, uncontrolled forces, unavoidable disruption, testing, hail",
        "reversed_meaning": "Natural disaster, catastrophe, stagnation (no traditional reversal)",
        "description": "Hagalaz is hailstone — the destructive force of nature that clears the way for new growth. Disruption as necessary transformation.",
    },
    {
        "name": "Naudhiz", "symbol": "ᚾ", "phoneme": "N",
        "element": "Fire",
        "keywords": "need, necessity, constraint, hardship, willpower",
        "upright_meaning": "Constraint, necessity, conflict, willpower, endurance, survival",
        "reversed_meaning": "Want, deprivation, neediness, sorrow, emotional bonds",
        "description": "Naudhiz is need — the friction that produces fire. It speaks to hardship that tests and ultimately strengthens.",
    },
    {
        "name": "Isa", "symbol": "ᛁ", "phoneme": "I",
        "element": "Water",
        "keywords": "ice, stillness, standstill, clarity, patience",
        "upright_meaning": "Ice, standstill, stillness, clarity, concentration, cold clarity",
        "reversed_meaning": "Treachery, illusion, deceit, blindness (limited reversal tradition)",
        "description": "Isa is ice — the freezing of time, complete stillness. It demands patience and offers clarity found in silence.",
    },
    {
        "name": "Jera", "symbol": "ᛃ", "phoneme": "J/Y",
        "element": "Earth",
        "keywords": "harvest, cycles, seasons, reward, patience",
        "upright_meaning": "Year, a good harvest, cycles, reward for effort, peace, contentment",
        "reversed_meaning": "Sudden change, conflict, setbacks (no traditional reversal)",
        "description": "Jera is the harvest — the year turning and reaping what was sown. It promises reward for patient labor.",
    },
    {
        "name": "Eihwaz", "symbol": "ᛇ", "phoneme": "Ei",
        "element": "Earth",
        "keywords": "yew tree, death/rebirth, endurance, transformation, Yggdrasil",
        "upright_meaning": "Endurance, trust, dependability, defense, avertment, enlightenment",
        "reversed_meaning": "Confusion, damage, weakness, destruction",
        "description": "Eihwaz is the yew — the world tree Yggdrasil, axis of all existence. It bridges life and death, offering enduring strength.",
    },
    {
        "name": "Perthro", "symbol": "ᛈ", "phoneme": "P",
        "element": "Water",
        "keywords": "dice cup, mystery, fate, chance, the unknown",
        "upright_meaning": "Initiation, secrets, hidden things, occult, esoteric, evolutionary change",
        "reversed_meaning": "Addiction, stagnation, loneliness, malaise",
        "description": "Perthro is the lot cup — mystery, fate, and the hidden workings of chance. What is unknown shall be revealed.",
    },
    {
        "name": "Algiz", "symbol": "ᛉ", "phoneme": "Z/R",
        "element": "Air",
        "keywords": "protection, elk, sanctuary, divine connection, warding",
        "upright_meaning": "Protection, a shield, connection to the gods, warding off evil, sanctuary",
        "reversed_meaning": "Hidden danger, consumption, loss of divine link",
        "description": "Algiz is the elk or the protective hand — divine guardian power. It wards off danger and connects the seeker to higher realms.",
    },
    {
        "name": "Sowilo", "symbol": "ᛊ", "phoneme": "S",
        "element": "Fire",
        "keywords": "sun, victory, wholeness, energy, enlightenment",
        "upright_meaning": "Wholeness, success, vitality, good health, optimism, victory",
        "reversed_meaning": "False goals, bad counsel, destruction (limited reversal in tradition)",
        "description": "Sowilo is the sun — radiant energy, victory, and wholeness. The solar force that guides toward success.",
    },
    {
        "name": "Tiwaz", "symbol": "ᛏ", "phoneme": "T",
        "element": "Air",
        "keywords": "Tyr, justice, sacrifice, victory, law",
        "upright_meaning": "Victory, passion, daring, justice, leadership, rationality, duty",
        "reversed_meaning": "Imbalance, injustice, defeat, self-sacrifice gone wrong",
        "description": "Tiwaz is the sky god Tyr — justice, sacrifice, and the courage to act rightly even at personal cost.",
    },
    {
        "name": "Berkano", "symbol": "ᛒ", "phoneme": "B",
        "element": "Earth",
        "keywords": "birch, fertility, growth, renewal, feminine",
        "upright_meaning": "Birth, fertility, feminine, beauty, blossoming, new beginnings, growth",
        "reversed_meaning": "Family problems, anxiety, careless, loss of control",
        "description": "Berkano is the birch goddess — fertility, birth, and the tender new growth of spring. The nurturing feminine principle.",
    },
    {
        "name": "Ehwaz", "symbol": "ᛖ", "phoneme": "E",
        "element": "Earth",
        "keywords": "horse, partnership, trust, movement, loyalty",
        "upright_meaning": "Movement, progress, swift change, transit, horse and rider partnership",
        "reversed_meaning": "Restlessness, disharmony, mistrust, recklessness",
        "description": "Ehwaz is the horse — the swift partnership between horse and rider. It governs trust, cooperation, and harmonious movement.",
    },
    {
        "name": "Mannaz", "symbol": "ᛗ", "phoneme": "M",
        "element": "Air",
        "keywords": "humanity, self, consciousness, community, human condition",
        "upright_meaning": "Humanity, the self, consciousness, divine structure, attitude, society",
        "reversed_meaning": "Depression, mortality, cunning, manipulation",
        "description": "Mannaz is humankind — consciousness, self-awareness, and the divine spark in human form. It asks for introspection.",
    },
    {
        "name": "Laguz", "symbol": "ᛚ", "phoneme": "L",
        "element": "Water",
        "keywords": "water, lake, flow, intuition, the unconscious",
        "upright_meaning": "Flow, water, sea, fertility, renewal, dreams, intuition, life force",
        "reversed_meaning": "Fear, confusion, avoidance, withering",
        "description": "Laguz is the water — the primordial ocean of intuition and the unconscious. It flows around obstacles and seeks its level.",
    },
    {
        "name": "Ingwaz", "symbol": "ᛜ", "phoneme": "Ing",
        "element": "Earth",
        "keywords": "fertility god, completion, gestation, rest, inner peace",
        "upright_meaning": "Fertility, new beginnings, gestation, internal growth, virtue, peace",
        "reversed_meaning": "Impotence, movement without change, wasted energy (no reversal in most traditions)",
        "description": "Ingwaz is the fertility god Ing — completion of a cycle and the gestation before new birth. Rest before action.",
    },
    {
        "name": "Dagaz", "symbol": "ᛞ", "phoneme": "D",
        "element": "Fire",
        "keywords": "dawn, day, breakthrough, clarity, awakening",
        "upright_meaning": "Breakthrough, clarity, transformation, hope, dawning light, awakening",
        "reversed_meaning": "Completion, ending, blindness (no reversal in most traditions)",
        "description": "Dagaz is the dawn — the moment of breakthrough between darkness and light. It signals awakening and radical positive change.",
    },
    {
        "name": "Othala", "symbol": "ᛟ", "phoneme": "O",
        "element": "Earth",
        "keywords": "heritage, homeland, ancestry, inheritance, property",
        "upright_meaning": "Ancestry, homeland, heritage, prosperity, estate, inheritance, legacy",
        "reversed_meaning": "Lack of roots, clannishness, prejudice, totalitarianism",
        "description": "Othala is the ancestral estate — the sacred inheritance of land, blood, and wisdom passed down through generations.",
    },
]

RUNE_INDEX: dict[str, dict] = {r["name"]: r for r in RUNES}
RUNE_SYMBOL_INDEX: dict[str, dict] = {r["symbol"]: r for r in RUNES}

# Spread positions
SINGLE_RUNE_POSITIONS = [
    {"number": 1, "name": "Oracle", "subtitle": "The Cast", "meaning": "The rune speaks."},
]

THREE_RUNE_POSITIONS = [
    {"number": 1, "name": "Past", "subtitle": "What was", "meaning": "The situation's origin."},
    {"number": 2, "name": "Present", "subtitle": "What is", "meaning": "The current challenge."},
    {"number": 3, "name": "Future", "subtitle": "What will be", "meaning": "The likely outcome."},
]

RUNIC_CROSS_POSITIONS = [
    {"number": 1, "name": "Present Situation", "subtitle": "Core matter", "meaning": "The heart of the question."},
    {"number": 2, "name": "Obstacle", "subtitle": "What blocks", "meaning": "The challenge to overcome."},
    {"number": 3, "name": "Advice", "subtitle": "Wisdom offered", "meaning": "Action the runes counsel."},
    {"number": 4, "name": "Foundation", "subtitle": "Root cause", "meaning": "Underlying influences."},
    {"number": 5, "name": "Past Influence", "subtitle": "Recent past", "meaning": "What shaped the situation."},
    {"number": 6, "name": "Outcome", "subtitle": "Resolution", "meaning": "Where this path leads."},
]


def build_seed(question: str, user_id: str, reading_date: str) -> tuple[int, str]:
    seed_str = f"RUNE{question}{user_id}{reading_date}"
    h = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()
    return int(h, 16) % (2 ** 32), h


def _draw_runes(seed_int: int, n: int, allow_reversed: bool = True) -> list[dict]:
    rng = np.random.default_rng(seed_int)
    indices = rng.choice(24, size=n, replace=False)
    result = []
    for idx in indices:
        rune = RUNES[int(idx)].copy()
        is_reversed = bool(rng.integers(0, 2)) if allow_reversed else False
        rune["is_reversed"] = is_reversed
        rune["active_meaning"] = rune["reversed_meaning"] if is_reversed else rune["upright_meaning"]
        result.append(rune)
    return result


def draw_single_rune(seed_int: int) -> list[dict]:
    runes = _draw_runes(seed_int, 1)
    return [{"position": p, "rune": r} for p, r in zip(SINGLE_RUNE_POSITIONS, runes)]


def draw_three_rune(seed_int: int) -> list[dict]:
    runes = _draw_runes(seed_int, 3)
    return [{"position": p, "rune": r} for p, r in zip(THREE_RUNE_POSITIONS, runes)]


def draw_runic_cross(seed_int: int) -> list[dict]:
    runes = _draw_runes(seed_int, 6)
    return [{"position": p, "rune": r} for p, r in zip(RUNIC_CROSS_POSITIONS, runes)]


def synthesize_rune_reading(cast: list[dict], question: str, spread_type: str) -> str:
    names = [f"{c['rune']['name']}{'(R)' if c['rune']['is_reversed'] else ''}" for c in cast]
    if spread_type == "single":
        r = cast[0]["rune"]
        return (
            f"The rune {r['name']} ({r['symbol']}) speaks to '{question}': "
            f"{r['active_meaning']}. Keywords: {r['keywords']}."
        )
    elif spread_type == "three_rune":
        return (
            f"The three-rune cast for '{question}': "
            f"Past — {names[0]} ({cast[0]['rune']['active_meaning'][:80]}); "
            f"Present — {names[1]} ({cast[1]['rune']['active_meaning'][:80]}); "
            f"Future — {names[2]} ({cast[2]['rune']['active_meaning'][:80]})."
        )
    else:
        return (
            f"The runic cross reveals: {', '.join(names)}. "
            f"At the heart of '{question}' lies {cast[0]['rune']['name']} — {cast[0]['rune']['active_meaning'][:100]}. "
            f"The outcome rune is {cast[5]['rune']['name']}: {cast[5]['rune']['active_meaning'][:100]}."
        )


def build_rune_reading(
    question: str,
    user_id: str,
    reading_date: Optional[str] = None,
    spread_type: str = "three_rune",
) -> dict:
    if reading_date is None:
        reading_date = str(_date_cls.today())
    seed_int, seed_hex = build_seed(question, user_id, reading_date)

    if spread_type == "single":
        cast = draw_single_rune(seed_int)
    elif spread_type == "runic_cross":
        cast = draw_runic_cross(seed_int)
    else:
        cast = draw_three_rune(seed_int)

    return {
        "spread_type": spread_type,
        "question": question,
        "user_id": user_id,
        "reading_date": reading_date,
        "seed_int": seed_int,
        "seed_hex": seed_hex,
        "cast": cast,
        "synthesis": synthesize_rune_reading(cast, question, spread_type),
    }


def get_rune_by_name(name: str) -> Optional[dict]:
    return RUNE_INDEX.get(name)


def get_rune_by_symbol(symbol: str) -> Optional[dict]:
    return RUNE_SYMBOL_INDEX.get(symbol)


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
