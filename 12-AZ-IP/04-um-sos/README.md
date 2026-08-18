# 10-UM-SOS — Unitary Manifold Scientific Operating System

*Version synchronized to v15.8 (2026-06-05). Build scripts verified current.*

## What is implemented

- **Layer 1 (Prediction API):** `src/core/um_sos_api.py`
- **Layer 2 (Experimental monitor endpoints):** `/api/v1/status`, `/api/v1/pillars`, `/api/v1/gaps`
- **Layer 3 (Derivation graph export + UI):** `10-UM-SOS/graph/dag.json`, `10-UM-SOS/graph/index.html`
- **Layer 4 (Preregistration registry):** `10-UM-SOS/registry/predictions.json`
- **Layer 5 (Frontend explorer/dashboard):** `10-UM-SOS/frontend/*`
- **Layer 6 (Governance-integrated AI query):** `/api/v1/ai/query` using epistemic labels + governance lane classification
- **Layer 7 bridge:** static/frontend + backend workflow in place for deployment

## Build status (v15.8)

Build scripts run successfully and produce current output:

```bash
python3 10-UM-SOS/scripts/build_registry.py   # → registry/predictions.json (8 entries)
python3 10-UM-SOS/scripts/build_graph.py       # → graph/dag.json (derivation DAG)
```

Both scripts verified current as of 2026-06-05. The registry is append-only;
new preregistrations (Pillars 435, 437, 369, 486) are included.

## Public deployment (GitHub Pages)

The UM-SOS frontend and derivation graph are configured for GitHub Pages deployment
via `.github/workflows/um-sos-pages.yml`. To enable:

1. Go to the repository Settings → Pages
2. Set source to "GitHub Actions"
3. The `um-sos-pages.yml` workflow will deploy on the next push to `main`

Once deployed, the public URL will be:  
`https://wuzbak.github.io/Unitary-Manifold-/`

The derivation graph (`graph/index.html`) is a standalone D3.js visualization
that works directly from the Pages endpoint — no server required.

## Run backend locally

```bash
pip install fastapi uvicorn numpy scipy sympy mpmath
uvicorn src.core.um_sos_backend:app --reload
```

## Key endpoints

- `GET /api/v1/predictions/all` — all 28 SM parameter predictions with epistemic labels
- `GET /api/v1/status?experiment=DESI` — current PASS/TENSION/FALSIFIED verdict
- `GET /api/v1/gaps` — all 13 formal admissions with current status
- `GET /api/v1/pillars?pillar_id=486` — pillar metadata and links
- `POST /api/v1/governance/classify` — Pentad decision routing
- `POST /api/v1/ai/query` — Layer 7 AI query with epistemic gating
- `GET /api/v1/preregistered` — preregistration registry (SHA-256 committed predictions)

## Deployment assets

- Docker image spec: `10-UM-SOS/Dockerfile`
- Compose stack: `docker-compose.yml`
- Registry integrity CI: `.github/workflows/um-sos-registry-check.yml`
- Pages deploy workflow: `.github/workflows/um-sos-pages.yml`

## Architecture reference

See `10-UM-SOS/ARCHITECTURE.md` for the full seven-layer architecture specification.
See `10-UM-SOS/ROADMAP.md` for the remaining implementation roadmap.



## Canonical source

This product is canonically consolidated at `12-AZ-IP/04-um-sos/`.
