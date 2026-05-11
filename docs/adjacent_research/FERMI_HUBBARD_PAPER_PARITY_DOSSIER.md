# Fermi–Hubbard Paper-Parity Dossier (Adjacent Track)

## Target parity dimensions

1. Hamiltonian formalization
2. Fermion-to-qubit mapping dual lane (JW/BK)
3. Digital execution and hardware-trajectory metadata
4. Observables parity: spin and charge lanes
5. TDVP parity comparison layer
6. Wall-clock scaling curves

## Current status

- Hamiltonian module: **implemented**
- JW mapping: **implemented**
- BK mapping: **implemented** (exact small-mode parity lane)
- Execution stack: **implemented** (simulator + hardware adapter abstraction)
- Observables: **implemented** (charge, spin, doublon, staggered magnetization)
- TDVP parity API: **implemented** (`TDVPReference`, `tdvp_parity_report`)
- Scaling curves: **implemented** (`build_scaling_curve`)

## Remaining escalation lane

- Hardware-scale empirical campaigns should use backend-specific adapter extensions
  with queue/job/result ingestion in a dedicated deployment pipeline.
- Large-mode BK acceleration can be expanded with algorithmic transform optimizations.
