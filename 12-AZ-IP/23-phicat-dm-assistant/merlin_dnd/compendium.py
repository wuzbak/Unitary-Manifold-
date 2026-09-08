# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from .models import Merchant, Monster

MONSTERS = {
    "goblin-skirmishers": Monster(
        slug="goblin-skirmishers",
        name="Goblin Skirmishers",
        challenge_rating=0.25,
        xp=50,
        role="ambusher",
        environment="ruins",
        tactics=["hit-and-run arrows", "disengage into cover"],
        signature_abilities=["nimble escape"],
    ),
    "skeleton-guard": Monster(
        slug="skeleton-guard",
        name="Skeleton Guard",
        challenge_rating=0.25,
        xp=50,
        role="frontline",
        environment="crypt",
        tactics=["hold chokepoints", "pressure with attrition"],
        signature_abilities=["undead resilience"],
    ),
    "owlbear": Monster(
        slug="owlbear",
        name="Owlbear",
        challenge_rating=3.0,
        xp=700,
        role="brute",
        environment="forest",
        tactics=["charge exposed targets", "break formation"],
        signature_abilities=["multiattack"],
    ),
    "mind-flayer": Monster(
        slug="mind-flayer",
        name="Mind Flayer",
        challenge_rating=7.0,
        xp=2900,
        role="controller",
        environment="underdark",
        tactics=["open with stun", "split party cohesion"],
        signature_abilities=["mind blast", "extract brain"],
    ),
    "young-red-dragon": Monster(
        slug="young-red-dragon",
        name="Young Red Dragon",
        challenge_rating=10.0,
        xp=5900,
        role="solo",
        environment="volcanic lair",
        tactics=["strafe with breath weapon", "threaten vertical space"],
        signature_abilities=["fire breath", "frightful presence"],
    ),
}

MERCHANTS = {
    "lantern-guild-quartermaster": Merchant(
        slug="lantern-guild-quartermaster",
        name="Lantern Guild Quartermaster",
        specialty="expedition gear",
        temperament="pragmatic",
        inventory=["rope", "pitons", "healer's kits", "lantern oil", "maps"],
        hooks=["buys dungeon sketches", "offers discounts for recovered relics"],
    ),
    "ember-arcana-broker": Merchant(
        slug="ember-arcana-broker",
        name="Ember Arcana Broker",
        specialty="spell components and scroll brokerage",
        temperament="precise",
        inventory=["spell scrolls", "focus crystals", "rare inks", "ritual chalk"],
        hooks=["wants field reports on unstable magic zones", "trades for monster glands"],
    ),
    "greenbottle-apothecary": Merchant(
        slug="greenbottle-apothecary",
        name="Greenbottle Apothecary",
        specialty="potions and poultices",
        temperament="warm",
        inventory=["healing potions", "antitoxins", "smoke sticks", "salves"],
        hooks=["needs herbs from a cursed fen", "can identify unknown spores"],
    ),
}

SPELL_EFFECTS = {
    "bless": "Adds 1d4 to attack rolls and saving throws for up to three creatures; concentration required.",
    "cure wounds": "Restores hit points on touch, scaling with higher spell slots.",
    "fireball": "20-foot-radius explosion dealing 8d6 fire damage on a failed Dexterity save.",
    "shield": "Reaction spell granting +5 AC until the start of your next turn and negating magic missile.",
    "spirit guardians": "15-foot aura that slows foes and deals radiant or necrotic damage while concentration holds.",
}


def list_monsters(*, environment: str | None = None, max_cr: float | None = None) -> list[Monster]:
    results = list(MONSTERS.values())
    if environment:
        results = [monster for monster in results if environment.lower() in monster.environment.lower()]
    if max_cr is not None:
        results = [monster for monster in results if monster.challenge_rating <= max_cr]
    return results


def get_monster(slug: str) -> Monster:
    return MONSTERS[slug]


def list_merchants() -> list[Merchant]:
    return list(MERCHANTS.values())


def get_merchant(slug: str) -> Merchant:
    return MERCHANTS[slug]
