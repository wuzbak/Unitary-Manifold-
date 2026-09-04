# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import secrets
import string
import threading
from uuid import uuid4

from .assistant import build_merlin_response
from .compendium import MONSTERS, SPELL_EFFECTS, get_merchant, get_monster, list_merchants, list_monsters
from .models import (
    Campaign,
    Character,
    DungeonLayout,
    Encounter,
    ImageBrief,
    InventoryItem,
    InviteCode,
    MapReference,
    Merchant,
    Npc,
    PlayerProfile,
    Quest,
    SharedImage,
    TreasureEntry,
)
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
                dm_name=str(payload.get("dm_name") or "Dungeon Master"),
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
        inventory = [self._inventory_from_dict(item) for item in payload.get("inventory", [])]
        return Character(
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
            player_id=str(payload.get("player_id")) if payload.get("player_id") else None,
            xp=int(payload.get("xp") or 0),
            gold=int(payload.get("gold") or 0),
            abilities=list(payload.get("abilities") or []),
            conditions=list(payload.get("conditions") or []),
            inventory=inventory,
            notes=list(payload.get("notes") or []),
        )

    def add_character_to_campaign(self, campaign_id: str, payload: dict) -> Character:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            character = self.build_character(payload)
            campaign.characters.append(character)
            if character.player_id:
                player = self._find_player(campaign, character.player_id)
                player.character_ids.append(character.id)
            return character

    def add_quest(self, campaign_id: str, payload: dict) -> Quest:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            quest = Quest(
                id=str(payload.get("id") or uuid4().hex),
                title=str(payload["title"]),
                status=str(payload.get("status") or "active"),
                objective=str(payload.get("objective") or ""),
                reward=str(payload.get("reward") or ""),
                notes=list(payload.get("notes") or []),
            )
            campaign.quests.append(quest)
            return quest

    def add_layout(self, campaign_id: str, payload: dict) -> DungeonLayout:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            layout = DungeonLayout(
                id=str(payload.get("id") or uuid4().hex),
                name=str(payload["name"]),
                environment=str(payload.get("environment") or "dungeon"),
                zones=list(payload.get("zones") or []),
                hazards=list(payload.get("hazards") or []),
                exits=list(payload.get("exits") or []),
                lighting=str(payload.get("lighting") or "mixed torchlight"),
            )
            campaign.layouts.append(layout)
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
                "version": "1.1.0",
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

    def generate_invite_code(self, campaign_id: str, payload: dict) -> InviteCode:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            code = str(payload.get("code") or self._new_invite_code())
            invite = InviteCode(
                code=code,
                role=str(payload.get("role") or "player"),
                status="active",
                created_by=str(payload.get("created_by") or campaign.dm_name),
                label=str(payload.get("label") or campaign.name),
            )
            campaign.active_invites.append(invite)
            return invite

    def join_campaign(self, payload: dict) -> dict:
        with self._lock:
            invite_code = str(payload["invite_code"]).upper()
            display_name = str(payload["display_name"])
            campaign = self._find_campaign_by_invite(invite_code)
            player = PlayerProfile(
                id=str(payload.get("player_id") or uuid4().hex),
                display_name=display_name,
                campaign_id=campaign.id,
                invite_code=invite_code,
                notes=list(payload.get("notes") or []),
            )
            campaign.players.append(player)
            imported_character = None
            if isinstance(payload.get("character"), dict):
                imported_payload = dict(payload["character"])
                imported_payload["player_id"] = player.id
                imported_character = self.add_character_to_campaign(campaign.id, imported_payload)
            return {
                "campaign": campaign.to_dict(),
                "player": player.to_dict(),
                "character": imported_character.to_dict() if imported_character else None,
            }

    def import_player_character(self, campaign_id: str, player_id: str, payload: dict) -> Character:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            self._find_player(campaign, player_id)
            imported_payload = dict(payload)
            imported_payload["player_id"] = player_id
            return self.add_character_to_campaign(campaign_id, imported_payload)

    def add_inventory_item(self, campaign_id: str, payload: dict) -> InventoryItem:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            item = self._inventory_from_dict(payload)
            campaign.inventory.append(item)
            if item.owner_type == "character":
                self._find_character(campaign, item.owner_id).inventory.append(item)
            return item

    def add_treasure(self, campaign_id: str, payload: dict) -> TreasureEntry:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            treasure = TreasureEntry(
                id=str(payload.get("id") or uuid4().hex),
                title=str(payload["title"]),
                gold=int(payload.get("gold") or 0),
                items=list(payload.get("items") or []),
                recipients=list(payload.get("recipients") or ["party"]),
                notes=list(payload.get("notes") or []),
            )
            campaign.treasure_log.append(treasure)
            campaign.party_gold += treasure.gold
            return treasure

    def award_xp(self, campaign_id: str, payload: dict) -> dict:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            amount = int(payload["amount"])
            campaign.party_xp_total += amount
            target_character_id = str(payload.get("character_id") or "")
            if target_character_id:
                character = self._find_character(campaign, target_character_id)
                character.xp += amount
                return {"campaign_id": campaign_id, "character_id": character.id, "xp": character.xp, "party_xp_total": campaign.party_xp_total}
            for player_id in payload.get("player_ids", []):
                player = self._find_player(campaign, str(player_id))
                for character_id in player.character_ids:
                    self._find_character(campaign, character_id).xp += amount
            return {"campaign_id": campaign_id, "party_xp_total": campaign.party_xp_total}

    def push_image(self, campaign_id: str, payload: dict) -> SharedImage:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            image = SharedImage(
                id=str(payload.get("id") or uuid4().hex),
                title=str(payload["title"]),
                image_url=str(payload["image_url"]),
                caption=str(payload.get("caption") or ""),
                audience=str(payload.get("audience") or "all_players"),
                tags=list(payload.get("tags") or []),
            )
            campaign.shared_images.append(image)
            return image

    def add_npc(self, campaign_id: str, payload: dict) -> Npc:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            npc = Npc(
                id=str(payload.get("id") or uuid4().hex),
                name=str(payload["name"]),
                role=str(payload.get("role") or "contact"),
                location=str(payload.get("location") or "unknown"),
                attitude=str(payload.get("attitude") or "neutral"),
                notes=list(payload.get("notes") or []),
            )
            campaign.npcs.append(npc)
            return npc

    def add_map_reference(self, campaign_id: str, payload: dict) -> MapReference:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            reference = MapReference(
                id=str(payload.get("id") or uuid4().hex),
                name=str(payload["name"]),
                kind=str(payload.get("kind") or "environment"),
                image_url=str(payload["image_url"]),
                fog_of_war=bool(payload.get("fog_of_war", False)),
                zones=list(payload.get("zones") or []),
                tokens=list(payload.get("tokens") or []),
            )
            campaign.maps.append(reference)
            return reference

    def dm_dashboard(self, campaign_id: str) -> dict:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            return {
                "mode": "dm",
                "campaign": campaign.to_dict(),
                "summary": {
                    "player_count": len(campaign.players),
                    "character_count": len(campaign.characters),
                    "encounter_count": len(campaign.encounters),
                    "quest_count": len(campaign.quests),
                    "inventory_count": len(campaign.inventory),
                    "party_gold": campaign.party_gold,
                    "party_xp_total": campaign.party_xp_total,
                },
                "active_invite_codes": [invite.to_dict() for invite in campaign.active_invites if invite.status == "active"],
                "recent_images": [image.to_dict() for image in campaign.shared_images[-5:]],
                "click_targets": {
                    "players": [player.to_dict() for player in campaign.players],
                    "party_members": [character.to_dict() for character in campaign.characters],
                    "maps": [reference.to_dict() for reference in campaign.maps],
                    "items": [item.to_dict() for item in campaign.inventory],
                    "monsters": [get_monster(slug).to_dict() for encounter in campaign.encounters for slug in encounter.monster_slugs],
                    "npcs": [npc.to_dict() for npc in campaign.npcs],
                },
            }

    def player_dashboard(self, campaign_id: str, player_id: str) -> dict:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            player = self._find_player(campaign, player_id)
            player_characters = [character for character in campaign.characters if character.player_id == player_id]
            visible_images = [image.to_dict() for image in campaign.shared_images if image.audience in {"all_players", player_id, "party"}]
            visible_inventory = [item.to_dict() for item in campaign.inventory if item.owner_type == "party" or item.owner_id in player.character_ids or item.owner_id == player_id]
            return {
                "mode": "player",
                "campaign": {
                    "id": campaign.id,
                    "name": campaign.name,
                    "setting": campaign.setting,
                    "rules_edition": campaign.rules_edition,
                    "tone": campaign.tone,
                    "summary": campaign.summary,
                },
                "player": player.to_dict(),
                "characters": [character.to_dict() for character in player_characters],
                "party_members": [character.to_dict() for character in campaign.characters],
                "quests": [quest.to_dict() for quest in campaign.quests],
                "maps": [reference.to_dict() for reference in campaign.maps],
                "images": visible_images,
                "inventory": visible_inventory,
                "npcs": [npc.to_dict() for npc in campaign.npcs],
                "monsters": [get_monster(slug).to_dict() for encounter in campaign.encounters for slug in encounter.monster_slugs],
                "treasure": [entry.to_dict() for entry in campaign.treasure_log],
            }

    def standalone_player_dashboard(self, payload: dict) -> dict:
        character = self.build_character(payload["character"])
        return {
            "mode": "standalone-player",
            "campaign": None,
            "player_name": str(payload.get("player_name") or character.name),
            "characters": [character.to_dict()],
            "inventory": [item.to_dict() for item in character.inventory],
            "rules_update_notes": rules_update_notes(character.rules_edition),
            "solo_ready": True,
        }

    def merlin_query(self, campaign_id: str, prompt: str) -> dict:
        with self._lock:
            campaign = self._campaigns[campaign_id]
            response = build_merlin_response(campaign.to_dict(), prompt)
            response["dashboards"] = {
                "dm": f"/api/campaigns/{campaign_id}/dm-dashboard",
                "player": f"/api/campaigns/{campaign_id}/player-dashboard",
            }
            return response

    def search_monsters(self, *, environment: str | None = None, max_cr: float | None = None) -> list[dict]:
        return [monster.to_dict() for monster in list_monsters(environment=environment, max_cr=max_cr)]

    def list_merchants(self) -> list[dict]:
        return [merchant.to_dict() for merchant in list_merchants()]

    def rules_reference(self, spell_name: str | None = None) -> dict:
        reference = {
            "spells": SPELL_EFFECTS,
            "supported_rules_editions": ["5e-2014", "5e-2024"],
            "dashboard_modes": ["dm", "player", "standalone-player"],
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
            dm_name=str(data.get("dm_name") or "Dungeon Master"),
            characters=[self._character_from_dict(item) for item in data.get("characters", [])],
            players=[PlayerProfile(**item) for item in data.get("players", [])],
            quests=[Quest(**item) for item in data.get("quests", [])],
            layouts=[DungeonLayout(**item) for item in data.get("layouts", [])],
            encounters=[Encounter(**item) for item in data.get("encounters", [])],
            merchants=[Merchant(**item) for item in data.get("merchants", [])],
            inventory=[self._inventory_from_dict(item) for item in data.get("inventory", [])],
            treasure_log=[TreasureEntry(**item) for item in data.get("treasure_log", [])],
            shared_images=[SharedImage(**item) for item in data.get("shared_images", [])],
            npcs=[Npc(**item) for item in data.get("npcs", [])],
            maps=[MapReference(**item) for item in data.get("maps", [])],
            active_invites=[InviteCode(**item) for item in data.get("active_invites", [])],
            notes=list(data.get("notes") or []),
            party_gold=int(data.get("party_gold") or 0),
            party_xp_total=int(data.get("party_xp_total") or 0),
        )

    def _character_from_dict(self, data: dict) -> Character:
        return Character(
            id=str(data["id"]),
            name=str(data["name"]),
            species=str(data.get("species") or "human"),
            klass=str(data["klass"]),
            background=str(data.get("background") or "wanderer"),
            level=int(data.get("level") or 1),
            rules_edition=str(data.get("rules_edition") or "5e-2024"),
            alignment=str(data.get("alignment") or "unaligned"),
            ability_scores={str(key): int(value) for key, value in data.get("ability_scores", {}).items()},
            proficiency_bonus=int(data.get("proficiency_bonus") or 2),
            hit_points=int(data.get("hit_points") or 1),
            armor_class=int(data.get("armor_class") or 10),
            passive_perception=int(data.get("passive_perception") or 10),
            spellcasting_ability=data.get("spellcasting_ability"),
            spell_save_dc=data.get("spell_save_dc"),
            spell_attack_bonus=data.get("spell_attack_bonus"),
            player_id=data.get("player_id"),
            xp=int(data.get("xp") or 0),
            gold=int(data.get("gold") or 0),
            abilities=list(data.get("abilities") or []),
            conditions=list(data.get("conditions") or []),
            inventory=[self._inventory_from_dict(item) for item in data.get("inventory", [])],
            notes=list(data.get("notes") or []),
        )

    def _inventory_from_dict(self, data: dict) -> InventoryItem:
        return InventoryItem(
            id=str(data.get("id") or uuid4().hex),
            name=str(data["name"]),
            kind=str(data.get("kind") or "gear"),
            quantity=int(data.get("quantity") or 1),
            rarity=str(data.get("rarity") or "common"),
            owner_type=str(data.get("owner_type") or "party"),
            owner_id=str(data.get("owner_id") or "party"),
            description=str(data.get("description") or ""),
            attunement_required=bool(data.get("attunement_required", False)),
            equipped=bool(data.get("equipped", False)),
        )

    def _find_campaign_by_invite(self, invite_code: str) -> Campaign:
        for campaign in self._campaigns.values():
            for invite in campaign.active_invites:
                if invite.code == invite_code and invite.status == "active":
                    return campaign
        raise KeyError(invite_code)

    def _find_player(self, campaign: Campaign, player_id: str) -> PlayerProfile:
        for player in campaign.players:
            if player.id == player_id:
                return player
        raise KeyError(player_id)

    def _find_character(self, campaign: Campaign, character_id: str) -> Character:
        for character in campaign.characters:
            if character.id == character_id:
                return character
        raise KeyError(character_id)

    def _new_invite_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(secrets.choice(alphabet) for _ in range(8))
            if not any(code == invite.code for campaign in self._campaigns.values() for invite in campaign.active_invites):
                return code


def list_merchants_by_slug() -> set[str]:
    return {merchant.slug for merchant in list_merchants()}
