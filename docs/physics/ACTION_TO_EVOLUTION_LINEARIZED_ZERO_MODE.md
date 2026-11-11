<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# Action-derived linearized radion–gauge evolution

## Result and perimeter

Pillar 1138 derives coordinate-time equations from the quadratic expansion of
the massless Einstein-frame circle action

\[
S=\int d^4x\sqrt{-g}\left[
R-\frac32(\partial\psi)^2-\frac14\lambda^2e^{3\psi}F_{\mu\nu}F^{\mu\nu}
\right].
\]

Expand around \(g_{\mu\nu}=\eta_{\mu\nu}\), \(\psi=\psi_0+\epsilon\chi\),
and \(B_\mu=\epsilon A_\mu\), with constant \(\psi_0\), zero gauge
background, no radion potential, and fields depending on physical time \(t\)
and one spatial coordinate \(x\). For \(Z=\lambda^2e^{3\psi_0}>0\), the
quadratic matter action per unit transverse area is

\[
\mathcal L^{(2)}
=\frac32(\chi_t^2-\chi_x^2)
+\frac Z2\left[E_x^2+A_{y,t}^2+A_{z,t}^2-A_{y,x}^2-A_{z,x}^2\right],
\qquad E_x=A_{x,t}-A_{0,x}.
\]

The expansion itself verifies that radion dependence in \(e^{3\psi}F^2\)
first contributes beyond quadratic order. The radion and transverse gauge
polarizations therefore obey

\[
\chi_{tt}-\chi_{xx}=0,\qquad
A_{y,tt}-A_{y,xx}=A_{z,tt}-A_{z,xx}=0.
\]

Varying \(A_0\) and \(A_x\) gives the longitudinal Maxwell constraint and
evolution equation,
\[
\partial_x E_x=0,\qquad \partial_t E_x=0.
\]
Thus the longitudinal electric field is a spatially and temporally constant
constraint mode, not a local propagating degree of freedom in this
one-dimensional dependence class. The scalar and transverse gauge modes have
the null principal symbol \(\omega^2-k^2\), hence \(\omega^2=k^2\). The
coefficient \(Z\) is positive for nonzero \(\lambda\) and \(\phi_0=e^{\psi_0}>0\).

The symbolic certificate derives these equations by Euler variation of the
quadratic action and checks the action expansion, constraint identities, and
mode symbol. Matter stress begins at quadratic perturbation order, so this
does not solve nonlinear gravitational backreaction; the metric perturbation
is not part of this certificate.

## Evidence boundary

This is a linearized, zero-mode, circle-reduced result on a fixed Minkowski
background. It does not derive the repository's separate relaxation-time
law, establish nonlinear or full \(3+1\) evolution, include the \(Z_2\)
orbifold, prove global existence, or close the framework-level
action-to-evolution obligations. Those remain open; the action-to-evolution
contract must not be promoted to closure-ready on this result.

Run the focused checks from the repository root:

```bash
python -m pytest tests/test_pillar1138_action_derived_linearized_zero_mode_evolution.py \
  tests/test_pillar1137_planar_radion_kasner_relations.py \
  tests/test_action_to_evolution_contract.py \
  tests/test_action_to_evolution_el_mismatch_certificate.py -q
```
