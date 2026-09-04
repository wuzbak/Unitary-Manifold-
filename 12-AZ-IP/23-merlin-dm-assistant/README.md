# Merlin DM Guide & Player Assistant

## Product 23 of the AxiomZero suite

Merlin DM Guide & Player Assistant is an offline-first Dungeons & Dragons **5e / 5.5e** campaign system built to give Dungeon Masters and players one coherent surface for campaign tracking, character building, invite-code joins, encounter planning, grounded image prompting, and rules-aware Merlin support.

> **Scope status:** educational / gameplay support tool. This product does not make physics claims; it applies repository design rigor, structured state, and explicit source grounding to tabletop play.

---

## What ships in v1.1.0

- **Separate DM and Player dashboards** with toggled local UI views.
- **Invite-code campaign joins** so a DM can generate a code and players can join from any player dashboard.
- **Character import** from player join flow or later player-to-DM import.
- **Multiple campaign trackers** with per-campaign settings, notes, quests, layouts, encounters, maps, NPCs, and merchants.
- **Full inventory / treasure / gold / XP tracking** at DM and player surfaces.
- **Monster manual lane** with seeded encounter-ready monster records.
- **Grounded image-brief generation** plus DM image pushes to players.
- **Solo standalone player mode** when no live campaign is attached.
- **Merlin expert assistant** for table-ready summaries, rules-digest notes, and next-step prompts.

## Core API

- `GET /api/health`
- `GET /api/rules`
- `GET /api/rules?spell=fireball`
- `GET /api/monsters`
- `GET /api/merchants`
- `GET /api/campaigns`
- `POST /api/campaigns`
- `POST /api/campaigns/import`
- `GET /api/campaigns/<id>/export`
- `GET /api/campaigns/<id>/dm-dashboard`
- `GET /api/campaigns/<id>/player-dashboard?player_id=<player_id>`
- `POST /api/campaigns/<id>/invite-codes`
- `POST /api/join-campaign`
- `POST /api/campaigns/<id>/player-import`
- `POST /api/campaigns/<id>/characters`
- `POST /api/campaigns/<id>/quests`
- `POST /api/campaigns/<id>/layouts`
- `POST /api/campaigns/<id>/encounters`
- `POST /api/campaigns/<id>/inventory`
- `POST /api/campaigns/<id>/treasure`
- `POST /api/campaigns/<id>/images`
- `POST /api/campaigns/<id>/maps`
- `POST /api/campaigns/<id>/npcs`
- `POST /api/campaigns/<id>/xp`
- `POST /api/campaigns/<id>/image-brief`
- `POST /api/campaigns/<id>/merlin`
- `POST /api/player-dashboard/standalone`

## Quick start

```bash
cd 12-AZ-IP/23-merlin-dm-assistant
python run.py --port 8033
# UI: http://127.0.0.1:8033/
```

Demo mode:

```bash
python run.py demo
```

## Design notes

- **Offline-first:** no API key or third-party account is required for the baseline runtime.
- **DM / Player split:** DMs control invites, encounters, treasure, images, maps, and campaign-wide trackers; players consume those updates and can import characters into the shared campaign.
- **Rules editions:** campaign and character state can explicitly target `5e-2014` or `5e-2024`.
- **Grounded prompting:** the image brief generator pulls campaign setting, active quest, party anchor, and layout anchor into every prompt.
- **Merlin role:** Merlin is embedded as the domain expert and returns rules-aware guidance, not just a generic chatbot answer.
- **Solo use:** standalone player dashboard mode supports isolated character/inventory play without a DM host.

## File structure

- `merlin_dnd/models.py` — campaign, player, invite, inventory, treasure, map, NPC, and image dataclasses
- `merlin_dnd/rules.py` — 5e/5.5e math helpers and edition digest
- `merlin_dnd/compendium.py` — seeded monsters, merchants, and spell effects
- `merlin_dnd/service.py` — core campaign, invite, dashboard, and assistant orchestration layer
- `merlin_dnd/server.py` — standalone JSON API server
- `ui/index.html` + `ui/app.js` — toggled DM/player/solo dashboard shell
- `run.py` — local launcher
- `tests/test_merlin_dnd.py` — targeted regression suite

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
