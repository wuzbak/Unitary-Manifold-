# AZ Platform Control Plane & Reliability Contract

This document operationalizes the multi-track architecture program for `12-AZ-IP`, `hf-spaces`, `public-site`, and Base44 transition.

## 1) Canonical status source

- **Single source of truth:** `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/9-INFRASTRUCTURE/um_live_status.json`
- **Generator of record:** `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/9-INFRASTRUCTURE/generate_live_status.py`
- **API compatibility surface:** `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/bot/assistant_api.py` (`/api/status`)
- **Status drift gate:** `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/9-INFRASTRUCTURE/check_status_drift.py`

## 2) Control plane responsibilities

1. Shared status service and status compatibility fields
2. Release metadata and provenance artifacts
3. App registry and ownership matrix
4. Observability baseline (health checks, synthetic checks, error taxonomy)
5. Security baseline (secret scan, dependency scan, SBOM, signed provenance)

## 3) App plane responsibilities

Each application remains independently deployable and testable, with its own release cadence and incident response notes.

- Static apps: `public-site/` + `12-AZ-IP/*` browser surfaces
- Compute apps: `hf-spaces/*` Gradio/static spaces
- API services: `bot/assistant_api.py` and product backends

## 4) SLO targets by surface

| Surface | Availability SLO | Latency SLO | Error budget | Notes |
|---|---:|---:|---:|---|
| Static web (`public-site`) | 99.95% monthly | p95 < 800ms document load | 21m/month | Route-level broken-link and JS error checks |
| HF Spaces (Gradio/static) | 99.5% monthly | p95 < 2.5s first response | 3h39m/month | Cold-start aware, per-space health probes |
| Assistant/API (`/api/assistant`, `/api/status`) | 99.9% monthly | p95 < 1.5s status, <8s assistant | 43m/month | Endpoint fallback chain allowed |
| Data pipelines/status generation | 99.9% weekly success | Daily run < 5m | 1 failed run/week max | Must not publish stale status |

## 5) Base44 transition policy

- Base44 remains a **compatibility edge** only.
- Canonical implementation path is `public-site` + `hf-spaces` + API services.
- New feature work must target canonical stack first.
- Base44 deprecation milestones:
  1. Mirror mode only
  2. Read-only maintenance
  3. Traffic cutover complete
  4. Decommission

## 6) Required release gates

1. Tests green
2. Status drift gate green
3. Secret scan clean
4. Dependency/advisory checks clean
5. Provenance artifact generated
6. Epistemic integrity checks: no unsupported certainty language; open gaps visible

