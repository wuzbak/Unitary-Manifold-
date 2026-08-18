# FilmersCompanion — AI-Powered Film Production Suite

> **AxiomZero** | Filmmaker's Companion v1.0.0  
> *An AI agent suite for independent filmmakers — cinematography, locations, finance & AD tools.*

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Quick Start — Desktop](#3-quick-start--desktop)
4. [Quick Start — Android](#4-quick-start--android)
5. [API Reference](#5-api-reference)
6. [Production Modules](#6-production-modules)
7. [Knowledge Base](#7-knowledge-base)
8. [Agent System](#8-agent-system)
9. [Database Schema](#9-database-schema)
10. [Testing](#10-testing)
11. [Deployment](#11-deployment)
12. [Roadmap](#12-roadmap)

---

## 1. Overview

FilmersCompanion is a **dual-platform** (Python desktop + Android) AI production assistant built for independent filmmakers. It provides four core production modules:

| Module | Function |
|--------|----------|
| 🎥 **Cinematography** | Coverage suggestions, lighting (inverse square law), shot-list validation |
| 📍 **Locations** | Scout reports, permit tracking, unconfirmed location alerts |
| 💰 **Finance** | Budget builder, ROI calculator, DOOD, burn-rate alerts |
| 📋 **AD Suite** | Call sheets, turnaround compliance, one-liner scene lists |

### Design Philosophy

- **Offline-first**: Full functionality without internet; local LLM (Ollama) supported
- **Agent resolver chain**: Remote LLM → Ollama → Static KB (always answers)
- **Deterministic seed**: Ships with "THE OMEGA PROTOCOL" sample project (ID: `omega-001`)
- **Guild-aware**: SAG/DGA/WGA/IATSE minimums baked into KB
- **Axiom Omega**: 10 production principles embedded in the knowledge base

---

## 2. Architecture

```
apps/filmmakers-companion/
├── desktop/                    ← Python desktop app (FastAPI + Gradio)
│   ├── app/
│   │   ├── config.py           ← FilmConfig dataclass, FILM_* env vars
│   │   ├── main.py             ← FastAPI app factory, CLI entry point
│   │   ├── db/
│   │   │   ├── schema.py       ← 8-table SQLite schema, get_conn()
│   │   │   └── seed.py         ← THE OMEGA PROTOCOL seed data
│   │   ├── kb/
│   │   │   └── film_kb.py      ← 19 KB entries, search_kb()
│   │   ├── agents/
│   │   │   ├── base.py         ← BaseAgent: remote → ollama → static KB
│   │   │   ├── cinematography.py
│   │   │   ├── locations.py
│   │   │   ├── finance.py
│   │   │   ├── ad_suite.py
│   │   │   └── master.py       ← ProductionMasterAgent
│   │   ├── cinematography/     ← FastAPI router + Gradio UI
│   │   ├── locations/
│   │   ├── finance/
│   │   └── ad_suite/
│   ├── deploy/
│   │   ├── requirements.txt
│   │   ├── install.sh
│   │   └── install.py
│   └── tests/                  ← 93 pytest tests (6 files)
│       ├── conftest.py
│       ├── test_config.py      ← 10 tests
│       ├── test_db.py          ← 20 tests
│       ├── test_kb.py          ← 15 tests
│       ├── test_agents.py      ← 25 tests
│       ├── test_finance.py     ← 15 tests
│       └── test_cinematography.py ← 14 tests (+ 4 via test_agents)
└── android/                    ← Kotlin/Compose/Hilt/Room Android app
    ├── app/
    │   └── src/main/
    │       ├── AndroidManifest.xml
    │       └── java/com/axiomzero/filmmakerscompanion/
    │           ├── MainActivity.kt
    │           ├── FilmApp.kt
    │           ├── FilmersCompanionApp.kt
    │           ├── data/local/   ← Room DB, DAOs, Entities
    │           ├── data/repository/
    │           ├── di/           ← Hilt modules
    │           ├── viewmodel/
    │           └── ui/           ← Compose screens
    ├── build.gradle.kts
    ├── settings.gradle.kts
    └── scripts/
        ├── install_android.sh
        └── install_windows.bat
```

---

## 3. Quick Start — Desktop

### Prerequisites

- Python 3.9+
- (Optional) Ollama for local LLM
- (Optional) OpenAI API key for GPT-4o

### Install

```bash
cd apps/filmmakers-companion/desktop/deploy
bash install.sh                 # Linux/macOS
python install.py               # any platform
```

### Run

```bash
# From repo root
python -m desktop.app.main                        # FastAPI + Gradio on :7864
python -m desktop.app.main --port 8080            # custom port
python -m desktop.app.main --init                 # init DB only
python -m desktop.app.main --ask "turnaround"     # CLI query

# Via uvicorn directly
cd apps/filmmakers-companion
uvicorn desktop.app.main:app --reload --port 7864
```

### URLs

| URL | Description |
|-----|-------------|
| `http://localhost:7864/` | App root |
| `http://localhost:7864/ui` | Gradio UI (all 4 modules) |
| `http://localhost:7864/docs` | Swagger API docs |
| `http://localhost:7864/api/health` | Health check |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FILM_PORT` | `7864` | HTTP server port |
| `FILM_HOST` | `0.0.0.0` | Bind address |
| `FILM_DB_PATH` | `data/film.db` | SQLite database path |
| `FILM_OFFLINE` | `false` | Disable remote LLM calls |
| `FILM_OPENAI_API_KEY` | _(none)_ | OpenAI key (optional) |
| `FILM_OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model |
| `FILM_LLM_URL` | `http://localhost:11434/api/generate` | Ollama endpoint |
| `FILM_LLM_MODEL` | `llama3.2:3b` | Ollama model |

---

## 4. Quick Start — Android

### Prerequisites

- Android Studio Ladybug (2024.2+)
- Android SDK 35
- Java 17

### Build

```bash
cd apps/filmmakers-companion/android

# Linux/macOS
bash scripts/install_android.sh

# Windows
scripts\install_windows.bat

# Manual Gradle
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Package

`com.axiomzero.filmmakerscompanion`

### Screens

1. **Dashboard** — module launcher with project header
2. **Cinematography** — lighting calculator (local Kotlin math, no network)
3. **Locations** — Room-backed list with unconfirmed alerts
4. **Finance** — budget lines, burn rate progress bar
5. **AD Suite** — turnaround checker (local math, instant)

---

## 5. API Reference

### Health

```
GET /api/health
→ {"status": "ok", "service": "filmers-companion", "version": "1.0.0"}
```

### Cinematography

```
POST /api/cinematography/suggest-coverage
Body: {"synopsis": "...", "scene_type": "drama|action|comedy|thriller"}
→ {"coverage": [...]}

POST /api/cinematography/calc-lighting
Body: {"distance_ft": 10, "fixture_power_w": 1000}
→ {"lux": 123.4, "ev": 5.68, "f_stop": 1.03, "color_temp_k": 5600, ...}

POST /api/cinematography/validate-shot-list
Body: {"shots": [{"coverage_type": "master"}, ...]}
→ {"valid": true, "issues": [], "warnings": [...]}
```

### Locations

```
GET  /api/locations/{project_id}
POST /api/locations/
GET  /api/locations/{location_id}/scout-report
GET  /api/locations/{project_id}/unconfirmed
```

### Finance

```
GET  /api/finance/{project_id}/budget-lines
POST /api/finance/build-budget         Body: {"total": 1000000, "custom_pcts": {...}}
POST /api/finance/calc-roi             Body: {"total_budget":..., "projected_revenue":..., "distribution_pct":...}
GET  /api/finance/{project_id}/burn-rate
GET  /api/finance/{project_id}/alerts?threshold=0.8
```

### AD Suite

```
GET  /api/ad-suite/{project_id}/call-sheets
POST /api/ad-suite/generate-call-sheet  Body: {"scenes":[...], "location":{...}, "shoot_date":"..."}
POST /api/ad-suite/check-turnaround     Body: {"wrap_time":"22:00", "call_time":"07:00"}
POST /api/ad-suite/one-liner            Body: {"scenes":[...]}
POST /api/ad-suite/dept-note            Body: {"project_id":"...", "dept":"...", "note":"..."}
```

---

## 6. Production Modules

### 🎥 Cinematography Advisor

**Coverage suggestions** — scene type × synopsis → ordered shot list suggestions with lens, movement, and notes.

**Lighting calculator** — inverse square law:
```
lumens   = fixture_power_w × 15            (LED approximation)
lux      = lumens / (4π × d_meters²)       (inverse square law)
EV       = log₂(lux / 2.5)                (ISO 100 incident calibration)
f-stop   = √(2^EV × 1/48)                 (24fps shutter)
```
Doubling distance → quarters lux → reduces EV by exactly 2 stops.

**Shot list validation** — `valid=True` iff master shot present; issues/warnings for missing CU, MS.

### 📍 Location Manager

- **Scout reports**: formatted text report with permit status, fee, access notes
- **Unconfirmed check**: scenes whose `location_id` maps to non-confirmed location
- **Group by location**: cluster scenes by location for scheduling

### 💰 Finance Officer

- **Build budget**: applies `BUDGET_ALLOCATION_DEFAULTS` (11 categories, sums to 100%), normalises custom overrides
- **ROI**: `gross_revenue = projected × dist_pct`; `roi_pct = net_profit / budget × 100`
- **DOOD**: `dood_per_day = total_budget / shoot_days`
- **Burn rate**: `total_actual / total_budgeted × 100%`; alerts when category exceeds threshold

### 📋 AD Chief

- **Call sheet**: formatted text sheet with crew call, location, scenes, general notes
- **Turnaround**: overnight-aware (if call ≤ wrap, add 24h); violation if gap < 12h
- **One-liner**: formatted scene list `1. INT/DAY — Synopsis (Xp)`

---

## 7. Knowledge Base

19 entries across these topics:

| Category | Entries |
|----------|---------|
| Scheduling | turnaround (12h min), call sheets, one-liners |
| Lighting | f-stop, EV, inverse square law, color temperature |
| Finance | budget allocation, ROI, DOOD, burn rate, contingency (12%), above-the-line |
| Coverage | master, coverage types, shot lists |
| Locations | scout reports, permits |
| Unions | SAG, DGA, WGA, IATSE minimums |

### Axiom Omega Principles (10)

Core production principles including: pre-production investment, clear chain of command, dailies review, safety, contingency buffer, communication rhythms, coverage before cutaways, location relationship-building, post-production front-loading, and creative accountability.

---

## 8. Agent System

```
BaseAgent.resolve(question)
    │
    ├── offline_mode=False?
    │   ├── _call_remote()      ← OpenAI API
    │   └── _call_ollama()      ← Ollama (local)
    │
    └── _static_kb_answer()     ← search_kb() always available
```

**ProductionMasterAgent.check_all(db_path, project_id)** returns:
```json
{
  "turnaround_violations": [...],
  "budget_alerts": [...],
  "unconfirmed_locations": [...],
  "total_issues": 3,
  "status": "NEEDS_ATTENTION"
}
```

---

## 9. Database Schema

8 SQLite tables, all with `TEXT PRIMARY KEY` IDs (UUID or deterministic for seed data):

| Table | Key Columns |
|-------|-------------|
| `scenes` | `id, project_id, scene_number, location_id, int_ext, day_night, synopsis, page_count, status, shoot_date` |
| `locations` | `id, project_id, name, address, int_ext, permit_status, fee, owner_contact, notes` |
| `budget_lines` | `id, project_id, category, description, budgeted, actual` |
| `takes` | `id, scene_id, take_number, printed, issues, notes` |
| `call_sheets` | `id, project_id, shoot_date, general_call, location_id, scenes, notes` |
| `dept_notes` | `id, project_id, dept, note, created_at` |
| `shot_lists` | `id, scene_id, shot_number, coverage_type, lens, movement, frame_rate, notes` |
| `permit_tracker` | `id, location_id, permit_type, status, applied_date, approved_date, expiry_date, authority` |

### Seed Data — THE OMEGA PROTOCOL (`omega-001`)

- 5 scenes (scene-001…scene-005)
- 3 locations: rooftop (confirmed), warehouse (pending), city hall (rejected)
- 6 budget lines totalling **$790,000**
- 2 call sheets, 3 shot list entries

---

## 10. Testing

```bash
# From apps/filmmakers-companion/
python -m pytest desktop/tests/ -q
# Expected: 93 passed, 0 failed

# Verbose with coverage
python -m pytest desktop/tests/ -v --tb=short

# Single file
python -m pytest desktop/tests/test_cinematography.py -v
```

### Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_config.py` | 10 | FilmConfig, env vars, singleton |
| `test_db.py` | 20 | All 8 tables, seed idempotency, totals |
| `test_kb.py` | 15 | KB entries, search, data structures |
| `test_agents.py` | 25 | All 6 agent classes, offline mode |
| `test_finance.py` | 15 | Budget, ROI, DOOD, burn rate, alerts |
| `test_cinematography.py` | 14 | Lighting math, shot list validation |

---

## 11. Deployment

### Local

```bash
pip install -r desktop/deploy/requirements.txt
python -m desktop.app.main
```

### Production

```bash
# Gunicorn
gunicorn desktop.app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:7864

# Docker (placeholder)
docker build -t filmers-companion .
docker run -p 7864:7864 filmers-companion
```

### Environment

Set `FILM_OFFLINE=true` for air-gapped deployments. The static KB always answers without network access.

---

## 12. Roadmap

See [`ROADMAP.md`](ROADMAP.md) for the full roadmap.

| Version | Status | Highlights |
|---------|--------|------------|
| **1.0** | ✅ Complete | 4 modules, 93 tests, Android MVP |
| **1.1** | Planned | PDF call sheet export, SQLite FTS search |
| **1.2** | Planned | Multi-project support, project switcher |
| **2.0** | Planned | Ollama streaming, real-time collaboration |

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
