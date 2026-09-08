# Review Packet — APS / Orbifold / Dirac Boundary Machinery

## Claim cluster

The current claim cluster is not “full first-principles closure.” It is the narrower statement that the repository now exposes the exact burden around APS η-invariants, orbifold parity, and Dirac-spectrum reasoning without hiding the remaining gaps.

## Assumptions boundary

Start with:

- `lean4/UnitaryManifold/NWUniquenessHonest.lean`
- `lean4/UnitaryManifold/DiracOrbifoldSpectrum.lean`
- `docs/TRUTH_LAYER.md`

Key honesty boundary:

- APS η-invariant formalization remains an explicit named gap in Lean.
- Dirac orbifold arithmetic proxies are labelled as proxies, not as a full boundary-value proof.
- Deriving `N_gen = 3` from first principles remains open.

## Lean surface

Primary Lean files:

- `lean4/UnitaryManifold/NWUniquenessHonest.lean`
- `lean4/UnitaryManifold/DiracOrbifoldSpectrum.lean`

Read these as an epistemic map:

- named axioms,
- named open gaps,
- theorem/proxy separation.

## Executable companion surface

Primary Python artifacts:

- `src/core/aps_eta_invariant.py`
- `src/core/pillar828_aps_eta_invariant_lean4_bridge.py`
- `src/core/yukawa_orbifold_bc_texture.py`
- `src/core/nw_circularity_audit.py`

Primary tests:

- `tests/test_pillar828_aps_eta_invariant_lean4_bridge.py`
- `tests/test_yukawa_orbifold_bc_texture.py`
- `tests/test_nw_circularity_audit.py`

These executable artifacts may validate calculations or honesty boundaries, but they do not by themselves discharge the missing Lean/Mathlib burden.

## Exact review question

Please answer one or more of the following:

1. Is the named APS burden stated at the right mathematical level?
2. Is any arithmetic proxy being mistaken for a Dirac/operator proof?
3. Is there a cleaner decomposition of the remaining orbifold/APS proof distance?
4. Is there an overlooked counterexample to the current conditional chain?

## Explicit falsifier / blocker request

A successful review packet response is one that either:

- finds a real mathematical error,
- isolates a missing assumption more sharply,
- supplies a smaller formalization route for APS/boundary machinery,
- or confirms that the current honesty boundary is correctly stated.
