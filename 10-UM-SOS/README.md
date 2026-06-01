# 10-UM-SOS — Unitary Manifold Scientific Operating System

Version synchronized to current repository state (v15.1 lane; 2026-06-01 session).

## What is implemented

- **Layer 1 (Prediction API):** `src/core/um_sos_api.py`
- **Layer 2 (Experimental monitor endpoints):** `/api/v1/status`, `/api/v1/pillars`, `/api/v1/gaps`
- **Layer 3 (Derivation graph export + UI):** `10-UM-SOS/graph/dag.json`, `10-UM-SOS/graph/index.html`
- **Layer 4 (Preregistration registry):** `10-UM-SOS/registry/predictions.json`
- **Layer 5 (Frontend explorer/dashboard):** `10-UM-SOS/frontend/*`
- **Layer 6 (Governance-integrated AI query):** `/api/v1/ai/query` using epistemic labels + governance lane classification
- **Layer 7 bridge:** static/frontend + backend workflow in place for deployment

## Build outputs

```bash
python3 10-UM-SOS/scripts/build_registry.py
python3 10-UM-SOS/scripts/build_graph.py
```

## Run backend locally

```bash
pip install fastapi uvicorn numpy scipy sympy mpmath
uvicorn src.core.um_sos_backend:app --reload
```

## Key endpoints

- `GET /api/v1/predictions/all`
- `GET /api/v1/status?experiment=DESI`
- `GET /api/v1/gaps`
- `GET /api/v1/pillars?pillar_id=486`
- `POST /api/v1/governance/classify`
- `POST /api/v1/ai/query`
- `GET /api/v1/preregistered`

## Deployment assets

- Docker image spec: `10-UM-SOS/Dockerfile`
- Compose stack: `docker-compose.yml`
- Registry integrity CI: `.github/workflows/um-sos-registry-check.yml`
- Pages deploy workflow: `.github/workflows/um-sos-pages.yml`
