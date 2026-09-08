# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from .rules import rules_update_notes


def build_merlin_response(campaign: dict, prompt: str) -> dict:
    notes = rules_update_notes(campaign["rules_edition"])
    active_quests = [quest for quest in campaign["quests"] if quest["status"] != "completed"]
    primary_layout = campaign["layouts"][0]["name"] if campaign["layouts"] else "unmapped frontier"
    answer = (
        f"Merlin recommends running '{campaign['name']}' as a {campaign['tone']} {campaign['setting']} campaign. "
        f"Current focus: {len(active_quests)} active quest(s), {len(campaign['characters'])} tracked character(s), "
        f"and the lead battlefield/dungeon anchor '{primary_layout}'. "
        f"Prompt received: {prompt.strip() or 'general table support'}."
    )
    return {
        "assistant": "Merlin",
        "answer": answer,
        "rules_digest": notes,
        "followups": [
            "Confirm whether the next session is travel, intrigue, or battle heavy.",
            "Lock a quest objective and one meaningful complication before generating encounter text.",
            "Use the image brief output to keep scenes, gear, and lighting tied to campaign canon.",
        ],
        "sources": [
            "5e/5.5e campaign registry",
            f"rules edition: {campaign['rules_edition']}",
            "Merlin DM Guide product-local compendium",
        ],
    }
