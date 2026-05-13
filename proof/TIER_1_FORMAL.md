# TIER_1_FORMAL.md — Isolated Mathematical Core

This document defines the strict mathematical evaluation surface for the Unitary Manifold framework. It is intentionally limited to the formal 5D Kaluza–Klein construction, executable algebraic verification, and numerical consistency checks.

For first-pass mathematical review, use only:

1. `proof/metric.py`
2. `proof/evolution.py`
3. `proof/ALGEBRA_PROOF.py`
4. `proof/VERIFY.py`
5. `1-THEORY/UNIFICATION_PROOF.md`
6. `FALLIBILITY.md`

## Formal Scope

The core ansatz is the 5D Kaluza–Klein metric with compact extra dimension,
\[
G_{AB} =
\begin{pmatrix}
g_{\mu\nu} + \lambda^2 \phi^2 B_\mu B_\nu & \lambda \phi^2 B_\mu \\
\lambda \phi^2 B_\nu & \phi^2
\end{pmatrix},
\]
with projection and closure relations implemented in `metric.py` and `evolution.py`.

The integer pair \((n_1, n_2) = (5, 7)\) sets the topological sector used in executable checks. In the canonical chain,
\[
k_{\mathrm{CS}} = n_1^2 + n_2^2 = 74,
\]
and downstream observables are evaluated by deterministic scripts (`ALGEBRA_PROOF.py`, `VERIFY.py`) against explicit bounds.

## Verification Commands

Run these commands from repository root:

```bash
python proof/VERIFY.py
python proof/ALGEBRA_PROOF.py
python -m pytest tests/test_metric.py tests/test_evolution.py tests/test_fixed_point.py -q
```

A valid run for this isolated surface requires successful execution with no failing assertions.

## Epistemic Boundary

This directory is a formal verification entry point, not a complete map of the repository. Adjacent research tracks and governance frameworks are documented elsewhere and are intentionally excluded from this Tier-1 surface.

Known limits, open problems, and non-claims are cataloged in `FALLIBILITY.md` and must be used as part of any technical assessment.
