# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import http.client
import json
import sys
import threading
import time
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from merlin_dnd.server import dispatch_request, serve
from merlin_dnd.service import MerlinDndService


def _wizard_payload(name: str = "Iria") -> dict:
    return {
        "name": name,
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
    }


def _seed_campaign(service: MerlinDndService) -> str:
    campaign = service.create_campaign(
        {
            "name": "The Ember Road",
            "setting": "Ash-fall trade frontier",
            "rules_edition": "5e-2024",
            "tone": "mythic frontier",
            "summary": "Caravan routes cross old dragon roads and haunted toll keeps.",
            "merchant_slugs": ["lantern-guild-quartermaster"],
            "dm_name": "Merlin Host",
        }
    )
    service.add_character_to_campaign(campaign.id, _wizard_payload())
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
    character = service.build_character(_wizard_payload("Mira"))
    assert character.proficiency_bonus == 3
    assert character.hit_points == 32
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
    invite = service.generate_invite_code(campaign_id, {"label": "Table A"})
    service.join_campaign({"invite_code": invite.code, "display_name": "Tamsin", "character": _wizard_payload("Tamsin")})
    service.add_inventory_item(campaign_id, {"name": "Wand", "owner_type": "party", "owner_id": "party", "kind": "focus", "quantity": 1, "rarity": "uncommon"})
    exported = service.export_campaign(campaign_id)

    clone = MerlinDndService()
    imported = clone.import_campaign(exported)
    assert imported.name == "The Ember Road"
    assert imported.players[0].display_name == "Tamsin"
    assert imported.inventory[0].name == "Wand"


def test_invite_join_and_player_dashboard_flow():
    service = MerlinDndService()
    campaign_id = _seed_campaign(service)
    invite = service.generate_invite_code(campaign_id, {"label": "Table B"})
    joined = service.join_campaign({"invite_code": invite.code, "display_name": "Aster", "character": _wizard_payload("Aster")})
    player = joined["player"]
    dashboard = service.player_dashboard(campaign_id, player["id"])
    assert dashboard["mode"] == "player"
    assert dashboard["player"]["display_name"] == "Aster"
    assert dashboard["characters"][0]["player_id"] == player["id"]


def test_dm_dashboard_tracks_images_treasure_items_and_xp():
    service = MerlinDndService()
    campaign_id = _seed_campaign(service)
    campaign = service.get_campaign(campaign_id)
    character_id = campaign.characters[0].id
    service.add_inventory_item(campaign_id, {"name": "Obsidian Key", "owner_type": "party", "owner_id": "party", "kind": "quest-item", "rarity": "rare", "quantity": 1})
    service.add_treasure(campaign_id, {"title": "Vault Recovery", "gold": 125, "items": ["Ruby Seal"], "recipients": ["party"]})
    service.push_image(campaign_id, {"title": "Ash Gate", "image_url": "https://example.invalid/ash-gate.png", "audience": "all_players"})
    xp = service.award_xp(campaign_id, {"amount": 250, "character_id": character_id})
    dashboard = service.dm_dashboard(campaign_id)
    assert dashboard["summary"]["party_gold"] == 125
    assert dashboard["summary"]["inventory_count"] == 1
    assert dashboard["recent_images"][0]["title"] == "Ash Gate"
    assert xp["xp"] == 250


def test_player_dashboard_surfaces_maps_npcs_monsters_and_inventory():
    service = MerlinDndService()
    campaign_id = _seed_campaign(service)
    invite = service.generate_invite_code(campaign_id, {})
    joined = service.join_campaign({"invite_code": invite.code, "display_name": "Rook", "character": _wizard_payload("Rook")})
    player_id = joined["player"]["id"]
    character_id = joined["character"]["id"]
    service.add_map_reference(campaign_id, {"name": "Gate Map", "kind": "battlemap", "image_url": "https://example.invalid/map.png", "zones": ["vault"], "tokens": ["Rook"]})
    service.add_npc(campaign_id, {"name": "Captain Elowen", "role": "quest-giver", "location": "ash market"})
    service.add_inventory_item(campaign_id, {"name": "Spellbook", "owner_type": "character", "owner_id": character_id, "kind": "focus", "quantity": 1, "rarity": "common"})
    service.plan_encounter(campaign_id, {"title": "Bridge Ambush", "monster_slugs": ["goblin-skirmishers", "owlbear"]})
    service.push_image(campaign_id, {"title": "Bridge Vision", "image_url": "https://example.invalid/bridge.png", "audience": "all_players"})
    dashboard = service.player_dashboard(campaign_id, player_id)
    assert dashboard["maps"][0]["name"] == "Gate Map"
    assert dashboard["npcs"][0]["name"] == "Captain Elowen"
    assert dashboard["inventory"][0]["name"] == "Spellbook"
    assert len(dashboard["monsters"]) == 2
    assert dashboard["images"][0]["title"] == "Bridge Vision"


def test_standalone_player_dashboard_supports_solo_use():
    service = MerlinDndService()
    dashboard = service.standalone_player_dashboard(
        {
            "player_name": "Solo Explorer",
            "character": {
                **_wizard_payload("Nym"),
                "klass": "rogue",
                "level": 3,
                "inventory": [{"name": "Lockpicks", "owner_type": "character", "owner_id": "solo", "quantity": 1, "kind": "tool", "rarity": "common"}],
            },
        }
    )
    assert dashboard["mode"] == "standalone-player"
    assert dashboard["solo_ready"] is True
    assert dashboard["inventory"][0]["name"] == "Lockpicks"


def test_dispatch_request_end_to_end_routes_campaign_api():
    status, payload = dispatch_request(
        "POST",
        "/api/campaigns",
        {"name": "Crown of Cinders", "setting": "Volcanic capital", "rules_edition": "5e-2024"},
    )
    assert status == 201
    campaign_id = payload["campaign"]["id"]
    status, payload = dispatch_request("POST", f"/api/campaigns/{campaign_id}/invite-codes", {"label": "Open Table"})
    invite_code = payload["invite"]["code"]
    status, payload = dispatch_request(
        "POST",
        "/api/join-campaign",
        {"invite_code": invite_code, "display_name": "Sable", "character": _wizard_payload("Sable")},
    )
    player_id = payload["player"]["id"]
    status, payload = dispatch_request("GET", f"/api/campaigns/{campaign_id}/player-dashboard?player_id={player_id}")
    assert status == 200
    assert payload["player"]["display_name"] == "Sable"


def test_dispatch_request_serves_static_index():
    status, payload = dispatch_request("GET", "/")
    assert status == 200
    assert payload["content_type"] == "text/html; charset=utf-8"
    assert "DM Dashboard" in payload["body"]


def test_dispatch_request_rules_reference_endpoint():
    status, payload = dispatch_request("GET", "/api/rules?spell=fireball")
    assert status == 200
    assert payload["spell"]["fireball"].startswith("20-foot-radius explosion")
    assert "dm" in payload["dashboard_modes"]


def test_dispatch_request_rejects_non_numeric_max_cr():
    status, payload = dispatch_request("GET", "/api/monsters?max_cr=abc")
    assert status == 400
    assert payload["error"] == "Query parameter 'max_cr' must be numeric."


def test_http_handler_rejects_invalid_json_body():
    server = serve(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        time.sleep(0.05)
        conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        conn.request("POST", "/api/campaigns", body="{bad json", headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        assert response.status == 400
        assert payload["error"] == "Request body must be valid JSON."
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_http_handler_rejects_non_object_json_body():
    server = serve(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        time.sleep(0.05)
        conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        conn.request("POST", "/api/campaigns", body='["not", "an", "object"]', headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        assert response.status == 400
        assert payload["error"] == "Request body must be a JSON object."
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_dispatch_request_requires_campaign_name():
    status, payload = dispatch_request("POST", "/api/campaigns", {"setting": "Mist coast"})
    assert status == 400
    assert payload["error"] == "Missing required field: name."


def test_dispatch_request_rejects_unknown_campaign_id():
    status, payload = dispatch_request("GET", "/api/campaigns/not-real/export")
    assert status == 404
    assert payload["error"] == "Resource not found: not-real."


def test_dispatch_request_rejects_duplicate_campaign_id():
    status, payload = dispatch_request("POST", "/api/campaigns", {"id": "dup-campaign", "name": "First"})
    assert status == 201
    status, payload = dispatch_request("POST", "/api/campaigns", {"id": "dup-campaign", "name": "Second"})
    assert status == 409
    assert payload["error"] == "Campaign ID already exists: dup-campaign."


def test_dispatch_request_requires_player_dashboard_player_id():
    status, payload = dispatch_request("GET", "/api/campaigns/abc/player-dashboard")
    assert status == 400
    assert payload["error"] == "Query parameter 'player_id' is required."
