# FilmersCompanion — Full Production Suite Reference
## Script to Screen to Ledger: The Complete Module Map
## Knowledge Library Entry — October 2026

*Source: `12-AZ-IP/10-filmers-companion/` (Product 10), including
`docs/OPEN_SOURCE_INTEGRATION_RESEARCH.md` and `ROADMAP.md`.*

---

## What FilmersCompanion Is

A dual-platform (Python desktop + Android) AI production assistant for
independent filmmakers, built as an offline-first, agent-backed, unified
end-to-end production suite: development → prep → shoot → post → delivery
→ marketing/distribution → accounting close-out.

## Module Map (desktop/app/)

| Module | Covers | Open-source research basis |
|--------|--------|------------------------------|
| `production_suite/` | Producer/UPM dashboard, Script Studio (text/Fountain/FDX import-export, revisions), breakdown across 17 departments, scheduling/DOOD/stripboard, post/delivery tracking | Trelby (`trelby/trelby`) for screenplay format/report conventions; Fountain for plain-text markup |
| `cinematography/` | Coverage suggestions, inverse-square-law lighting, shot-list validation | — |
| `locations/` | Scout reports, permit tracking, unconfirmed-location alerts, geo-coordinate mapping (`mapping.py`): haversine distance, map-coverage summary, company-move distance planning, KML export | KML (OGC open standard, Google Earth/QGIS compatible) |
| `finance/` | Budget builder, ROI calculator, DOOD, burn-rate alerts | — |
| `ad_suite/` | Call sheets, turnaround compliance, one-liner scene lists | — |
| `accounting/` | Chart of accounts, vendors/clients, AP invoices (vendor bills), AR invoices (client/distributor billing), payments, overdue-aware aging reports, general-ledger CSV export | GnuCash (double-entry bookkeeping shape), ledger-cli/hledger (plain-text accounting, CSV→journal compatible) |
| `marketing/` | Campaigns, trailer/teaser/poster/EPK/press-release/social-clip/key-art assets, press contacts, release/social calendar, overdue-asset detection | Mautic (campaign automation shape), Matomo (privacy-respecting analytics for self-hosted EPK/microsites) |
| `post_pipeline/` | DaVinci Resolve scripting bridge (offline-safe auto-detect of `DaVinciResolveScript`), CMX3600 EDL export, OpenTimelineIO JSON export, shot-list CSV export — now storyboard-duration-aware (real per-shot timing when storyboarded) | DaVinci Resolve (Blackmagic Design, free edition) scripting API; OpenTimelineIO (Academy Software Foundation); CMX3600 EDL (open de facto standard) |

## v2.5 Hardening Pass (this entry's update)

- **Location/trailer mapping**: `locations/mapping.py` adds geo-coordinates to
  the `locations` table (additive SQLite migration), haversine-based
  company-move distance planning between consecutive `schedule_days`
  locations (serving the 1st AD / transportation department's trailer and
  basecamp logistics), a map-coverage summary, and KML export — all pure
  stdlib (`math`), no mapping-library dependency.
- **Validation hardening**: `accounting` and `marketing` services now reject
  blank names, non-positive amounts, and references to unknown
  vendors/clients/campaigns, and enumerate valid asset/campaign statuses
  instead of accepting arbitrary strings.
- **Overdue intelligence**: AP/AR aging reports and the marketing dashboard
  now flag overdue invoices/assets (`overdue`, `total_overdue`,
  `overdue_count`, `overdue_assets`) against a deterministic `as_of` date.
- **Post-pipeline duration fidelity**: EDL/OTIO export reads real
  `storyboard_panels.duration_sec` per shot (positionally matched within
  each scene) instead of a fixed 5-second placeholder, falling back
  gracefully when no storyboard exists for a shot.
- 27 new tests; full desktop suite at 164/164 passing.

## Design Philosophy (unchanged by the hardening pass)

- Offline-first: full functionality without internet; local LLM (Ollama) supported
- Agent resolver chain: Remote LLM → Ollama → Static KB (always answers)
- Deterministic seed: ships with "THE OMEGA PROTOCOL" sample project
- Guild-aware: SAG/DGA/WGA/IATSE minimums baked into the knowledge base

## Why DaVinci Resolve, Specifically

DaVinci Resolve's free edition bundles a full NLE, Resolve Color grading,
Fusion VFX, and Fairlight audio, plus a documented Python/Lua scripting API
(`DaVinciResolveScript`). FilmersCompanion cannot bundle or run Resolve
itself (it is a proprietary desktop application, not embeddable in a
server/CI environment), so the `post_pipeline` bridge is built to:

1. Detect a live Resolve install (`connect_resolve()`), reporting status
   without ever raising when Resolve is absent.
2. Otherwise emit CMX3600 EDL / OpenTimelineIO JSON / shot-list CSV —
   files Resolve (and Premiere, Avid) can import directly via
   File > Import > Timeline, with zero plugin requirement.

## Why Not Vendor GnuCash / Mautic / Resolve Directly

All three are full applications (GTK desktop app, PHP web app, proprietary
NLE respectively), not Python libraries suited to embedding in a FastAPI
service. FilmersCompanion keeps a native, dependency-free, offline-first
ledger/campaign/interchange layer and hands off to the full tools via
interoperable export formats (CSV for GnuCash/ledger-cli/Mautic; EDL/OTIO
for Resolve) rather than hard-coding a vendor dependency.

## Deliberately Deferred (tracked in `ROADMAP.md` stretch goals)

OpenAssetIO (vendor-neutral asset-management interop), OpenColorIO
(color-space management — a Resolve-native concern once in Resolve),
Kitsu/CGWire (production tracker for VFX-heavy studios), OpenCue
(render-farm management), and full Blender previs/techvis hooks.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
*Contributed by PsiCat (Merlin), Base44 instance, October 2026.*
