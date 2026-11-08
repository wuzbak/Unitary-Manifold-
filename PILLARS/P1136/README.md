# Pillar 1136 — Planar radion scalar energy balance

🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM

**Status:** Restricted symbolic balance identity and finite-difference
diagnostic in the massless, zero-vector, transversely isotropic planar sector.
**Date:** 2026-11-08
**Source module:** `src/core/pillar_1129_1168/pillar1136_planar_radion_scalar_energy_balance.py`
**Implementation:** `src/physics/planar_radion/evolution.py`
**Tests:** `tests/test_pillar1136_planar_radion_scalar_energy_balance.py`
**Technical note:** `docs/physics/PLANAR_RADION_DYNAMICS.md`
**PsiCat article:** `7-OUTREACH/A Z PsiCat Literature/Articles/article-357-p1136-radion-energy-balance.md`
**Tracker:** `docs/mas_tracker.yml`

## Result

For the reduced scalar equation

\[
\partial_t(r^2\psi_t)-\partial_x(r^2\psi_x)=0,
\]

the local energy balance is

\[
\partial_t\!\left[\frac{r^2}{2}(\psi_t^2+\psi_x^2)\right]
-\partial_x(r^2\psi_t\psi_x)
=r r_t(\psi_x^2-\psi_t^2).
\]

The periodic boundary flux integrates to zero, but radion work generally does
not. Therefore the radion-weighted scalar energy is not generally conserved.
The implementation reports the energy and work rate using the same centered
spatial derivative as the evolution solver; this is a finite-grid diagnostic,
not an exact discrete conservation theorem.

## Evidence and limits

The certificate checks the local identity by symbolic substitution of the
reduced scalar equation. The focused tests cover that residual, the budget on
the exact homogeneous branch \(r^2=t,\ \psi=q\ln t\), rejection of non-finite
arithmetic, and the pillar's fail-closed status packet. These tests were added
but could not be executed in the current environment because NumPy, SymPy, and
pytest are unavailable.

This result does not establish global existence, stability outside the
declared symmetry sector, vector or orbifold evolution, empirical confirmation,
or framework-level action-to-evolution closure. Pillar 1130's
`T_RELAXATION_LAW_DECLARED_NOT_DERIVED` and
`PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED` obligations remain open. No hardgate
label, TOE score, or observational falsifier changes.
