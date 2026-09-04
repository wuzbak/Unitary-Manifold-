# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Character:
    id: str
    name: str
    species: str
    klass: str
    background: str
    level: int
    rules_edition: str
    alignment: str
    ability_scores: dict[str, int]
    proficiency_bonus: int
    hit_points: int
    armor_class: int
    passive_perception: int
    spellcasting_ability: str | None = None
    spell_save_dc: int | None = None
    spell_attack_bonus: int | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Quest:
    id: str
    title: str
    status: str
    objective: str
    reward: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DungeonLayout:
    id: str
    name: str
    environment: str
    zones: list[str]
    hazards: list[str]
    exits: list[str]
    lighting: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Monster:
    slug: str
    name: str
    challenge_rating: float
    xp: int
    role: str
    environment: str
    tactics: list[str]
    signature_abilities: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Merchant:
    slug: str
    name: str
    specialty: str
    temperament: str
    inventory: list[str]
    hooks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Encounter:
    id: str
    title: str
    monster_slugs: list[str]
    adjusted_xp: int
    difficulty: str
    battlefield_notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ImageBrief:
    title: str
    prompt: str
    negative_prompt: str
    anchors: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Campaign:
    id: str
    name: str
    setting: str
    rules_edition: str
    tone: str
    summary: str
    pillars: list[str]
    characters: list[Character] = field(default_factory=list)
    quests: list[Quest] = field(default_factory=list)
    layouts: list[DungeonLayout] = field(default_factory=list)
    encounters: list[Encounter] = field(default_factory=list)
    merchants: list[Merchant] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "setting": self.setting,
            "rules_edition": self.rules_edition,
            "tone": self.tone,
            "summary": self.summary,
            "pillars": list(self.pillars),
            "characters": [item.to_dict() for item in self.characters],
            "quests": [item.to_dict() for item in self.quests],
            "layouts": [item.to_dict() for item in self.layouts],
            "encounters": [item.to_dict() for item in self.encounters],
            "merchants": [item.to_dict() for item in self.merchants],
            "notes": list(self.notes),
        }
