# AZ Braided Qubit Ansatz Studio — Product 31

**Folder:** `12-AZ-IP/31-az-braided-qubit-ansatz-studio/`
**Version:** 1.2.0
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
The exported circuit now includes OpenQASM 2.0 with RY/CNOT operations so it
can be handed to compatible quantum SDKs or transpilers. The file has no
measurements, backend selection, noise model, or job submission; successful
simulation does not establish hardware behavior or validate a physics claim.

## Usage

```bash
python 12-AZ-IP/31-az-braided-qubit-ansatz-studio/run.py --help
```

Export a deterministic, seeded circuit to OpenQASM 2.0:

```bash
python 12-AZ-IP/31-az-braided-qubit-ansatz-studio/run.py export \
  --n-qubits 8 --n-layers 2 --seed 42 > ansatz.qasm
```

To export parameters produced by an external optimizer, pass the ordered
rotation angles directly (one per qubit per layer, including the final layer):

```bash
python 12-AZ-IP/31-az-braided-qubit-ansatz-studio/run.py export \
  --n-qubits 2 --n-layers 1 --angles 0.25,-0.5,0.75,0 > optimized.qasm
```

The CLI requires an explicit `export` or `serve` command and a parameter source.
Exports are bounded to 2–8 qubits and 0–8 layers; user angles must match
`n_qubits * (n_layers + 1)` and be finite. It does not submit the program to
a quantum provider.

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

Endpoints: `GET /api/status`, `GET /api/circuit?n_qubits=&n_layers=&seed=` or
`GET /api/circuit?n_qubits=2&n_layers=1&angles=0.25,-0.5,0.75,0` —
deterministic for a given seed, returning the exported gate list, OpenQASM 2.0,
and the validation report. The dashboard can download the `.qasm` artifact.
The API rejects unknown/duplicate parameters and bounds circuits to 2–8 qubits,
0–8 layers, a 32-bit unsigned seed, and user-angle input to 4096 characters.
Pass either `seed` or `angles`, not both. The API reports whether parameters
were seeded or user supplied; a comparison against the reference ansatz is a
software consistency check, not an experimental result.

## Tests

```bash
python -m pytest 12-AZ-IP/31-az-braided-qubit-ansatz-studio/tests -q
```

## Sources

- `src/quantum/kk_vqe.py`, `src/quantum/xdiag_bridge/`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #4

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
