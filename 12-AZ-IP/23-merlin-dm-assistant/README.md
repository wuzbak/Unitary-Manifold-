# Merlin DM Guide & Player Assistant

## Product 23 of the AxiomZero suite

Merlin DM Guide & Player Assistant is an offline-first Dungeons & Dragons **5e / 5.5e** campaign system built to give Dungeon Masters and players one coherent surface for campaign tracking, character building, encounter planning, grounded image prompting, and rules-aware Merlin support.

> **Scope status:** educational / gameplay support tool. This product does not make physics claims; it applies repository design rigor, structured state, and explicit source grounding to tabletop play.

---

## What ships in v1.0.0

- **Multiple campaign trackers** with per-campaign settings, tones, notes, quests, layouts, encounters, and merchants.
- **Character creator** with level, species, class, background, HP, proficiency bonus, passive perception, and spellcasting math.
- **Import / export** as deterministic JSON bundles for campaign portability.
- **Monster manual lane** with seeded encounter-ready monster records.
- **Merchants** with specialties, inventories, and hooks.
- **Quest notes** with status and rewards.
- **Dungeon / battle layouts** with zones, hazards, exits, and lighting.
- **Grounded image-brief generation** that keeps prompts tied to campaign canon instead of generic fantasy output.
- **Merlin expert assistant** for table-ready summaries, rules-digest notes, and next-step prompts.

## Core API

- `GET /api/health`
- `GET /api/monsters`
- `GET /api/merchants`
- `GET /api/campaigns`
- `POST /api/campaigns`
- `POST /api/campaigns/import`
- `GET /api/campaigns/<id>/export`
- `POST /api/campaigns/<id>/characters`
- `POST /api/campaigns/<id>/quests`
- `POST /api/campaigns/<id>/layouts`
- `POST /api/campaigns/<id>/encounters`
- `POST /api/campaigns/<id>/image-brief`
- `POST /api/campaigns/<id>/merlin`

## Quick start

```bash
cd 12-AZ-IP/23-merlin-dm-assistant
python run.py --port 8033
```

Demo mode:

```bash
python run.py demo
```

## Design notes

- **Offline-first:** no API key or third-party account is required for the baseline runtime.
- **Rules editions:** campaign and character state can explicitly target `5e-2014` or `5e-2024`.
- **Grounded prompting:** the image brief generator pulls campaign setting, active quest, party anchor, and layout anchor into every prompt.
- **Merlin role:** Merlin is embedded as the domain expert and returns rules-aware guidance, not just a generic chatbot answer.

## File structure

- `merlin_dnd/models.py` — campaign, character, quest, layout, encounter, merchant, and image-brief dataclasses
- `merlin_dnd/rules.py` — 5e/5.5e math helpers and edition digest
- `merlin_dnd/compendium.py` — seeded monsters, merchants, and spell effects
- `merlin_dnd/service.py` — core campaign and assistant orchestration layer
- `merlin_dnd/server.py` — standalone JSON API server
- `run.py` — local launcher
- `tests/test_merlin_dnd.py` — targeted regression suite

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
