# THREE_SECTOR_ARCHITECTURE.md — UV/Bulk/IR Extension Specification

## Scope

This document defines the three-sector extension of the existing S¹/Z₂ orbifold
architecture and records what is and is not closed.

Sectors:
- **UV boundary sector:** \(n_w = 5\)
- **Bulk parent sector:** \(n = 6\)
- **IR boundary sector:** \(n_{shadow} = 7\)

Derived invariant:
- \(k_{CS} = n_w^2 + n_{shadow}^2 = 5^2 + 7^2 = 74\)

## Field and geometry assignment

- Base compactification remains S¹/Z₂.
- \(B_\mu\) remains a bulk field with orbifold boundary conditions inherited from the canonical metric lane.
- Boundary sectors are treated as independent anomaly receivers at \(y=0\) and \(y=\pi R\).

## Anomaly structure

Implemented in:
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/src/core/anomaly_inflow_3sector.py`

What is computed:
- APS η-invariants at both fixed points.
- Linear anomaly coefficient candidate \(5+6+7=18\).
- η-weighted anomaly coefficient candidate.

Status:
- **OPEN_GAP** for uniqueness of “18 Weyl fermions required”.
- Reason: the linear and η-weighted anomaly prescriptions do not yet collapse to a single forced integer count.

## Brane tension and stabilization structure

Implemented in:
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/src/core/brane_tension_stabilization.py`

What is computed:
- \(T_{UV}\propto n_w^2=25\), \(T_{IR}\propto n_{shadow}^2=49\), \(T_{UV}+T_{IR}=74\).
- Candidate relation \(k r_c = 2n = 12\).
- Candidate relation \(\phi^{bare}_{min}=3n=18\).

Status:
- **FITTED** for both integer closures.
- Reason: these relations hold exactly under the three-sector closure ansatz, but a full first-principles RS1 variational derivation remains open.

## Prediction-impact lane for certified architecture limits

Implemented in:
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/src/core/three_sector_cosmology.py`

Tested limits:
- AL-1 CMB peak suppression
- AL-2 tensor ratio tension
- AL-3 \(w_a\) tension
- AL-4 cosmological-constant hierarchy residual

Status summary:
- Current three-sector implementation yields **partial reductions only**.
- No certified limit is fully closed in this architecture pass.

## Yukawa geometric lane

Implemented in:
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/src/core/yukawa_geometric.py`

What is closed:
- **DERIVED** three-sector zero-mode overlap texture (3×3 geometric Yukawa matrix).

What remains open:
- **FITTED** mass-calibrated phenomenology remains required for full SM hierarchy closure.

## ADM synchronization lane

Existing canonical closure lane remains:
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/src/core/pillar212_adm_decomposition.py`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/src/core/adm_quantitative_closure.py`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/src/core/wdw_full_5d.py`

This sprint does not re-open or weaken the existing ADM closure claims; it
only updates gap labels in the derivation ledger.

## Falsifiability additions

New break handles are added in:
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/1-THEORY/HOW_TO_BREAK_THIS.md`

Each added handle corresponds to a concrete mutation and test failure target.
