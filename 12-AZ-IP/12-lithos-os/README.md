# ⬛ LithosOS — Mineral & Gemstone Identifier

**Folder:** `12-AZ-IP/12-lithos-os/`  
**Product:** LithosOS — Mineral and Gemstone Identifier  
**Version:** v1.0  
**Company:** AxiomZero Technologies  
**Status:** Active — functional Gradio desktop application  
**Port:** `http://localhost:7861`

---

## What LithosOS Is

LithosOS is a specialized mineral classification and gemstone diagnostic application. It runs a
dedicated Gradio PC UI and is deployed as part of a cohesive "crust diagnostic loop" alongside
**TerraOS** (soil/water) to form the AxiomZero Earth Science suite.

The application provides (current, verified scope):
- **Mineral identification by description** — keyword matching against the local catalog.
  Image-based identification is a **stub** (`source="offline_stub"`); no trained model ships.
- **Gemstone grading guidance** — advisory text from the retrieval/LLM agents only; there is
  no automated colour/clarity/cut/carat measurement.
- **Formation context** (igneous, metamorphic, sedimentary) from the local knowledge base.
- **Measured field seismicity (live public data)** — recent catalogued earthquakes near a
  site from the USGS ComCat FDSN Event Web Service, with source/time provenance and an
  explicit `live` / `cached` / `stale` / `unavailable` status (see below).

Not provided: geographic occurrence mapping, geothermal resource assessment, earthquake
prediction, or seismic-hazard estimates. Earlier text describing "occurrence mapping based on
the Unitary Manifold geological model" overstated the implementation and has been withdrawn.

---

## Quick Start

```bash
pip install -r requirements.txt
python run.py                      # REST API at http://localhost:7861 (docs at /docs)
# Gradio desktop UI (requires gradio):  python -m lithic.app.main --ui
#   (the `lithic` package alias is provided by the repository-root conftest/launcher)
```

---

## Architecture

```
12-lithos-os/
├── README.md
├── __init__.py
├── requirements.txt         ← pip dependencies
├── app/
│   ├── __init__.py
│   ├── main.py              ← Gradio entry point
│   ├── config.py            ← constants and model paths
│   ├── android/             ← Android companion app
│   ├── api/                 ← REST API layer (FastAPI)
│   ├── bot/                 ← keyword/IDF retrieval + optional LLM agents
│   ├── db/                  ← SQLite mineral catalog
│   ├── models/              ← domain model classes
│   ├── pc/                  ← PC desktop UI modules
│   └── sync/                ← delta sync, Mindat/USGS guide fetcher,
│                               usgs_seismicity.py (measured USGS seismicity adapter)
├── deploy/
│   ├── install.py           ← automated installer
│   ├── install.sh           ← shell installer
│   └── requirements.txt     ← deploy-only requirements
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_bot.py
    ├── test_db.py
    ├── test_installer.py
    ├── test_mineral_guides.py
    └── test_usgs_seismicity.py  ← deterministic, no-network adapter/API/UI tests
```

---

## Dependencies

See `requirements.txt`. Core dependencies:
- `gradio` — UI framework
- `fastapi` + `uvicorn` — REST API
- `sqlite3` — mineral database (stdlib)
- `scikit-learn` — TF-IDF retrieval for TerraBot
- `pillow` — image processing for visual identification

---

## Live measured data — USGS field seismicity

**Workflow:** enter a site latitude/longitude → LithosOS queries the USGS ComCat catalogue
(`https://earthquake.usgs.gov/fdsnws/event/1/query`, GeoJSON) → validates the payload →
caches it in SQLite → returns measured events plus a summary and provenance.

| Surface | How |
|---|---|
| REST | `GET /api/v1/field/seismicity?lat=38.79&lon=-122.76&radius_km=50&days=30&min_magnitude=1&limit=100&refresh=false` |
| Gradio UI | Tab **"Field Seismicity (USGS, measured)"** (`python -m lithic.app.main --ui`) |
| Python | `app.sync.usgs_seismicity.USGSSeismicityAdapter(...).get_seismicity(SeismicityQuery(...))` |

**Guarantees**
- Query bounds validated before any network call (lat ±90, lon ±180, radius 1–2000 km,
  days 1–90, magnitude −1–10, limit 1–500); invalid input → HTTP 422.
- Network bounded: socket timeout clamped to 0.5–15 s (`LITHOS_SEISMICITY_TIMEOUT_S`,
  default 8), response capped at 5 MB, HTTPS to `earthquake.usgs.gov` only.
- Schema validation: FeatureCollection envelope + `metadata.generated` required; malformed
  features are dropped and counted in `provenance.features_rejected`.
- Status: `live` (fresh fetch), `cached` (≤15 min old cache), `stale` (data older than
  `LITHOS_SEISMICITY_STALE_AFTER_S`, default 3600 s — e.g. last good copy served after a
  timeout), `unavailable` (no valid data; no events are ever fabricated).
- Provenance: source name, exact query URL, licence (USGS public domain), source
  `generated` time, retrieval time, data age, cache flag, adapter version.
- `LITHOS_OFFLINE=true` disables fetching; existing cache is served with its true status.

**Limitations:** events are catalogue entries (automatic or reviewed — see `review_status`);
recent automatic solutions may be revised by USGS. Coverage and completeness vary by region
(densest in the U.S. networks). The data is site context only — it is not linked to the
mineral catalog and is not a hazard or geothermal assessment. Tests use injected fixtures;
live connectivity is not exercised in CI.

## Integration with TerraOS

LithosOS shares the `TerraBot` retrieval engine and the Android companion with `11-terra-os`.
Both are part of the AxiomZero Earth Science diagnostic loop.

---

## Co-authorship

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## Open mineral data

- `lithos_os/engine/open_mineral_data.py` provides a 30-mineral Raman reference table, best-match identification, and orbifold boundary-condition lookups.
- The RRUFF download URL is carried as a reference pointer for open spectral workflows.

## KK crystal analogy

- `lithos_os/engine/crystal_symmetry.py` maps the seven crystal systems onto 5D KK orbifold boundary-condition analogies (`Z1`, `Z2`, `Z2xZ2`, `Z3`, `Z4`, `Z6`).
