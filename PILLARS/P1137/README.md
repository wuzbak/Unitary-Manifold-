# Pillar 1137 — Planar radion Kasner relations

🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM

**Status:** Exact generalized-Kasner identities on the rolling homogeneous
branch of the massless, zero-vector, transversely isotropic circle sector.
**Date:** 2026-11-10
**Source module:** `src/core/pillar_1129_1168/pillar1137_planar_radion_kasner_relations.py`
**Derivation:** `src/physics/planar_radion/derivation.py`
**Tests:** `tests/test_pillar1137_planar_radion_kasner_relations.py`
**Technical note:** `docs/physics/PLANAR_RADION_DYNAMICS.md`

For \(r^2=at+b>0\), \(a\ne0\), the exact branch implies
\[
p_\parallel+2p_\perp=1,\qquad
p_\parallel^2+2p_\perp^2+\frac32q_\psi^2=1.
\]
The identities are checked symbolically and for representative rational
parameters with both signs of \(a\).

This restricted identity does not establish stability or genericity outside
the homogeneous branch, global existence, a Lean proof, empirical
confirmation, or framework-level closure. The flat `src.core.pillar1137_*`
import resolves through the `src.core` shard search path to the tracked
`pillar_1129_1168` source file; the focused regression exercises that import.
