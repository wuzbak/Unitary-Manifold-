# AZ Braided Qubit Ansatz Studio — Product 31

**Folder:** `12-AZ-IP/31-az-braided-qubit-ansatz-studio/`
**Version:** 1.1.0
**TRL:** TRL-2 (simulation-validated circuit export; no hardware submission performed)
**Status:** Active — Phase 0 of article-354's quantum-bridge roadmap, now a runnable web product

## What this is

Extends `src/quantum/kk_vqe.py`'s existing hardware-efficient ansatz — Ry
layers plus a CNOT ladder — from a dense-matrix construction into an
explicit, JSON-serializable gate list (`build_braided_ansatz_circuit`) for
an eight-qubit braided-lattice instance, the representation a transpiler
for a real cloud quantum backend (IBM Quantum, IonQ, or similar) would
consume.

The exported gate list is independently cross-checked: `simulate_circuit`
is a from-scratch statevector simulator that does **not** reuse
`kk_vqe`'s matrix-construction code path, and `validate_against_kk_vqe`
confirms the two produce the identical state (max abs diff < 1e-9) across
2–8 qubit instances.

## Epistemic status

This is Phase 0 only: a small-qubit ansatz, validated in simulation. Phase 1
(an actual cloud quantum-hardware run, on the order of a few thousand
dollars of compute) and Phase 2 (comparing the noisy hardware result
against both the classical Fermi-Hubbard solver and XDiag exact
diagonalization) are **not** part of this product and require submitting a
real job to external infrastructure.

## Usage

```bash
python 12-AZ-IP/31-az-braided-qubit-ansatz-studio/run.py
```

```python
from az_braided_qubit_ansatz_studio import build_braided_ansatz_circuit, validate_against_kk_vqe
import numpy as np

theta = np.random.default_rng(0).uniform(-np.pi, np.pi, size=8 * 3)
circuit = build_braided_ansatz_circuit(theta, n_qubits=8, n_layers=2)
result = validate_against_kk_vqe(theta, n_qubits=8, n_layers=2)
```

## Running as a web product

A stdlib-only JSON API plus a static dashboard sits over the same circuit export above
(`app/server.py` dispatches to `dispatch_api_request`, covered by `tests/test_api.py`):

```bash
python 12-AZ-IP/31-az-braided-qubit-ansatz-studio/run.py serve --port 8131
# then open http://127.0.0.1:8131/
```

Endpoints: `GET /api/status`, `GET /api/circuit?n_qubits=&n_layers=&seed=` — deterministic
for a given seed, returning both the exported gate list and the validation report.

## Tests

```bash
python -m pytest 12-AZ-IP/31-az-braided-qubit-ansatz-studio/tests -q
```

## Sources

- `src/quantum/kk_vqe.py`, `src/quantum/xdiag_bridge/`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #4

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
