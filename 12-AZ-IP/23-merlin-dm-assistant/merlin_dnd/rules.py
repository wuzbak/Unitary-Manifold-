# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

# Encounter thresholds and multipliers intentionally follow the 2014 5e DMG
# encounter-budget model as a deterministic baseline. Product consumers can
# still tag campaigns as `5e-2024`, but current difficulty grading remains this
# published legacy table until a separate 2024-calibrated budget lane is added.

PROFICIENCY_BY_LEVEL = {
    range(1, 5): 2,
    range(5, 9): 3,
    range(9, 13): 4,
    range(13, 17): 5,
    range(17, 21): 6,
}

CLASS_HIT_DIE = {
    "artificer": 8,
    "barbarian": 12,
    "bard": 8,
    "cleric": 8,
    "druid": 8,
    "fighter": 10,
    "monk": 8,
    "paladin": 10,
    "ranger": 10,
    "rogue": 8,
    "sorcerer": 6,
    "warlock": 8,
    "wizard": 6,
}

CLASS_SPELLCASTING_ABILITY = {
    "artificer": "intelligence",
    "bard": "charisma",
    "cleric": "wisdom",
    "druid": "wisdom",
    "paladin": "charisma",
    "ranger": "wisdom",
    "sorcerer": "charisma",
    "warlock": "charisma",
    "wizard": "intelligence",
}

ENCOUNTER_THRESHOLDS = {
    1: (25, 50, 75, 100),
    2: (50, 100, 150, 200),
    3: (75, 150, 225, 400),
    4: (125, 250, 375, 500),
    5: (250, 500, 750, 1100),
    6: (300, 600, 900, 1400),
    7: (350, 750, 1100, 1700),
    8: (450, 900, 1400, 2100),
    9: (550, 1100, 1600, 2400),
    10: (600, 1200, 1900, 2800),
    11: (800, 1600, 2400, 3600),
    12: (1000, 2000, 3000, 4500),
    13: (1100, 2200, 3400, 5100),
    14: (1250, 2500, 3800, 5700),
    15: (1400, 2800, 4300, 6400),
    16: (1600, 3200, 4800, 7200),
    17: (2000, 3900, 5900, 8800),
    18: (2100, 4200, 6300, 9500),
    19: (2400, 4900, 7300, 10900),
    20: (2800, 5700, 8500, 12700),
}

ENCOUNTER_MULTIPLIER = {
    1: 1.0,
    2: 1.5,
    3: 2.0,
    6: 2.5,
    10: 3.0,
    15: 4.0,
}

RULES_UPDATE_DIGEST = {
    "5e-2014": [
        "Use the 2014 PHB/DMG baseline for backgrounds, exhaustion, and encounter assumptions.",
        "Feats remain optional unless the table explicitly enables them.",
    ],
    "5e-2024": [
        "Use the 2024 core rules baseline: backgrounds front-load origin identity and feat selection.",
        "Weapon mastery, refreshed class wording, and revised exhaustion/change-tracking should stay visible in table rulings.",
    ],
}


def ability_modifier(score: int) -> int:
    return (score - 10) // 2


def proficiency_bonus(level: int) -> int:
    bounded = min(20, max(1, level))
    for levels, bonus in PROFICIENCY_BY_LEVEL.items():
        if bounded in levels:
            return bonus
    return 6


def starting_hit_points(klass: str, level: int, constitution_score: int) -> int:
    hit_die = CLASS_HIT_DIE.get(klass.lower(), 8)
    con_mod = ability_modifier(constitution_score)
    first_level = hit_die + con_mod
    later_levels = max(level - 1, 0) * max((hit_die // 2) + 1 + con_mod, 1)
    return max(first_level + later_levels, level)


def passive_perception(wisdom_score: int, proficiency: int, proficient: bool = True) -> int:
    return 10 + ability_modifier(wisdom_score) + (proficiency if proficient else 0)


def spell_save_dc(proficiency: int, casting_score: int) -> int:
    return 8 + proficiency + ability_modifier(casting_score)


def spell_attack_bonus(proficiency: int, casting_score: int) -> int:
    return proficiency + ability_modifier(casting_score)


def encounter_thresholds(levels: list[int]) -> dict[str, int]:
    easy = medium = hard = deadly = 0
    for level in levels:
        row = ENCOUNTER_THRESHOLDS[min(20, max(1, level))]
        easy += row[0]
        medium += row[1]
        hard += row[2]
        deadly += row[3]
    return {"easy": easy, "medium": medium, "hard": hard, "deadly": deadly}


def adjusted_encounter_xp(base_xp: int, monster_count: int) -> int:
    applicable = 1.0
    for cutoff, multiplier in ENCOUNTER_MULTIPLIER.items():
        if monster_count >= cutoff:
            applicable = multiplier
    return int(round(base_xp * applicable))


def classify_encounter(adjusted_xp: int, thresholds: dict[str, int]) -> str:
    if adjusted_xp < thresholds["easy"]:
        return "trivial"
    if adjusted_xp < thresholds["medium"]:
        return "easy"
    if adjusted_xp < thresholds["hard"]:
        return "medium"
    if adjusted_xp < thresholds["deadly"]:
        return "hard"
    return "deadly"


def rules_update_notes(rules_edition: str) -> list[str]:
    return list(RULES_UPDATE_DIGEST.get(rules_edition, RULES_UPDATE_DIGEST["5e-2024"]))
