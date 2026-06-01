# Core Theory — Unitary Manifold (Current Snapshot)

The Unitary Manifold is a 5D gauge-geometric framework where irreversibility is modeled as a structural feature of the higher-dimensional geometry, not as a statistical add-on.

## Core structural claim

> The arrow of time is encoded in geometric structure and propagated through the 5D→4D reduction chain.

## Current machine-verified surfaces

- `src/core/metric.py`
- `src/core/evolution.py`
- `src/core/inflation.py`
- `src/core/pillar394_postulate_minimality_audit.py`
- `src/core/pillar395_derivation_dag.py`
- `src/core/prediction_registry.py`

## Current epistemic architecture

- **Derived / constrained predictions** are surfaced in registry and claim boards.
- **Admissions (1–13)** are explicit and machine-readable; no hidden gap lane.
- **Decision windows** are preregistered and tied to experiment-specific tripwires.

## Current verification baseline

- Full regression in current session: **45,505 passed · 22 skipped · 12 deselected · 0 failed**.

## UM-SOS integration points

- Preregistration registry export: `10-UM-SOS/registry/predictions.json`
- Derivation DAG export: `10-UM-SOS/graph/dag.json`
- FastAPI endpoints in `src/core/um_sos_api.py`
