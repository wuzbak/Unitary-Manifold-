# RELAY — External AI Context Hand-Off Document

> **Badge:** `[OPERATIONS]` `[CURRENT]`
>
> **Purpose:** Copy this file into a fresh AI session to restore current execution context quickly.
> **Last updated:** 2026-06-01 (v15.1 sync + UM-SOS platform rollout)

---

## 1) Project state

The Unitary Manifold is an executable 5D geometric physics framework with machine-auditable prediction routing, falsification tripwires, and governance lanes.

Current verified baseline in this session:

- **45,505 passed · 22 skipped · 12 deselected · 0 failed**
- Command: `python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q --tb=short`
- Next sprint slot starts at **Pillar 495**

---

## 2) High-signal current outputs

- `n_s = 0.9635` (Planck-consistent)
- `r_braided = 0.0315` (tracked against SO/CMB-S4 routing)
- `beta = {0.273°, 0.331°}` (LiteBIRD window preregistered)
- DESI dark-energy tension lane active and preregistered
- Admission ledger surfaced machine-readably in API and registry exports

---

## 3) Canonical truth surfaces

- `STATUS.md`
- `FALLIBILITY.md`
- `docs/TRUTH_LAYER.md`
- `docs/CLAIM_MASTER_BOARD.md`
- `docs/GATEKEEPER_SUMMARY.md`
- `docs/mas_tracker.yml`

---

## 4) UM-SOS implementation surfaces

- Registry export: `10-UM-SOS/registry/predictions.json`
- Derivation graph export: `10-UM-SOS/graph/dag.json`
- Graph UI: `10-UM-SOS/graph/index.html`
- Prediction frontend: `10-UM-SOS/frontend/index.html`
- FastAPI backend app: `10-UM-SOS/backend/app.py`
- Core API implementation: `src/core/um_sos_api.py`
- Registry build script: `10-UM-SOS/scripts/build_registry.py`
- Graph build script: `10-UM-SOS/scripts/build_graph.py`

---

## 5) API endpoints

- `GET /api/v1/predictions/all`
- `GET /api/v1/status?experiment=...`
- `GET /api/v1/gaps`
- `GET /api/v1/pillars?pillar_id=...`
- `POST /api/v1/governance/classify`
- `GET /api/v1/preregistered`

---

## 6) Active decision windows

- DESI DR3 (2026)
- SO DR1 (2027)
- JUNO (2027)
- SPHEREx (2027–2028)
- HL-LHC graviton lane (2029–2033)
- LiteBIRD birefringence lane (~2032)

---

## 7) Manuscript and outreach

- New manuscript chapters added under `manuscript/` for cosmology, holography, topology, entropy-functional framing, and admissions appendix.
- Submission checklist synchronized at `6-MONOGRAPH/ZENODO_SUBMISSION_CHECKLIST.md`.
- Latest outreach slot advanced with a new post at `7-OUTREACH/substack/posts/post-250-s03e028-autonomous-stewardship-machine.md`.

---

## 8) Quick runbook

```bash
# rebuild UM-SOS machine exports
python3 10-UM-SOS/scripts/build_registry.py
python3 10-UM-SOS/scripts/build_graph.py

# run UM-SOS targeted tests
python3 -m pytest tests/test_um_sos_registry.py tests/test_um_sos_graph.py tests/test_um_sos_api.py tests/test_um_sos_rag.py -q

# run full regression
python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q --tb=short
```
