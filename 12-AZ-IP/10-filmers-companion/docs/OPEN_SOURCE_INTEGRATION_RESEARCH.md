# OPEN_SOURCE_INTEGRATION_RESEARCH.md — FilmersCompanion

> Exhaustive survey of free / public-domain / open-source film-production
> tooling, mapped to FilmersCompanion's module architecture. Each entry
> states **what** it is, **why** it matters, and **how** it integrates (or
> why it was deliberately not vendored as a hard dependency).

This document is the product of the "ultimate filmmaker's production
suite" research pass: covering script writing and breakdown, shot lists,
location and trailer mapping, full department support, accounting,
marketing, accounts payable/receivable, and DaVinci Resolve-centric post.

---

## 1. Already integrated (prior to this pass)

| Area | Tool researched | Status |
|------|------------------|--------|
| Screenwriting interchange | [Trelby](https://github.com/trelby/trelby) | Format/report research basis for Fountain/FDX import-export, scene/character/location reports — see `TRELBY_CAPABILITY_PACKET` in `production_suite/service.py` |
| Screenplay markup | [Fountain](https://fountain.io) (open, public-domain-spirited plain-text screenplay spec) | Implemented: `import_script_fountain` / `export_script_fountain` |
| Final Draft interchange | FDX (Final Draft XML) | Implemented: `import_script_fdx` / `export_script_fdx` (XML is an open, documented schema even though Final Draft itself is commercial) |

## 2. Newly researched and integrated (this pass)

### 2.1 Accounting / bookkeeping (chart of accounts, AP/AR)

| Tool | What | Why | Integration |
|------|------|-----|--------------|
| **GnuCash** (`Gnucash/gnucash`) | Free, open-source, double-entry personal/small-business accounting (GTK desktop app, `libgnucash` engine, CLI). Multi-currency, invoicing, reports, QIF/OFX import. | Most mature FOSS alternative to QuickBooks; widely used by indie productions that can't justify SaaS accounting fees. | FilmersCompanion's new `accounting` module provides a lightweight chart of accounts + AP/AR ledger that **exports** (`export_general_ledger_csv`) into a GnuCash/QIF-importable CSV, rather than vendoring GnuCash's GTK/engine stack (which has no stable pure-Python API and is a desktop app, not a library). |
| **ledger-cli / hledger** (`ledger/ledger`, `simonmichael/hledger`) | Plain-text, double-entry accounting read/written as human-readable journals; fully scriptable, diffable in git. | Plain-text accounting fits a repo-first production workflow — ledgers can live alongside the project and be code-reviewed. | The same CSV export is 1:1 convertible into a ledger-cli journal (date / account / amount columns map directly); documented in `LEDGER_CLI_CAPABILITY_PACKET`. |
| **Wave / Akaunting-style AP/AR concepts** | Invoice → payment → aging-report pattern. | Standard indie-production bookkeeping shape (vendor bills payable, client/distributor invoices receivable, partial payments, aging). | Implemented directly as `ap_invoices` / `ar_invoices` / `payments` tables and `ap_aging_report()` / `ar_aging_report()` in `accounting/service.py`. |

**Why not vendor GnuCash/ledger-cli directly:** both are full applications/binaries (GTK app; C++/Haskell CLIs), not Python libraries suited to embedding in a FastAPI service. The chosen approach — a native lightweight AP/AR ledger with interoperable CSV export — keeps FilmersCompanion dependency-free and offline-first while still handing off to full bookkeeping tools for tax/payroll compliance.

### 2.2 Marketing / distribution / accounts receivable support

| Tool | What | Why | Integration |
|------|------|-----|--------------|
| **Mautic** (`mautic/mautic`) | Free, open-source marketing automation: email campaigns, landing pages, contact segmentation. | FOSS alternative to HubSpot/Mailchimp for festival outreach, audience building, distributor/press communication. | `marketing_campaigns` rows map 1:1 onto Mautic campaigns; `press_contacts` exports as a segment list for Mautic contact import (`MAUTIC_CAPABILITY_PACKET`). |
| **Matomo** (`matomo-org/matomo`) | Free, open-source, privacy-respecting web analytics (self-hostable GA alternative). | Tracks trailer/landing-page/EPK engagement without third-party data sharing — important for indie productions self-hosting a film microsite. | Each `marketing_campaigns` row can carry a Matomo site ID to correlate engagement with release windows (`MATOMO_CAPABILITY_PACKET`). |

New `marketing` module: campaigns, deliverable assets (trailer/teaser/poster/EPK/press-release/social-clip/key-art), press contacts, and a release/social calendar (`marketing/service.py`).

### 2.3 Post-production pipeline, color, and NLE interchange

| Tool | What | Why | Integration |
|------|------|-----|--------------|
| **DaVinci Resolve (Blackmagic Design) — free edition** | Industry-standard, free, full NLE + color grading (Resolve Color) + Fusion VFX + Fairlight audio. Ships a documented Python/Lua scripting API (`DaVinciResolveScript`). | This is the tool explicitly named in the brief ("use of Black Magic DaVinci Design"). Free edition scripting is sufficient for bin/timeline automation. | New `post_pipeline` module: `connect_resolve()` auto-detects `DaVinciResolveScript` on `PYTHONPATH` (set by the Resolve installer) and reports a live connection when run on a machine with Resolve installed; otherwise degrades to file-based interchange — never raises in a server/CI environment with no Resolve present. |
| **OpenTimelineIO** (`AcademySoftwareFoundation/OpenTimelineIO`) | Academy Software Foundation open-source editorial-timeline interchange format, with adapters for Resolve, Premiere, Final Cut, Avid, Nuke. | The de facto FOSS standard for cross-NLE conform — avoids one-off format lock-in. | `export_otio_json()` emits a minimal OTIO-schema-compatible timeline JSON built from the shot list; full adapter chains available via `pip install opentimelineio` + `otiotool` downstream. |
| **CMX3600 EDL** | Universally supported plain-text edit-decision-list format (SMPTE/CMX lineage, open de facto standard). | Importable by Resolve, Premiere, and Avid without any plugin — the most portable interchange available. | `export_edl()` renders the scheduled shot list as a conformed CMX3600 EDL with synthetic non-drop-frame timecodes. |

**Why not vendor DaVinci Resolve itself:** Resolve is a proprietary (though free-to-use) Blackmagic Design application; it cannot be bundled or run headless inside this repository/CI. The bridge is deliberately **optional and offline-safe**: it detects a live Resolve install when present and otherwise produces the EDL/CSV/OTIO files Resolve can import directly.

### 2.4 Location / trailer / basecamp mapping (added in the v2.5 hardening pass)

| Tool/format | What | Why | Integration |
|------|------|-----|--------------|
| **KML** (Keyhole Markup Language, OGC open standard) | Open, documented XML schema for geographic placemarks; readable by Google Earth, Google Maps, QGIS, and most GIS tooling. | "Location and trailer mapping" from the original brief covers both scouted shoot locations and production-trailer/basecamp logistics (company moves between locations). KML is free/open and needs no account or API key, consistent with the offline-first mandate. | `locations/mapping.py` adds `latitude`/`longitude`/`basecamp_notes` columns to `locations` (additive SQLite migration) and `export_kml()` renders mapped locations as a KML placemark document. |
| **Haversine great-circle distance** (public-domain formula) | Pure-math distance between two lat/lng points on a sphere. | No geocoding/mapping library dependency needed for company-move distance planning — just stdlib `math`. | `haversine_km()` computes point-to-point distance; `company_move_plan()` chains it across consecutive `schedule_days` locations so the 1st AD / transportation department can see mileage (and missing-coordinate gaps) per company move. |

## 3. Reviewed and deliberately deferred (stretch goals, tracked in `ROADMAP.md`)

| Tool | What | Why deferred |
|------|------|----------------|
| **OpenAssetIO** (`OpenAssetIO/OpenAssetIO`) | Open, vendor-neutral asset-management interop API (ASWF). | Valuable for VFX/asset pipeline at a scale (multi-vendor DAM, shot-level asset tracking) beyond the current single-SQLite-file production model; tracked as a stretch goal. |
| **OpenColorIO** (`AcademySoftwareFoundation/OpenColorIO`) | Open, ASWF color-management library used throughout VFX/post (including inside Resolve/Nuke). | Color-space management is a Resolve-native concern once a project is inside Resolve; no FilmersCompanion-side config needed yet. |
| **Kitsu / CGWire** (`cgwire/kitsu`) | Open-source production tracker (shots, tasks, versions) for animation/VFX studios. | FilmersCompanion's own breakdown/department/schedule/post modules already cover this surface for live-action indie production; Kitsu integration would be relevant if/when a VFX-heavy pipeline needs shot-level review tooling beyond `assets`/`reviews`. |
| **OpenCue** (`AcademySoftwareFoundation/OpenCue`) | Open-source render-farm management (originally Sony Pictures Imageworks). | Only relevant once CG/VFX rendering at scale is part of the pipeline; noted for future `src/quantum`-adjacent or VFX-heavy productions. |
| **Blender** | Free/open-source 3D, VFX compositor, and previs tool. | Already called out as a stretch goal in `ROADMAP.md` ("Blender / previs / techvis hooks"); unchanged by this pass. |

## 4. Summary of new FilmersCompanion capability surface

- `desktop/app/accounting/` — chart of accounts, vendors, clients, AP/AR invoices, payments, aging reports, general-ledger CSV export (GnuCash/ledger-cli compatible).
- `desktop/app/marketing/` — campaigns, marketing/distribution assets (trailer, poster, EPK, press-release, social-clip, key-art, BTS), press contacts, release/social calendar.
- `desktop/app/post_pipeline/` — DaVinci Resolve scripting bridge (offline-safe auto-detect), CMX3600 EDL export, OpenTimelineIO JSON export, shot-list CSV export, export history.
- `desktop/app/locations/mapping.py` — geo-coordinates on locations, haversine company-move distance planning, map-coverage summary, KML export.

All modules follow the existing FilmersCompanion conventions: a `service.py` with a plain class operating over the shared SQLite schema (`db/schema.py`), a thin FastAPI `router.py` mounted under `/api`, and dedicated pytest coverage in `desktop/tests/`.

## 5. v2.5 hardening pass — validation and overdue intelligence

Beyond adding new surface area, this pass tightened the modules shipped in
v2.4 so they fail loudly instead of silently accepting bad data:

- `accounting/service.py` now rejects blank vendor/client names, non-positive
  invoice/payment amounts, and invoices referencing unknown vendors/clients;
  AP/AR aging reports accept a deterministic `as_of` date and flag overdue
  invoices (`overdue`, `total_overdue`, `overdue_count`).
- `marketing/service.py` now validates `asset_type` and campaign/asset
  `status` against explicit enumerations, rejects assets referencing unknown
  campaigns, and the marketing dashboard flags overdue (past-due,
  not-yet-delivered) assets.
- `post_pipeline/service.py` EDL/OTIO export now reads real
  `storyboard_panels.duration_sec` per shot (positionally matched within
  each scene) instead of a fixed 5-second placeholder, so cut timing
  reflects actual storyboarded pacing when available.
- 27 new tests across `test_location_mapping.py`, `test_accounting.py`,
  `test_marketing.py`, and `test_post_pipeline.py`; full desktop suite at
  164/164 passing.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
