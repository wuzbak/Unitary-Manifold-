# Predictions, Gaps, and Falsification — Current Operational Form

## Primary observable lanes

- `n_s = 0.9635` (Planck-consistent)
- `r_braided = 0.0315` (SO/CMB-S4 routing active)
- `beta = {0.273°, 0.331°}` with explicit forbidden interval routing
- DESI dark-energy lane with DR3 decision protocol preregistered

## Active falsification windows

- DESI DR3 (2026)
- SO DR1 (2027)
- JUNO (2027)
- SPHEREx (2027–2028)
- HL-LHC KK graviton lane (2029–2033)
- LiteBIRD birefringence lane (~2032)

## Honest-gap lane

Admissions are explicit and queryable.

- API: `GET /api/v1/gaps`
- Registry payload: `10-UM-SOS/registry/predictions.json#admissions`
- Canonical source: `src/core/pillar394_postulate_minimality_audit.py`

## Machine-readable prediction surfaces

- `src/core/prediction_registry.py`
- `10-UM-SOS/registry/predictions.json`
- `GET /api/v1/predictions/all`

## Validation posture

The framework is evaluated continuously through testable code paths and preregistered decision rules. Claims remain tied to explicit status labels and can be programmatically filtered by endpoint consumers.
