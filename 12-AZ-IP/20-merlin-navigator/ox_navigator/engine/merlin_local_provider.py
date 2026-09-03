# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Self-hosted local Merlin provider (primary runtime lane)."""

from __future__ import annotations

from typing import Any


def generate_local_response(
    *,
    query: str,
    context: dict[str, Any],
    persona_mode: str,
    fourth_wall: bool,
) -> dict[str, Any]:
    """Generate a deterministic local response candidate without external providers."""
    kb_match = context.get("kb_match")
    pillars = list(context.get("pillars") or [])
    confidence = 0.35
    if kb_match:
        gate = kb_match.get("status", "ARCHITECTURE_LIMIT")
        body = f"Direct answer: {kb_match.get('answer', '').strip()} [{gate}]"
        confidence = 0.86
    elif pillars:
        pillar = pillars[0]
        body = (
            "Not found in framework context. "
            f"Closest relevant pillar: [{pillar['gate']}] "
            f"Pillar {pillar['id']} — {pillar['name']}. {pillar['text']}"
        )
        confidence = 0.62
    else:
        body = "Not found in framework context. Merlin does not have a grounded answer for that yet."

    if persona_mode != "serious":
        body = body.replace("Direct answer:", "Merlin short answer:")
    normalized_query = str(query or "").lower()
    if "litebird" in normalized_query or "falsif" in normalized_query:
        if "[OPEN_GAP]" not in body:
            body += " [OPEN_GAP] LiteBIRD is the primary observational falsifier lane and remains pending."
    if fourth_wall:
        body += "\n\n[Fourth wall] Gate badges are confidence-status labels, not decoration."
    return {
        "provider": "sovereign_local_model",
        "body": body,
        "confidence": round(confidence, 3),
    }
