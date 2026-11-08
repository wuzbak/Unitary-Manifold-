# The Radion Does Work: An Energy Balance for a Restricted Scalar Sector

*Merlin/PsiCat Rewrite v1 · Series/Season One*
*AxiomZero Technologies & Consulting, SPC commissioned work: Edited and written by PsiCat Ai.*
*Date: November 8, 2026*
*Grounded rewrite source: `/7-OUTREACH/substack/research/p1136-planar-radion-energy-balance-brief.md`*
*Epistemic status: a restricted symbolic identity and numerical diagnostic. It is not a new hardgate physics claim, an empirical result, or a framework-level closure.*
*Provenance: this article summarizes Pillar 1136 and its technical derivation. No external PsiCat runtime, experiment, independent scientific review, or fresh test execution is claimed.*

🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM

## A conservation question with a moving answer

When a field evolves in a changing geometry, asking whether its energy is
conserved is not a formality. The geometry can exchange energy with the field.
In the Unitary Manifold repository's recently registered planar radion
calculation, the scalar propagates while the effective transverse area changes.
The useful question is therefore not “Did we find a conserved scalar energy?”
It is “What is the balance law, including the work done by the radion?”

For the restricted sector in question, the scalar equation takes the
divergence form

\[
\partial_t(r^2\psi_t)-\partial_x(r^2\psi_x)=0,
\]

where \(r\) is the planar area scale and \(\psi\) is the radion scalar. Multiply
by \(\psi_t\), and the equation becomes

\[
\partial_t\!\left[\frac{r^2}{2}(\psi_t^2+\psi_x^2)\right]
-\partial_x(r^2\psi_t\psi_x)
=r r_t(\psi_x^2-\psi_t^2).
\]

The left side contains the time derivative of a radion-weighted energy and a
spatial flux. With periodic boundaries, the flux integrates to zero. The
right side is work exchanged with the evolving radion. It can be positive or
negative depending on the state, so neither monotonic decay nor monotonic
growth follows.

## A small, checkable contribution

Pillar 1136 adds a diagnostic that reports this integrated energy and work
rate from a solver state. Its spatial derivative is the same centered
finite-difference stencil used by the evolution code. That makes it useful
for interpreting simulations, but it does not make the discrete update obey
an exact conservation identity: finite differences do not inherit every
continuum product rule. The helper also rejects arithmetic overflow rather
than returning a success-shaped non-finite budget.

The exact homogeneous branch offers a simple unit test. For \(r^2=t\) and
\(\psi=q\ln t\) on a \(2\pi\)-periodic interval, the energy is
\(E=\pi q^2/t\), and its derivative is \(-\pi q^2/t^2\). The computed radion
work rate gives that same value. Separately, a symbolic residual substitutes
the reduced scalar equation into the local identity and should simplify to
zero. The new tests encode these checks; the current environment lacked
NumPy, SymPy, and pytest, so they were not run for this change.

This is deliberately not a claim that the Unitary Manifold has passed a
general conservation test. It is a careful accounting identity within an
already restricted model. The radion-work term is the point: omitting it would
mistake energy exchange for a violation or, worse, assert conservation where
the equations do not.

## What remains open

This calculation stays inside the massless, zero-vector, transversely
isotropic planar circle sector. It does not establish global existence,
stability under symmetry-breaking perturbations, gauge-field evolution,
\(Z_2\)-orbifold dynamics, or general five-dimensional evolution. Nor does it
close Pillar 1130's declared relaxation-law or framework physical-time
obligations. There is no observational prediction here and no change to the
framework's hardgate labels, TOE score, or falsification conditions.

More broadly, the repository describes a 5D Kaluza--Klein research framework,
not a completed derivation of every claimed physical sector. The current
formal entry point leaves equivalence between the symmetry-reduced evolution
and full Lorentzian field equations open. The foundation reassessment
withdraws the earlier fixed-plane odd-field photon argument and the claimed
reciprocal suppression bound; photon origin and action-to-evolution
equivalence remain unresolved. The current status also says the candidate
\(\alpha_{\rm GUT}=N_c/K_{\rm CS}\) is postulated, not derived from the stated
action, because conditional orbifold matching leaves independent bulk and
boundary kinetic coefficients.

The CMB acoustic-peak amplitude deficit (roughly a factor of \(4\)–\(7\))
remains open; reproducing an input pivot amplitude is calibration, not an
independent prediction. Likewise, \(n_w=5\) is conditional on the restricted
candidate set \(\{5,7\}\) and a boundary rule, not a uniqueness result from
first principles alone. The registered birefringence values near
\(0.273^\circ\) and \(0.331^\circ\) remain unconfirmed future predictions.
The repository's stated primary falsifier is unchanged: a LiteBIRD value
outside \([0.22^\circ,0.38^\circ]\), or in the predicted gap
\([0.29^\circ,0.31^\circ]\), falsifies the braided-winding mechanism.
The DESI Year 2 equation-of-state tension with the \(w_a=0\) model expectation
also remains tracked and unresolved. This energy-balance sprint changes none
of those claims, gaps, or thresholds.

That modest boundary is scientifically useful. A transparent source term,
an inspectable implementation, and explicit tests are a better foundation
for later work than a broader conservation claim unsupported by the model.

### Gate Certification (v1)

This is an editorial self-check, not an external factual certification,
scientific peer review, or certification of the model.

1. **Grounding and fidelity:** equations, implementation scope, and test
   limits match the Pillar 1136 brief and technical note.
2. **Accuracy and epistemic restraint:** radion work is explicit; no
   conservation law, discrete exactness, global theorem, or broad framework
   closure is claimed.
3. **Cross-audience clarity:** the balance equation is stated, each term is
   interpreted, and the unrun tests and open boundaries are disclosed.

— PsiCat
