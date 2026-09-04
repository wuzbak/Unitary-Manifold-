# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class InventoryItem:
    id: str
    name: str
    kind: str
    quantity: int
    rarity: str
    owner_type: str
    owner_id: str
    description: str = ""
    attunement_required: bool = False
    equipped: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PlayerProfile:
    id: str
    display_name: str
    campaign_id: str
    invite_code: str
    character_ids: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
    player_id: str | None = None
    xp: int = 0
    gold: int = 0
    abilities: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    inventory: list[InventoryItem] = field(default_factory=list)
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
class SharedImage:
    id: str
    title: str
    image_url: str
    caption: str
    audience: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TreasureEntry:
    id: str
    title: str
    gold: int
    items: list[str]
    recipients: list[str]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Npc:
    id: str
    name: str
    role: str
    location: str
    attitude: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MapReference:
    id: str
    name: str
    kind: str
    image_url: str
    fog_of_war: bool
    zones: list[str] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class InviteCode:
    code: str
    role: str
    status: str
    created_by: str
    label: str = ""

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
    dm_name: str = "Dungeon Master"
    characters: list[Character] = field(default_factory=list)
    players: list[PlayerProfile] = field(default_factory=list)
    quests: list[Quest] = field(default_factory=list)
    layouts: list[DungeonLayout] = field(default_factory=list)
    encounters: list[Encounter] = field(default_factory=list)
    merchants: list[Merchant] = field(default_factory=list)
    inventory: list[InventoryItem] = field(default_factory=list)
    treasure_log: list[TreasureEntry] = field(default_factory=list)
    shared_images: list[SharedImage] = field(default_factory=list)
    npcs: list[Npc] = field(default_factory=list)
    maps: list[MapReference] = field(default_factory=list)
    active_invites: list[InviteCode] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    party_gold: int = 0
    party_xp_total: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
