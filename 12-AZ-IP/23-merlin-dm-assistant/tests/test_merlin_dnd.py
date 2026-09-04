# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from merlin_dnd.server import dispatch_request
from merlin_dnd.service import MerlinDndService


def _seed_campaign(service: MerlinDndService) -> str:
    campaign = service.create_campaign(
        {
            "name": "The Ember Road",
            "setting": "Ash-fall trade frontier",
            "rules_edition": "5e-2024",
            "tone": "mythic frontier",
            "summary": "Caravan routes cross old dragon roads and haunted toll keeps.",
            "merchant_slugs": ["lantern-guild-quartermaster"],
        }
    )
    service.add_character_to_campaign(
        campaign.id,
        {
            "name": "Iria",
            "species": "human",
            "klass": "wizard",
            "background": "scribe",
            "level": 5,
            "ability_scores": {
                "strength": 8,
                "dexterity": 14,
                "constitution": 14,
                "intelligence": 18,
                "wisdom": 12,
                "charisma": 10,
            },
        },
    )
    service.add_quest(
        campaign.id,
        {
            "title": "Seal the Ash Gate",
            "objective": "Close the unstable gate below the toll keep.",
            "reward": "A charter and obsidian ward-key.",
        },
    )
    service.add_layout(
        campaign.id,
        {
            "name": "Toll Keep Undercroft",
            "environment": "ruins",
            "zones": ["collapsed chapel", "gate vault", "ash cistern"],
            "hazards": ["falling masonry", "embersmoke"],
            "exits": ["front gate", "smuggler shaft"],
        },
    )
    return campaign.id


def test_character_builder_computes_spellcasting_math():
    service = MerlinDndService()
    character = service.build_character(
        {
            "name": "Mira",
            "species": "elf",
            "klass": "wizard",
            "level": 5,
            "ability_scores": {
                "strength": 8,
                "dexterity": 14,
                "constitution": 14,
                "intelligence": 18,
                "wisdom": 12,
                "charisma": 10,
            },
        }
    )
    assert character.proficiency_bonus == 3
    assert character.hit_points == 26
    assert character.spell_save_dc == 15
    assert character.spell_attack_bonus == 7


def test_multi_campaign_tracking_and_listing():
    service = MerlinDndService()
    first = service.create_campaign({"name": "First", "setting": "City"})
    second = service.create_campaign({"name": "Second", "setting": "Wilds"})
    listing = service.list_campaigns()
    assert {item["id"] for item in listing} == {first.id, second.id}


def test_export_import_round_trip_preserves_campaign_state():
    service = MerlinDndService()
    campaign_id = _seed_campaign(service)
    exported = service.export_campaign(campaign_id)

    clone = MerlinDndService()
    imported = clone.import_campaign(exported)
    assert imported.name == "The Ember Road"
    assert imported.characters[0].name == "Iria"
    assert imported.layouts[0].name == "Toll Keep Undercroft"


def test_encounter_planner_scores_difficulty():
    service = MerlinDndService()
    campaign_id = _seed_campaign(service)
    encounter = service.plan_encounter(
        campaign_id,
        {
            "title": "Gate Vault Push",
            "monster_slugs": ["owlbear", "goblin-skirmishers", "goblin-skirmishers"],
        },
    )
    assert encounter.adjusted_xp > 0
    assert encounter.difficulty in {"medium", "hard", "deadly"}


def test_image_brief_is_grounded_in_campaign_context():
    service = MerlinDndService()
    campaign_id = _seed_campaign(service)
    brief = service.build_image_brief(campaign_id, {"subject": "the party confronting the gate"})
    assert "The Ember Road" in brief.title or brief.title.endswith("image brief")
    assert "Ash-fall trade frontier" in brief.prompt
    assert "Toll Keep Undercroft" in brief.prompt


def test_monster_search_filters_by_environment_and_cr():
    service = MerlinDndService()
    monsters = service.search_monsters(environment="ruins", max_cr=1)
    assert len(monsters) == 1
    assert monsters[0]["slug"] == "goblin-skirmishers"


def test_merlin_query_returns_rules_digest_and_followups():
    service = MerlinDndService()
    campaign_id = _seed_campaign(service)
    response = service.merlin_query(campaign_id, "Prep tonight's delve")
    assert response["assistant"] == "Merlin"
    assert response["rules_digest"]
    assert len(response["followups"]) == 3


def test_dispatch_request_end_to_end_routes_campaign_api():
    status, payload = dispatch_request(
        "POST",
        "/api/campaigns",
        {
            "name": "Crown of Cinders",
            "setting": "Volcanic capital",
            "rules_edition": "5e-2024",
        },
    )
    assert status == 201
    campaign_id = payload["campaign"]["id"]

    status, payload = dispatch_request(
        "POST",
        f"/api/campaigns/{campaign_id}/merlin",
        {"prompt": "Plan the next session opener."},
    )
    assert status == 200
    assert payload["response"]["assistant"] == "Merlin"
