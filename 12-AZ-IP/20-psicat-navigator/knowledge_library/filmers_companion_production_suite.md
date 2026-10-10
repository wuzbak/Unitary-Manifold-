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
| `locations/` | Scout reports, permit tracking, unconfirmed-location alerts | — |
| `finance/` | Budget builder, ROI calculator, DOOD, burn-rate alerts | — |
| `ad_suite/` | Call sheets, turnaround compliance, one-liner scene lists | — |
| `accounting/` **(new)** | Chart of accounts, vendors/clients, AP invoices (vendor bills), AR invoices (client/distributor billing), payments, aging reports, general-ledger CSV export | GnuCash (double-entry bookkeeping shape), ledger-cli/hledger (plain-text accounting, CSV→journal compatible) |
| `marketing/` **(new)** | Campaigns, trailer/teaser/poster/EPK/press-release/social-clip/key-art assets, press contacts, release/social calendar | Mautic (campaign automation shape), Matomo (privacy-respecting analytics for self-hosted EPK/microsites) |
| `post_pipeline/` **(new)** | DaVinci Resolve scripting bridge (offline-safe auto-detect of `DaVinciResolveScript`), CMX3600 EDL export, OpenTimelineIO JSON export, shot-list CSV export | DaVinci Resolve (Blackmagic Design, free edition) scripting API; OpenTimelineIO (Academy Software Foundation); CMX3600 EDL (open de facto standard) |

## Design Philosophy (unchanged by the v2.4 pass)

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
