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

## Theorem Labeling Key

Results referenced from this Tier-1 surface carry the following epistemic labels:

| Label | Meaning |
|-------|---------|
| **PROVED** | Formally derived from the 5D metric ansatz with no free parameters; executable test passes. |
| **DERIVED** | Algebraically derived given stated assumptions; result is deterministic but depends on the ansatz or an upstream proved step. |
| **GEOMETRICALLY MOTIVATED** | Identification supported by dimensional / group-theoretic reasoning (e.g., n_w KK species → SU(n_w)); not a rigorous derivation from the 5D action. |
| **CONDITIONAL THEOREM** | Formally derived given a named axiom or postulate; result is only as strong as the axiom. |
| **CONJECTURE** | Plausible but not yet derived; flagged in `FALLIBILITY.md`. |

The n_w = 5 uniqueness result is a **CONDITIONAL THEOREM** (conditional on Axiom A, which is itself now DERIVED from the 5D CS action — see `nw5_pure_theorem.py`). The SU(5) gauge-group identification from n_w = 5 KK species is **GEOMETRICALLY MOTIVATED** (minimality argument). All downstream RGE predictions are **DERIVED** given SU(5).
