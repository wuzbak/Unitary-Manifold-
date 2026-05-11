# Adjacent Research Track — Fermi–Hubbard Quantum Simulation

## Scope and boundary

This track is a **connected but separate** effort from Unitary Manifold Category-1
physics claims.

- Classification: **Phenomenological/engineering adjacent research**
- Not a numbered core UM pillar
- Not a hardgate dependency
- Tracked for reproducibility and audit traceability

## Implemented components

- `src/quantum/fermi_hubbard.py`
  - Dedicated 1D spinful Fermi–Hubbard Hamiltonian specification and fermionic terms
- `src/quantum/fermion_mapping.py`
  - Jordan–Wigner mapping
  - Bravyi–Kitaev exact mapping pipeline for small-mode parity verification lane
- `src/quantum/execution.py`
  - Simulator-first execution
  - Hardware-adapter abstraction (mock hardware payload for queued-run metadata)
  - Trotterized evolution and run-manifest artifact writer
- `src/quantum/observables.py`
  - Spin/charge observables and double occupancy snapshots
- `src/quantum/benchmarks.py`
  - TDVP parity metric interface
  - Wall-clock scaling-curve builder

## Hardgate posture

This lane is intentionally isolated from canonical closure hardgates.
Core UM PASS/TENSION/FALSIFIED surfaces remain unchanged unless a future,
explicit governance decision promotes any result across the epistemic boundary.
