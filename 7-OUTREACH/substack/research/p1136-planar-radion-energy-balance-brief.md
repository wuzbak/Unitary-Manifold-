# Research brief: scalar energy exchange in the planar radion sector

**Date:** 2026-11-08
**Status:** Restricted theoretical identity and numerical diagnostic; not a hardgate physics claim.
**Pillar:** 1136 (v38.7, Sprint DC)
**Implementation:** `src/physics/planar_radion/evolution.py`
**Derivation:** `src/physics/planar_radion/derivation.py`

## Question

What quantity should be monitored when a scalar propagates in the already
specified planar Einstein-radion sector, where the effective transverse area
changes in coordinate time? A bare flat-space scalar energy would omit the
radion's changing measure and could create a misleading conservation claim.

## Derivation

Within the massless, zero-vector, transversely isotropic circle reduction,
the scalar equation can be written as

\[
\partial_t(r^2\psi_t)-\partial_x(r^2\psi_x)=0.
\]

Multiplication by \(\psi_t\) yields

\[
\partial_t\!\left[\frac{r^2}{2}(\psi_t^2+\psi_x^2)\right]
-\partial_x(r^2\psi_t\psi_x)
=r r_t(\psi_x^2-\psi_t^2).
\]

On a periodic spatial domain, the integrated flux term vanishes. The remaining
radion-work term generally does not, so the scalar energy is not generally
conserved. The sign of the work is state-dependent; the result does not say
that energy monotonically decays or grows.

## What changed

The solver now exposes `planar_scalar_energy_budget`, returning the
radion-weighted scalar energy and its integrated work rate. It uses the same
centered spatial derivative as the solver. A symbolic residual helper and
Pillar 1136 provide a fail-closed check of the continuum identity. The focused
tests include the exact homogeneous branch \(r^2=t,\ \psi=q\ln t\), for which
\(E=\pi q^2/t\) and \(dE/dt=-\pi q^2/t^2\) on a \(2\pi\)-periodic interval,
as well as explicit rejection of arithmetic overflow in the diagnostic.

## Boundary of the claim

This is a diagnostic and exact identity within the existing restricted model,
not a new empirical prediction, exact conservation statement for the
discretized solver, global-existence theorem, or stability analysis. It does
not address gauge fields, the \(Z_2\) orbifold, generic polarizations, or the
full 5D field equations. Pillar 1130's relaxation-law and framework physical-
time obligations remain open. No hardgate physics label, TOE score, or
observational falsifier changes.

## Where the wider framework stands

The Unitary Manifold is a 5D Kaluza--Klein research framework; repository
registration and passing software checks are not, by themselves, scientific
closure. The current formal entry point calls the evolution implementation
symmetry-reduced and leaves its equivalence to the full Lorentzian field
equations open. The foundation reassessment also records that the earlier
fixed-plane odd-field photon argument and a proposed reciprocal suppression
bound do not establish their historical conclusions. Photon origin and
action-to-evolution equivalence remain open.

The current status record further qualifies the candidate
\(\alpha_{\rm GUT}=N_c/K_{\rm CS}\) as postulated rather than derived from the
stated 5D action: conditional orbifold matching has independent bulk and
boundary kinetic coefficients. The CMB acoustic-peak amplitude deficit of
roughly \(4\)–\(7\) remains unresolved; matching the pivot amplitude to an
observational input is calibration, not an independent prediction. The
winding selection \(n_w=5\) is conditional on the restricted candidate set
\(\{5,7\}\) and its boundary rule, not a standalone first-principles
uniqueness proof.

The registered birefringence values, approximately \(0.273^\circ\) and
\(0.331^\circ\), remain future-facing predictions rather than current
confirmation. Under the repository's stated falsification condition, a
LiteBIRD result outside \([0.22^\circ,0.38^\circ]\), or inside the predicted
gap \([0.29^\circ,0.31^\circ]\), falsifies the braided-winding mechanism.
The DESI Year 2 equation-of-state tension with the \(w_a=0\) model expectation
is also tracked, not resolved, by this sprint. These open issues are unchanged.
See `STATUS.md`,
`proof/TIER_1_FORMAL.md`, and `docs/TRUTH_LAYER.md#foundation-reassessment`
for the canonical scope and evidence boundary.

The required Python packages were absent in the authoring environment, so
focused tests and full regression were not run. The test code and exact
commands are in the repository; no test-pass claim is made here.

### References

- [`PLANAR_RADION_DYNAMICS.md`](../../../docs/physics/PLANAR_RADION_DYNAMICS.md)
- [`Pillar 1136`](../../../PILLARS/P1136/README.md)
- [`Pillar 1136 implementation`](../../../src/core/pillar_1129_1168/pillar1136_planar_radion_scalar_energy_balance.py)
