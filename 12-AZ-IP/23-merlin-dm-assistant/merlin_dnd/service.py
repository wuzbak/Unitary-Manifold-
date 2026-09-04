# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import threading
from uuid import uuid4

from .assistant import build_merlin_response
from .compendium import MONSTERS, SPELL_EFFECTS, get_merchant, get_monster, list_merchants, list_monsters
from .models import Campaign, Character, DungeonLayout, Encounter, ImageBrief, Merchant, Quest
from .rules import (
    CLASS_SPELLCASTING_ABILITY,
    ability_modifier,
    adjusted_encounter_xp,
    classify_encounter,
    encounter_thresholds,
    passive_perception,
    proficiency_bonus,
    rules_update_notes,
    spell_attack_bonus,
    spell_save_dc,
    starting_hit_points,
)


class MerlinDndService:
    """Offline-first D&D 5e/5.5e campaign and assistant service."""

    def __init__(self) -> None:
        self._campaigns: dict[str, Campaign] = {}
        self._lock = threading.RLock()

    def create_campaign(self, payload: dict) -> Campaign:
        with self._lock:
            campaign_id = str(payload.get("id") or uuid4().hex)
            if campaign_id in self._campaigns:
                raise ValueError(f"Campaign ID already exists: {campaign_id}.")
            allowed_merchant_slugs = list_merchants_by_slug()
            campaign = Campaign(
                id=campaign_id,
                name=str(payload["name"]),
                setting=str(payload.get("setting") or "Original fantasy world"),
                rules_edition=str(payload.get("rules_edition") or "5e-2024"),
                tone=str(payload.get("tone") or "heroic"),
                summary=str(payload.get("summary") or ""),
                pillars=list(payload.get("pillars") or []),
                merchants=[get_merchant(slug) for slug in payload.get("merchant_slugs", []) if slug in allowed_merchant_slugs],
                notes=list(payload.get("notes") or []),
            )
            self._campaigns[campaign.id] = campaign
            return campaign

    def list_campaigns(self) -> list[dict]:
        with self._lock:
            return [campaign.to_dict() for campaign in self._campaigns.values()]

    def get_campaign(self, campaign_id: str) -> Campaign:
        with self._lock:
            return self._campaigns[campaign_id]

    def build_character(self, payload: dict) -> Character:
        scores = {key.lower(): int(value) for key, value in payload["ability_scores"].items()}
        level = int(payload.get("level") or 1)
        klass = str(payload["klass"]).lower()
        prof = proficiency_bonus(level)
        spell_ability = CLASS_SPELLCASTING_ABILITY.get(klass)
        character = Character(
            id=str(payload.get("id") or uuid4().hex),
            name=str(payload["name"]),
            species=str(payload.get("species") or "human"),
            klass=klass,
            background=str(payload.get("background") or "wanderer"),
            level=level,
            rules_edition=str(payload.get("rules_edition") or "5e-2024"),
            alignment=str(payload.get("alignment") or "unaligned"),
            ability_scores=scores,
            proficiency_bonus=prof,
            hit_points=starting_hit_points(klass, level, scores.get("constitution", 10)),
            armor_class=int(payload.get("armor_class") or (10 + ability_modifier(scores.get("dexterity", 10)))),
            passive_perception=passive_perception(scores.get("wisdom", 10), prof, bool(payload.get("perception_proficient", True))),
            spellcasting_ability=spell_ability,
            spell_save_dc=(spell_save_dc(prof, scores[spell_ability]) if spell_ability else None),
            spell_attack_bonus=(spell_attack_bonus(prof, scores[spell_ability]) if spell_ability else None),
            notes=list(payload.get("notes") or []),
        )
        return character

    def add_character_to_campaign(self, campaign_id: str, payload: dict) -> Character:
        with self._lock:
            character = self.build_character(payload)
            self._campaigns[campaign_id].characters.append(character)
            return character

    def add_quest(self, campaign_id: str, payload: dict) -> Quest:
        with self._lock:
            quest = Quest(
                id=str(payload.get("id") or uuid4().hex),
                title=str(payload["title"]),
                status=str(payload.get("status") or "active"),
                objective=str(payload.get("objective") or ""),
                reward=str(payload.get("reward") or ""),
                notes=list(payload.get("notes") or []),
            )
            self._campaigns[campaign_id].quests.append(quest)
            return quest

    def add_layout(self, campaign_id: str, payload: dict) -> DungeonLayout:
        with self._lock:
            layout = DungeonLayout(
                id=str(payload.get("id") or uuid4().hex),
                name=str(payload["name"]),
                environment=str(payload.get("environment") or "dungeon"),
                zones=list(payload.get("zones") or []),
                hazards=list(payload.get("hazards") or []),
                exits=list(payload.get("exits") or []),
                lighting=str(payload.get("lighting") or "mixed torchlight"),
            )
            self._campaigns[campaign_id].layouts.append(layout)
            return layout

    def plan_encounter(self, campaign_id: str, payload: dict) -> Encounter:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            monster_slugs = [slug for slug in payload.get("monster_slugs", []) if slug in MONSTERS]
            monsters = [get_monster(slug) for slug in monster_slugs]
            base_xp = sum(monster.xp for monster in monsters)
            levels = [character.level for character in campaign.characters] or [1]
            adjusted_xp = adjusted_encounter_xp(base_xp, len(monsters) or 1)
            difficulty = classify_encounter(adjusted_xp, encounter_thresholds(levels))
            encounter = Encounter(
                id=str(payload.get("id") or uuid4().hex),
                title=str(payload.get("title") or "Encounter"),
                monster_slugs=monster_slugs,
                adjusted_xp=adjusted_xp,
                difficulty=difficulty,
                battlefield_notes=list(payload.get("battlefield_notes") or [monster.environment for monster in monsters]),
            )
            campaign.encounters.append(encounter)
            return encounter

    def build_image_brief(self, campaign_id: str, payload: dict) -> ImageBrief:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            anchor_character = campaign.characters[0].name if campaign.characters else "the party"
            anchor_layout = campaign.layouts[0].name if campaign.layouts else "the active dungeon"
            anchor_quest = campaign.quests[0].title if campaign.quests else "the current objective"
            prompt = (
                f"{campaign.setting}; tone={campaign.tone}; subject={payload.get('subject', 'party scene')}; "
                f"anchor character={anchor_character}; anchor quest={anchor_quest}; layout={anchor_layout}; "
                f"preserve gear continuity, spell effects, heraldry, and environmental storytelling."
            )
            negative = "generic fantasy collage, contradictory gear, wrong species count, modern props, inconsistent lighting"
            return ImageBrief(
                title=str(payload.get("title") or f"{campaign.name} image brief"),
                prompt=prompt,
                negative_prompt=negative,
                anchors={
                    "campaign": campaign.name,
                    "rules_edition": campaign.rules_edition,
                    "setting": campaign.setting,
                    "party_size": len(campaign.characters),
                },
            )

    def export_campaign(self, campaign_id: str) -> dict:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            return {
                "product": "Merlin DM Guide & Player Assistant",
                "version": "1.0.0",
                "campaign": campaign.to_dict(),
                "rules_update_notes": rules_update_notes(campaign.rules_edition),
            }

    def import_campaign(self, payload: dict) -> Campaign:
        with self._lock:
            data = payload["campaign"]
            campaign_id = str(data["id"])
            if campaign_id in self._campaigns:
                raise ValueError(f"Campaign ID already exists: {campaign_id}.")
            campaign = self._campaign_from_dict(data)
            self._campaigns[campaign.id] = campaign
            return campaign

    def merlin_query(self, campaign_id: str, prompt: str) -> dict:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            return build_merlin_response(campaign.to_dict(), prompt)

    def search_monsters(self, *, environment: str | None = None, max_cr: float | None = None) -> list[dict]:
        return [monster.to_dict() for monster in list_monsters(environment=environment, max_cr=max_cr)]

    def list_merchants(self) -> list[dict]:
        return [merchant.to_dict() for merchant in list_merchants()]

    def rules_reference(self, spell_name: str | None = None) -> dict:
        reference = {
            "spells": SPELL_EFFECTS,
            "supported_rules_editions": ["5e-2014", "5e-2024"],
        }
        if spell_name:
            reference["spell"] = {spell_name: SPELL_EFFECTS.get(spell_name.lower())}
        return reference

    def _campaign_from_dict(self, data: dict) -> Campaign:
        return Campaign(
            id=str(data["id"]),
            name=str(data["name"]),
            setting=str(data.get("setting") or "Original fantasy world"),
            rules_edition=str(data.get("rules_edition") or "5e-2024"),
            tone=str(data.get("tone") or "heroic"),
            summary=str(data.get("summary") or ""),
            pillars=list(data.get("pillars") or []),
            characters=[Character(**item) for item in data.get("characters", [])],
            quests=[Quest(**item) for item in data.get("quests", [])],
            layouts=[DungeonLayout(**item) for item in data.get("layouts", [])],
            encounters=[Encounter(**item) for item in data.get("encounters", [])],
            merchants=[Merchant(**item) for item in data.get("merchants", [])],
            notes=list(data.get("notes") or []),
        )


def list_merchants_by_slug() -> set[str]:
    return {merchant.slug for merchant in list_merchants()}
