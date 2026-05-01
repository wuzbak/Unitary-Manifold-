# 2-REPRODUCIBILITY — Everything a Verifier Needs

This folder contains all records required to reproduce, audit, and independently
verify the numerical results of the Unitary Manifold framework.

---

## Quick start

```bash
# From the repository root:
pip install -r requirements.txt pytest

# Full test suite (~2 min):
python -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" omega/ -q
# Expected: 14,772 passed, 330 skipped, 11 deselected, 0 failed

# Single-module fast check:
python -m pytest tests/test_metric.py tests/test_evolution.py -v

# Entry-point proof script (13 checks, < 1 second):
python VERIFY.py

# Full symbolic algebra proof:
python ALGEBRA_PROOF.py
```

---

## Contents

| File | Purpose |
|------|---------|
| `SIMULATION_RUNS.md` | Record of all major simulation runs: parameters, hardware, output checksums |
| `VALIDATION_REPORT.md` | External validation attempts and results |
| `CONSISTENCY_LOG.md` | Cross-check log: every equation verified against at least two independent code paths |
| `SNAPSHOT_MANIFEST.md` | File-by-file hash manifest for the v9.27 OMEGA EDITION snapshot |

The test suite itself lives at `tests/` (repo root) — it is not moved because
pytest must discover it from the root directory.

---

## Test suite organisation

| Directory | Tests | What it covers |
|-----------|-------|----------------|
| `tests/` | ~13,059 | Core physics: metric, evolution, holography, inflation, FTUM, SM parameters |
| `recycling/` | 316 | Pillar 16: φ-debt entropy accounting |
| `5-GOVERNANCE/Unitary Pentad/` | ~1,266 | HILS governance framework |
| `omega/` | 168 | Pillar Ω: Universal Mechanics Engine |

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
