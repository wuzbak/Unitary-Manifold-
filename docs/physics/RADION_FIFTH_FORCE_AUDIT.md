<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# Radion fifth-force audit: conditional circle sector

**Decision: no Tier 1 promotion, no new UM physical exclusion.** This note
derives an exact, deliberately limited stabilized interval vacuum, a
conditional matter charge and finite-body response, and identifies what the
current action does not determine. It is not a realistic Standard Model
orbifold reduction, a data fit, or a certification of the Walker--Pearson
physical-time flow. The relevant
current foundation boundaries are in [Tier 1](../../proof/TIER_1_FORMAL.md)
and the [truth layer](../TRUTH_LAYER.md#foundation-reassessment).

## 1. Action, normalization, and a mass calculation

The zero-mode **circle**, Einstein-frame action in
`src/core/action_derived_flow.py`, omitting its optional potential, is

\[
 S={M_{\rm Pl}^2\over 2}\int d^4x\sqrt{-g}
 [R-\tfrac32(\partial\psi)^2-\tfrac14\lambda^2e^{3\psi}F^2],
 \quad \psi=\ln\phi,\quad M_{\rm Pl}^{-2}=8\pi G.
\]

The source implementation suppresses the overall gravitational normalization;
we restore it consistently here. This is not a derivation of the projected-out
orbifold vector or a matter action. In particular, pure Einstein--Hilbert
circle reduction supplies no stabilizing radion potential or nonzero radion
mass. The canonical scalar is
\(\varphi=\sqrt{3/2}\,M_{\rm Pl}(\psi-\psi_0)\).

The module optionally **adds**, rather than derives, a potential
\(U(\phi)=m_{\rm in}^2(\phi-\phi_0)^2/(2\phi)\) inside the square brackets.
At \(\phi=\phi_0>0\), \(U=U_{,\psi}=0\) and
\[
 U_{,\psi\psi}=m_{\rm in}^2\phi_0,\qquad
 m_{\rm physical}^2=\frac{U_{,\psi\psi}}3
 =\frac{m_{\rm in}^2\phi_0}{3}.
\]
The last equality follows also from the source equation
\(3\Box\psi=U_{,\psi}\) at \(F=0\). For example, at \(\phi_0=1\),
the physical mass is \(m_{\rm in}/\sqrt3\), not the supplied parameter.
This result is specific to this optional potential and its normalization;
it cannot be transferred to a differently normalized GW or RS potential.
`reduced_action_radion_mass_squared` implements the scoped relation.

The same vacuum \(\phi_0\) with \(m_{\rm in}=0\) or \(m_{\rm in}>0\)
already gives different masses. The reduced vacuum action therefore does
not fix a unique fifth-force range. Background stationarity
\(U_{,\psi}(\psi_0)=0\) does not eliminate the perturbation sourced by matter.
The historical `gw_stabilizer.py` statement to the contrary is not a
fifth-force proof. Likewise, the cylinder condition \(\partial_5=0\) does
not imply \(\partial_\mu\phi=0\).

### An explicit stabilized 5D interval counterexample

The following is a complete **specified vacuum model**, not a derivation of
the repository's optional potential or a proposed realistic cosmology. Take
\(0\leq y\leq L\), \(M_5^3>0\), a real bulk scalar \(\chi\), and
Dirichlet boundary values \(\chi(0)=v_0\), \(\chi(L)=v_1\). With the
outward-normal convention for \(K\), include the Gibbons--Hawking term:
\[
 S_5=\int d^5x\sqrt{-G}\left[\frac{M_5^3}{2}R_5
       -\frac12(\partial\chi)^2-\Lambda_5\right]
     +M_5^3\sum_{i=0,L}\int_i d^4x\sqrt{-\gamma_i}K_i
     -\sum_A m_{J,A}\int_{\text{boundary}}ds_{\gamma}.
\]
The last term specifies fixed-mass point particles confined to a boundary;
it is absent in the vacuum solution. Free boundary metric variation gives
zero extrinsic curvature in the vacuum, and fixed scalar boundary values
give \(\delta\chi=0\) at both ends. This is the interval convention;
doubling to an orbifold covering space must be accompanied by consistent
normalization.

Set \(\chi=v_0+wy\), \(w=(v_1-v_0)/L\ne0\), and
\[
 ds_5^2=e^{-\psi}g_{\mu\nu}^E dx^\mu dx^\nu+e^{2\psi}dy^2,
 \quad M_{\rm Pl}^2=M_5^3L.
\]
The proper interval length is \(Le^\psi\). Substitution into the vacuum
action gives the Einstein-frame potential
\[
 V_E(\psi)=L\left[\Lambda_5e^{-\psi}
                     +\frac12w^2e^{-3\psi}\right],
 \qquad
 S_4=\int\sqrt{-g_E}\left[
 \frac{M_{\rm Pl}^2}{2}R_E-\frac{3M_{\rm Pl}^2}{4}(\partial\psi)^2
 -V_E\right].
\]
For \(\Lambda_5<0\), the stationary point and canonically normalized
radion mass are
\[
 e^{2\psi_0}={3w^2\over2|\Lambda_5|},\quad
 V_0=-Lw^2e^{-3\psi_0},\quad
 m_\varphi^2={V_{E,\psi\psi}(\psi_0)\over(3/2)M_{\rm Pl}^2}
 ={2w^2e^{-3\psi_0}\over M_5^3}
 =-{2V_0\over M_{\rm Pl}^2}>0.
\]
This is also an **on-shell 5D vacuum**: \(K_{\mu\nu}=0\);
\(\Box_5\chi=0\); and the trace-reversed Einstein equations
\(M_5^3R_{MN}=\partial_M\chi\,\partial_N\chi+
\tfrac23\Lambda_5G_{MN}\) give the same radius from the \(yy\) equation and
\(R_{\mu\nu}(g_E)=V_0g^E_{\mu\nu}/M_{\rm Pl}^2\) from the 4D equations.
The spacetime is AdS, with
\(\ell_{\rm AdS}^2=-3M_{\rm Pl}^2/V_0\) and
\(m_\varphi^2\ell_{\rm AdS}^2=6\). These identities are checked
symbolically in `tests/test_isl_yukawa.py`.

The brane worldline action gives \(ds_\gamma=e^{-\psi/2}ds_E\), hence
\(m_A^E=m_{J,A}e^{-\psi/2}\) and \(q_A=-1/\sqrt6\) for the stated
fixed Jordan mass. This is an explicit normalized **probe** charge, not a
calculation of nuclear, atomic or Standard Model sensitivities. In contrast,
an independent massless bulk scalar mode with Neumann modes \(n\ge1\)
has \(m_{n,E}=n\pi e^{-3\psi/2}/L\) and \(q_n=-\sqrt{3/2}\);
different matter actions give different charges. Boundary sources also
produce nonzero junction stress, so the vacuum ansatz is not a solution of
the sourced experiment without solving its backreaction and KK modes.

#### An explicit conditional boundary matter sector

The point-particle action can be replaced by a specified renormalized
four-dimensional matter theory on the \(y=0\) boundary,
\[
 S_{\rm m}=\int_{y=0}d^4x\sqrt{-\gamma}\,
 \mathcal L_{\rm SM}(\gamma_{\mu\nu},
   A_\mu,\Psi,H;\,g_i,y_{ij},v_J,\lambda_H,\theta_{\rm QCD},\ldots).
\]
Here the Lagrangian contains the usual gauge kinetic and fermion terms,
Yukawa interactions and Higgs potential
\(\lambda_H(H^\dagger H-v_J^2/2)^2\); the ellipsis denotes the
remaining Standard Model couplings, not an asserted 5D origin. This example
**assumes** the renormalized dimensionless parameters and the
dimensionful Jordan-frame input \(v_J\), defined at a fixed physical
Jordan-frame renormalization scale, are independent of \(\psi\) and of
the boundary value of \(\chi\). It also assumes there are no direct
\(\chi\)-matter or radion-dependent boundary-kinetic couplings. These are
model inputs, not consequences of the UM vacuum action.

With \(\gamma_{\mu\nu}=e^{-\psi}g^E_{\mu\nu}\), a local Jordan-frame
clock has \(ds_J=e^{-\psi/2}ds_E\). Each isolated, weakly
self-gravitating composite body's Jordan rest mass \(m_{J,A}\), including
its electromagnetic and nuclear binding contributions, is then independent
of a constant \(\psi\) **under those assumptions**. Thus
\[
 m_{E,A}=e^{-\psi/2}m_{J,A},\qquad
 q_A=M_{\rm Pl}{\partial\ln m_{E,A}\over\partial\varphi}
 =-{1\over\sqrt6},\qquad \alpha_{AB}=2q_Aq_B={1\over3}.
\]
QCD dimensional transmutation does not by itself generate a differential
charge in this specified model: the Jordan-frame gauge coupling and
renormalization reference scale were fixed. A radion-dependent UV matching,
boundary gauge term, Higgs parameter, or renormalization input changes that
conclusion. This does not derive actual material sensitivities in UM; it
exhibits one explicit, universal-charge matter choice and the inputs on
which it depends.

For comparison, in a **separately assumed flat, low-energy 4D linear
regime**, the canonically normalized scalar obeys
\[
 (\nabla^2-m_\varphi^2)\delta\varphi={q\rho\over M_{\rm Pl}},
 \qquad
 \delta\varphi(\boldsymbol{x})=-{q\over4\pi M_{\rm Pl}}
 \int d^3x'\,{\rho(\boldsymbol{x}')e^{-|\boldsymbol{x}-\boldsymbol{x}'|/\ell}
                   \over|\boldsymbol{x}-\boldsymbol{x}'|}.
\]
This produces the force law and finite-body integrals below with
\(\alpha=2q_Aq_B\). It is not a solution of the full 5D sourced junction
problem: the actual brane stress perturbs the bulk metric, scalar and KK
tower, and the AdS vacuum's curvature cannot be ignored at its radion
range. Establishing a realistic 5D source response requires solving those
linearized bulk equations and boundary conditions, matching the Green
function and its normalization, and verifying the 4D/KK hierarchy.

The radion in this model has positive curvature in the displayed homogeneous
sector; stability of the full 5D fluctuation spectrum has not been shown.
Its range is \(\ell_{\rm AdS}/\sqrt6\): a flat-space Yukawa law at distances
of order that range is **not** justified in this AdS vacuum. A nearly flat
stabilized vacuum, realistic matter, screening, all KK modes, and the actual
boundary response remain open. Thus the finite-body flat-space formulas
below are separately assumed examples, not an experimental prediction
of this AdS construction.

### A separate exactly flat, warped interval background

The AdS obstruction is not a no-go theorem for every stabilized 5D model.
Consider the same interval and Gibbons--Hawking convention, but now take
\[
 W(\chi)=6M_5^3k-u\chi^2,\qquad
 V(\chi)={W_{,\chi}^2\over8}-{W^2\over6M_5^3},
 \qquad k,u>0,
\]
and add boundary potentials
\[
 U_0={W\over2}+{\lambda_0\over2}(\chi-v_0)^2,\quad
 U_L=-{W\over2}+{\lambda_L\over2}(\chi-v_L)^2,\quad
 \lambda_0,\lambda_L>0,\quad v_0>v_L>0.
\]
They enter as \(-\sum_i\int\sqrt{-\gamma_i}U_i\); the scalar and gravitational
bulk actions are otherwise those above. A classical vacuum background is
\[
 ds_5^2=e^{-2A(y)}\eta_{\mu\nu}dx^\mu dx^\nu+dy^2,\quad
 \chi=v_0e^{-uy},\quad
 A=ky-{v_0^2\over12M_5^3}(1-e^{-2uy}),\quad
 L={1\over u}\ln{v_0\over v_L}.
\]
The four-dimensional slices are exactly Minkowski. In the chosen interval
normalization, the trace-reversed Einstein equations and bulk scalar
equation hold, as do
\[
 M_5^3(K_{\mu\nu}-K\gamma_{\mu\nu})+U_i\gamma_{\mu\nu}=0,\qquad
 n^M\partial_M\chi+U_{i,\chi}=0.
\]
The outward normal is negative at \(0\) and positive at \(L\). The bulk and
both boundary equations are checked symbolically in
`tests/test_isl_yukawa.py`, including finite positive \(\lambda_i\).
The displayed radius is fixed within this background branch by the selected
endpoint values; uniqueness and stability for all solutions are not proven.
The brane tensions are tuned to the bulk potential, and generic additional
vacuum energy would spoil the flatness without retuning. This is a separate
specified model, not a derivation of the optional circle potential or of
the UM \((5,7)\) sector.

The full backreacted Einstein-frame Planck coefficient for this background is
\(M_{\rm Pl}^2=M_5^3\int_0^L e^{-2A(y)}dy\). For
\(v_0^2/M_5^3\ll1\) and negligible scalar backreaction, the conventional
leading Randall--Sundrum approximation with \(\mu=e^{-kL}\) gives
\(M_{\rm Pl}^2\simeq M_5^3(1-\mu_0^2)/(2k)\). A commonly used modulus
normalization then gives fixed-mass IR/UV brane charges approximately
\(q_{\rm IR}\simeq1/(\sqrt6\mu_0)\) and
\(q_{\rm UV}\simeq\mu_0/\sqrt6\), respectively. These depend on matter
location and assumptions and are **not** certified eigenmode charges:
the coupled metric--scalar fluctuation problem, boundary stiffness effects,
and kinetic normalization must be independently solved. See the original
[stabilization proposal](https://arxiv.org/abs/hep-ph/9907447) and the
[coupled perturbation treatment](https://arxiv.org/abs/hep-th/0001092).
An earlier claim of a large kinetic correction in
[Cline and Firouzjahi](https://arxiv.org/abs/hep-ph/0006037v4) was
**withdrawn** in its final version; it is not evidence for that correction.

We can nevertheless compute a more explicit **stiff-boundary probe**.
Take \(\lambda_i\to\infty\), fix the two scalar values, discard scalar
backreaction on \(A=ky\), and set \(\epsilon=u/k\),
\(\mu=e^{-kL}\). The bulk scalar solves
\(\chi=ae^{(4k+u)y}+be^{-uy}\), with
\[
 a={v_L-v_0\mu^\epsilon\over\mu^{-4-\epsilon}-\mu^\epsilon},
 \qquad b=v_0-a.
\]
The on-shell scalar bulk action, the quadratic-in-\(\chi\) pieces of the
tuned boundary tensions, and the tuned RS vacuum terms give the Jordan-frame
potential
\[
 V_J(\mu)=
 {k(2+\epsilon)\mu^4(v_L-v_0\mu^\epsilon)^2
 \over1-\mu^{4+2\epsilon}}.
\]
The denominator and boundary terms matter; this is not obtained by merely
assuming a quartic potential. At
\(\mu_0^\epsilon=v_L/v_0\), \(V_J=V'_J=0\). A Weyl conversion to the
Einstein frame multiplies \(V_J\) by
\([(1-\mu_0^2)/(1-\mu^2)]^2\), which does not change the second derivative
at this zero-energy stationary point. If one also assumes the conventional
unstabilized-RS Einstein-frame modulus kinetic coefficient
\[
 \left({d\varphi\over d\mu}\right)^2_{\mu_0}
 ={3M_5^3\over k(1-\mu_0^2)},
\]
then the probe curvature is
\[
 m_{\rm probe}^2=
 {2k^2(2+\epsilon)\epsilon^2v_L^2\mu_0^2(1-\mu_0^2)
  \over3M_5^3(1-\mu_0^{4+2\epsilon})}>0.
\]
Symbolic tests check the scalar boundary-action identity and this normalized
curvature, and `stiff_wall_probe_radion_mass_squared` evaluates the
expression with input and floating-point checks. The result is a controlled
algebraic result for the specified frozen background and assumed kinetic
term; its accuracy as a full 5D eigenvalue is not yet demonstrated.
Weak backreaction, the stiff-wall approximation and an isolated mode are
necessary assumptions, not a substitute for checking coupled constraints and
kinetic mixing. For \(\mu_0\ll1\) and \(\epsilon\ll1\), this probe gives
\(m_{\rm probe}^2/(k\mu_0)^2\simeq(4/3)\epsilon^2v_L^2/M_5^3\);
this is an estimated hierarchy, not a validated full-spectrum result.
The coupled-mode calculation below goes beyond this probe, but does not
establish the complete matter response.

### Coupled scalar--metric eigenproblem: a conditional calculation

For the flat background above, consider the perturbation ansatz
\[
 ds^2=e^{-2A}(1-2F)\eta_{\mu\nu}dx^\mu dx^\nu+(1+4F)dy^2,
 \quad \chi=\bar\chi+\delta\chi,
\]
and the linear constraint
\(F'-2A'F=\bar\chi'\delta\chi/(3M_5^3)\). In the regular
sector where \(\bar\chi'\ne0\), set \(h=e^{-2A}F\),
\(p=e^{2A}/\bar\chi'^2\), and \(w=e^{4A}/\bar\chi'^2\). The
coupled scalar equation and finite-stiffness boundary conditions used here
reduce to the eigenvalue-dependent problem
\[
 -(ph')'+2A''ph=m^2wh,\qquad
 h'(0)=-{m^2\over\lambda_0}h(0),\quad
 h'(L)={m^2e^{2A(L)}\over\lambda_L}h(L).
\]
The \(\lambda_i\) are the additional stiffnesses in the **specific**
boundary potentials above, not arbitrary total boundary second derivatives.
Integration by parts gives
\[
 K=\int_0^L p\bigl(h'^2+2A''h^2\bigr)dy,\quad
 I=\int_0^Lwh^2dy+{w(0)h(0)^2\over\lambda_0}
                   +{w(L)h(L)^2\over\lambda_L},\quad
 K=m^2 I.
\]
Since \(A''=\bar\chi'^2/(3M_5^3)>0\), the displayed forms are positive
for nonzero regular real modes and positive stiffnesses. This is a
conditional scalar-sector statement, not a proof of full 5D stability,
absence of ghosts, or a full sourced propagator.

`flat_interval_scalar_mode` shoots this boundary-value problem for a
bracketed positive nodeless mode and checks its integrated identity.
The tests also independently discretize the same generalized eigenproblem
with finite elements, including its endpoint mass terms. At
\(M_5^3=k=1,\ u=0.3,\ v_0=0.2,\ L=2\), the stiff-wall mode has
\(m^2=3.00378828\times10^{-5}\), versus the probe value
\(2.9896719\times10^{-5}\). Equal stiffnesses 10, 1, and 0.1 give
respectively \(2.05759349\times10^{-5}\), \(5.36517630\times10^{-6}\),
and \(6.39278711\times10^{-7}\). These are dimensionless model examples,
not observed masses; agreement at this point is not a parameter sweep or
an independent derivation of the linearized equations.

For this action without boundary-localized kinetic terms, the proposed
physical-interval quadratic-action normalization is
\[
 N=\int_0^L e^{-2A}(\delta\chi^2+6M_5^3F^2)dy=9M_5^6K,
 \qquad q_i=-{M_{\rm Pl}F(y_i)\over\sqrt N},
\]
An independent check against the indexed rendering of
[Kofman--Martin--Peloso](https://arxiv.org/abs/hep-ph/0401189), especially
Eqs. 5, 18 and 29, maps their conformal-coordinate perturbations to
\(\Psi=-F,\Phi=2F\) and converts their doubled orbifold bulk integral to
one physical interval. It supports the coefficient \(6M_5^3\) and the
fixed-brane trace overlap above. The equality to \(9M_5^6K\) follows from
the constraint and background; the finite-stiffness endpoint terms enter
its equivalent on-shell \(9M_5^6m^2I\) form and must not be added again to
the original bulk norm. The endpoint-weighted product is also consistent
with the finite-boundary treatment in
[Girmohanta et al.](https://arxiv.org/abs/2404.05141v2). Direct retrieval
of these complete primary texts was unavailable in this session, so this
cross-check relies on indexed renderings; a complete independent
re-expansion of the action remains outstanding.

On these assumptions, fixed-Jordan-mass boundary matter without direct
\(\chi\) coupling gives \(q_0=-0.05536,\ q_L=-3.01088\) in the stiff
benchmark. A finite-element calculation independently evaluates the bulk
norm and overlaps for stiff and finite walls. The code labels these charges
conditional: the sourced brane-bending and tensor junctions, complete
propagator, and physical material matching have not been established.

With \(\alpha_{ij}=2q_iq_j\) for these conditional charges, the stiff
benchmark gives \(\alpha_{\rm UV,UV}\simeq0.0061\),
\(\alpha_{\rm UV,IR}\simeq0.33\) and \(\alpha_{\rm IR,IR}\simeq18.1\).
Matter localized on the IR boundary would thus couple far more strongly than
gravity, as in unstabilized warped models; a viable model must place or
screen Standard Model matter accordingly or add direct \(\chi\) couplings.
The benchmark mass is dimensionless, so no laboratory range or exclusion
follows. This is a restricted scalar-pole estimate, not the sourced
tensor-plus-scalar Green function.

Positive curvature of a restricted potential or eigenproblem is not a
complete 5D stability result. The scalar and tensor spectrum, action
normalization, 5D EFT hierarchy, and matter-sourced junction response remain
open. A flat background alone does not authorize applying either the AdS
mass or the surrogate laboratory calculation below to this model.

## 2. Couplings and the point-source calculation

Assume, in addition, nonrelativistic bodies whose Einstein-frame masses
\(m_A(\varphi)\) have scalar sensitivities
\(q_A=M_{\rm Pl}\partial_\varphi\ln m_A|_{\varphi_0}\). For a stable scalar
of mass \(m_\varphi\), linear response in an approximately flat spacetime,
unscreened point bodies, and \(r>0\),
\[
 V_{AB}(r)=-{Gm_Am_B\over r}
 [1+2q_Aq_Be^{-r/\ell}],\qquad
 \ell={\hbar\over m_\varphi c}.
\]
Differentiation gives
\[
 {\Delta F\over F_N}=2q_Aq_B(1+r/\ell)e^{-r/\ell}.
\]
The massless limit is \(\ell\to\infty\). The repository's
`yukawa_correction` and `fifth_force_signal_strength` return only the
potential factor; `yukawa_force_correction` evaluates the differentiated
point-source expression. Historical results using the old functions as
acceleration estimates should not be treated as observational exclusions.

As an explicit **conditional example**, if all point masses couple minimally
to the Jordan metric \(g_J=e^{-\psi}g_E\), then
\(m_A(\varphi)\propto e^{-\psi/2}\), \(q_A=-1/\sqrt6\), and the scalar
potential strength is \(2q_Aq_B=1/3\). This assumption is not established
for Standard Model bound bodies, an orbifold brane, or every model in the
repository. In contrast, an independently assumed matter action with
field-independent Einstein-frame masses has \(q_A=0\). Both examples share
the same vacuum gravity action, demonstrating why its gauge and scalar terms
alone do not determine the laboratory matter coupling.

For equal scalar sensitivities of the two test bodies, a universal scalar
force contributes equally at leading order, so their differential
acceleration vanishes even if the common force is nonzero. Non-universal
sensitivities require the actual matter and nuclear binding response; neither
the baryon-number coupling nor the nonminimal-composition expression in
`ep_violation.py` is derived by the circle action.

## 3. Source size and experimental comparisons

For an unscreened homogeneous sphere of radius \(R\), uniform scalar
charge per unit mass, and observation at \(r\geq R\), integrating the
Yukawa Green function gives the same exterior potential with its Yukawa
term multiplied by
\[
 {\cal F}(x)={3(x\cosh x-\sinh x)\over x^3},\quad
 x=R/\ell,\quad
 {\cal F}(x)=1+x^2/10+x^4/280+O(x^6).
\]
This factor belongs with \(e^{-r/\ell}\); evaluating them separately at
large \(x\) risks overflow. The formula is a homogeneous-sphere model, not
Earth's actual density and composition or a torsion-balance geometry.
For a spherical source, the leading differential signal depends on
\(2q_E(q_A-q_B){\cal F}(R_E/\ell)
(1+r/\ell)e^{-r/\ell}\), with the exact Eotvos denominator and
other effects retained where needed.

`homogeneous_sphere_yukawa_force_correction` evaluates this form factor
combined with the exponential, avoiding the large-\(R/\ell\) hyperbolic
overflow, and `homogeneous_sphere_eotvos_parameter` retains the exact
two-acceleration denominator for positive inward accelerations. Direct
two-dimensional volume quadrature checks the force. For a **hypothetical**
uniform sphere with \(R=1\) mm, a point test body at \(r=1.052\) mm,
\(\ell=100\,\mu\mathrm m\), and \(\alpha=1/3\), the relative force is
0.03082; treating the same mass as pointlike at the center gives 0.0001036.
The large difference illustrates why finite-size treatment matters. Neither
geometry represents the patterned Eöt-Wash apparatus.

### A patterned finite-thickness apparatus surrogate

The following is closer to a patterned experiment than a sphere, but remains
an infinite planar surrogate, **not** a model of the actual rotating detector.
Take nonoverlapping parallel layers separated by a gap \(d\), thicknesses
\(t_a,t_b>0\), and physical mass densities with periodic components
\(\delta\rho_a=\rho_{a1}\cos kx\) and
\(\delta\rho_b=\rho_{b1}\cos[k(x-\delta)]\), where \(k>0\). Their
mean densities must be chosen so the full density is nonnegative. Assume a
constant pairwise Yukawa coefficient \(\alpha\), no screening, and an
infinite periodic area. Fourier-transforming the three-dimensional Green
function across the plate gives
\[
 \int_{\mathbb R^2}d^2\boldsymbol{s}\,
 {e^{-\sqrt{|\boldsymbol{s}|^2+z^2}/\ell}\over
  \sqrt{|\boldsymbol{s}|^2+z^2}}e^{ik s_x}
 = {2\pi\over p}e^{-p|z|},\qquad p=\sqrt{k^2+\ell^{-2}}.
\]
Integrating the two layer depths and averaging the two cosines gives
\[
 {U_{\rm harmonic}\over A}=-C\cos(k\delta),\quad
 {F_x\over A}=-kC\sin(k\delta),\quad
 C={\pi G\alpha\rho_{a1}\rho_{b1}\over p^3}\,
 e^{-pd}(1-e^{-pt_a})(1-e^{-pt_b}).
\]
The factor \(1/2\) from averaging the cosines is included; it applies for
\(k>0\), not to a constant-density \(k=0\) mode. Mean-density contributions
and other harmonics do not contribute to this lateral Fourier coefficient.
For negative \(\alpha\) or opposite-sign density harmonics, \(C\) is signed.

`periodic_slab_yukawa_coefficients` computes \((C,kC)\) using log-domain
evaluation, including short ranges and thin layers. Its tests independently
integrate the Green function over transverse distance and both layer depths,
differentiate the energy with respect to displacement, and check the
long-wavelength limit. [Lee et al.](https://ar5iv.labs.arxiv.org/html/2002.11761)
describe 18- and 120-fold rotating patterns, 54- and 99-µm platinum
detector and attractor thicknesses, and a 10-µm Be--Cu electrostatic shield.
Using those nominal layer thicknesses and a 52-µm gap, but assuming a
hypothetical planar wavelength of 1 mm, \(\ell=100\,\mu\mathrm m\),
both density-harmonic amplitudes \(10{,}000\) kg/m³,
\(G=6.67430\times10^{-11}\) SI, and \(\alpha=1/3\), gives
\(C=7.46\times10^{-16}\) J/m² and
\(|kC|=4.69\times10^{-12}\) Pa. Replacing the gap by 100 or
300 µm gives \(2.66\times10^{-12}\) or \(2.51\times10^{-13}\) Pa.
Only the thicknesses and the first gap are taken from the paper; the
wavelength and density harmonics are not apparatus measurements. This is
**not** a measured torque, an apparatus fit, or an exclusion.
An actual response requires the complete disk/hole layouts, multilayer
thicknesses and densities, angular harmonics, edge effects, gap calibration,
and experiment-specific uncertainty/covariance and fitting procedure.
The [Fourier--Bessel methods paper](https://doi.org/10.1088/1361-6382/abebf2)
and [Lee's dissertation](https://hdl.handle.net/1773/45542) are starting
points for a faithful annular calculation. Direct retrieval of the complete
paper, supplemental material and dissertation was blocked by DNS in this
session; the dimensions above were checked against indexed excerpts of the
paper. An official machine-readable torque dataset and likelihood were not
located in this search. Their absence cannot be inferred merely from that.

### A coaxial rotating-harmonic finite-body surrogate

The planar calculation cannot produce a torsional signal. As an independent
rotating-geometry benchmark, model each finite-thickness layer by an
axisymmetric background plus the harmonic
\[
 \delta\rho_i(r,\theta)=\rho_{i1}g_m(r/a_i)\cos(m\theta),\quad
 g_m(s)=(s/\sqrt m)^m e^{(m-s^2)/2},\quad m\ge1.
\]
The radial profile peaks at one and extends to infinity; choose an appropriate
nonnegative mean density to make each total density physical. Rotate layer
\(b\) through angle \(\delta\). With
\(p(q)=\sqrt{q^2+\ell^{-2}}\) and
\[
 R_i(q)=a_i^2 e^{m/2}m^{-m/2}(qa_i)^m e^{-q^2a_i^2/2},
\]
the Fourier--Bessel transform of the Yukawa kernel and the two depth
integrals give
\[
 U_{\rm harmonic}=-C_m\cos(m\delta),\quad
 \tau_b=-mC_m\sin(m\delta),
\]
\[
 C_m=2\pi^2G\alpha\rho_{a1}\rho_{b1}
 \int_0^\infty q\,dq\,R_a(q)R_b(q)
 {e^{-p(q)d}(1-e^{-p(q)t_a})(1-e^{-p(q)t_b})\over p(q)^3}.
\]
The normalization includes the full azimuthal integration; \(C_m\) is
signed. `gaussian_ring_yukawa_torque_coefficient` evaluates the signed
coefficient \(mC_m\) with quadrature convergence checks. Tests compare
the result for \(m=1\) and \(m=18\) with direct volume integration of the
three-dimensional Yukawa Green function, and test signs, exchanging the
two bodies, increasing separation, and \(m=120\).

For illustration, take nominal Lee thicknesses 54 and 99 µm and gap 52 µm,
both Gaussian peaks at an **assumed** radius of 20 mm, \(\ell=100\) µm,
density amplitudes \(10{,}000\) kg/m³, and \(\alpha=1/3\). The computed
torque amplitudes are \(1.45\times10^{-17}\) N m for \(m=18\) and
\(2.65\times10^{-17}\) N m for \(m=120\). The harmonic numbers and
thicknesses echo the published apparatus, but its actual patterns are not
Gaussian rings and the density amplitudes and radius are not measured inputs.
These numbers are not a prediction for, or fit to, the experiment.

For future material maps, `voxel_yukawa_energy_and_torque` evaluates the
pairwise Yukawa energy and rotational torque of point-voxel masses in blocks.
Tests compare torque with the energy derivative and show convergence from
a coarser to a finer quadrature grid against the independently integrated
\(m=1\) Gaussian-ring benchmark. This validates only that example, not
arbitrary voxel grids: each actual apparatus map needs its own resolution,
geometry, material, and uncertainty checks. No actual Eöt-Wash map or
experimental likelihood is supplied.

* [Lee et al. (2020)](https://doi.org/10.1103/PhysRevLett.124.101101)
  measured separations 52 micrometres to 3 mm and reported a 95% limit
  of 38.6 micrometres on the range of a gravitational-strength Yukawa
  interaction under their stated model. The reported range limit is **not**
  a general exclusion curve for arbitrary coupling. The legacy power-law
  fit in `isl_yukawa.py` is not validated here and must not be used as one.
  At \(\alpha=1\) only, \(\ell=38.6\,\mu\mathrm m\) corresponds to
  \(m c^2=\hbar c/\ell\simeq5.11\) meV. This is a conversion of the
  published model-specific limit, not a bound for the \(\alpha=1/3\)
  example or for the AdS construction.
* [MICROSCOPE final results](https://doi.org/10.1103/PhysRevLett.129.121102)
  report \(\eta({\rm Ti,Pt})=[-1.5\pm2.3_{\rm stat}\pm1.5_{\rm syst}]
  \times10^{-15}\), with the statistical error at 1 sigma. A comparison
  needs source and detector sensitivities, Earth geometry, range, and
  the paper's statistical conventions; the result is not a universal
  hard threshold of \(10^{-15}\).
* [Fayet (2026)](https://arxiv.org/abs/2603.21275) discusses finite-source
  Yukawa form factors and Earth density dependence. It is a preprint and
  does not replace the experiment's response model.

As a **provenance-limited cross-check**, a community-maintained
[digitization attributed to Lee et al.](https://raw.githubusercontent.com/cajohare/AxionLimits/7d375f4879b32406a239fe48d2615a4bfd9bc0bb/limit_data/ScalarNucleon/EotWash2020.txt)
lists range in metres and \(\alpha\), not the collaboration's raw likelihood.
At \(100\,\mu\mathrm m\), log-linear interpolation between the listed points
\((98.2553\,\mu\mathrm m,0.07402)\) and
\((104.0509\,\mu\mathrm m,0.06611)\) gives \(\alpha\simeq0.0715\).
The legacy power law gives 0.001 at that range, about 71 times smaller.
This discrepancy rules out treating that legacy approximation as a
verified conservative representation of this digitization; it is not itself
an official collaboration constraint or a fit to the original data. Confirm
curve provenance, conventions, signs, and uncertainty before scientific use.

A further attempt to open the Eöt-Wash group site
(`https://www.npl.washington.edu/eotwash/node/1`) failed with the same DNS
block. Indexed excerpts identify the dissertation PDF
(`Lee_washington_0250E_21241.pdf`; effective pendulum masses 0.21 mg and
0.62 mg for the 18- and 120-fold patterns) and quote a dissertation limit of
\(\lambda>39\,\mu\)m versus 38.6 µm in the paper. The dissertation's
contents, torque tables and likelihood remain unread here.

**Network access (corrected).** Contrary to my earlier statement, the session
is not offline: GitHub and PyPI are reachable, while arXiv, APS, the
University of Washington repository, DOI resolvers and other publisher or
mirror hosts fail at DNS, consistent with a host allowlist. The pinned
community digitization above could therefore be fetched and checked.

**Digitized-curve check.** The pinned file has 116 points (5.8 µm to 996 µm),
strictly monotone. Log-log interpolation crosses \(|\alpha|=1\) at
\(\lambda=37.97\,\mu\)m versus the published 38.6 µm (1.6% lower),
consistent with digitization error and supporting its use as a
provenance-limited curve. `digitized_yukawa_excluded_range` returns the range
interval whose limit lies below \(|\alpha|\), without extrapolating beyond
the last digitized range. Applied to the **conditional** couplings of the
stiff-wall benchmark, under the experiment's point-Yukawa convention and
with no screening, apparatus response or covariance:

* \(\alpha=1/3\) (UV--IR): ranges from about 52.8 µm to the end of the
  digitization (996 µm) would be excluded;
* \(\alpha\simeq18.1\) (IR--IR): about 20.3 µm to 996 µm;
* \(\alpha\simeq0.0061\) (UV--UV): lies below the weakest digitized
  limit (0.0173), so it is not excluded within the digitized range.

Because the benchmark masses are dimensionless, these exclusions constrain
only a hypothetical physical range \(\ell\); they do not exclude the model
or fix \(\ell\). The digitization is not an official likelihood, and
this is not a validated apparatus-level comparison.

**Independent cross-checks and the multi-experiment envelope.** A second
extraction, `fifthforce_alpha_tilde.csv` in
[PolonaiseExperiment/luhdm](https://github.com/PolonaiseExperiment/luhdm)
(GPL-3.0), reports points taken from the vector figure in the arXiv source
with quoted uncertainties of ±10% at 10 µm and ±7% at 20 µm. The pinned
digitization used above agrees with it to 8% and 5.5% at those ranges, within
those uncertainties; the extractor's claim to have validated crossings
against five published \(|\alpha|=1\) values was not independently checked
here. Its 200 µm point belongs to a different experiment (HUST, Tan et al.
2020) and is about six times tighter than the Lee curve at that range.

This shows the Lee curve alone is not the relevant constraint for
\(\ell\gtrsim100\,\mu\)m. `digitized_yukawa_exclusion_intervals` overlays
several digitized 95%-type upper limits (MIT-licensed
[AxionLimits](https://github.com/cajohare/AxionLimits/tree/7d375f4879b32406a239fe48d2615a4bfd9bc0bb/limit_data/ScalarNucleon)
files for Eöt-Wash 2020 and 2006, HUST 2020 and 2012, Wuhan, Irvine and
Stanford, as of the pinned commit), interpolating each only inside its own
range. Overlaying is not a statistical combination; the Irvine curve is
labelled in the file as updated to 2σ, and other confidence conventions were
not verified. Over 5.8 µm to 5 m, the conditional couplings of the
stiff-wall benchmark would then be excluded for these Yukawa ranges, under
the point-Yukawa convention, no composition dependence, no screening:

| Coupling | \(\alpha\) | Excluded \(\ell\) (Lee curve only) | Excluded \(\ell\) (envelope) |
|---|---|---|---|
| UV--UV | 0.0061 | none | 166 µm to 0.79 m |
| UV--IR | 1/3 | 52.8 µm to 996 µm | 51.5 µm to 5 m |
| IR--IR | 18.1 | 20.3 µm to 996 µm | 20.3 µm to 5 m |

For a given benchmark model all three apply simultaneously, so a
laboratory-scale radion would need \(\ell\lesssim20\,\mu\)m (a mass above
about 10 meV) or an \(\ell\) beyond the digitized ranges, unless matter
placement, screening, or direct bulk couplings change the charges. This is
the first place the specified 5D model meets data, but it constrains only
the unspecified physical scale, not the model; the benchmark mass is
dimensionless and a real prediction needs the dimensionful parameters fixed
by the UM sector. The upper-range edges (996 µm for the Lee curve) are
the end of the digitization, not physical boundaries.

**User-supplied, unverified account (not used in any calculation).** A
maintainer reports that the group publishes no machine-readable torque tables
or likelihood, that numbers must be digitized from the published figures or
requested from the authors, and quotes a calibration factor
\(\gamma=0.988\pm0.005\) and a 52 mm hole-pattern diameter. These values
could not be checked against the paper here. The claim of no supplemental
material is in tension with an indexed excerpt of the arXiv text that cites
"Supplemental Material at XXXX", so it is not adopted. If tables can only be
digitized, the digitization method, its uncertainty and the covariance must
be frozen before any exclusion is claimed. Direct network access to arXiv
remained unavailable in this session.

No original experimental raw data were imported or fitted for this audit.
The conditional point-source expression is a calculator, not a measured
allowed region or an experimentally tested UM prediction.
The experimental \(\alpha=1\) range bound cannot be substituted for an
\(\alpha=1/3\) bound. MICROSCOPE's differential observable is zero in the
assumed equal-charge model irrespective of the nonzero common force, so its
reported measurement alone does not constrain that universal coupling.

For the separately assumed benchmark \(m=1040\) GeV,
\(\hbar c/m=1.897\times10^{-19}\) m \(=0.0001897\) fm, not
0.19 fm. This short-range benchmark is not an action-derived radion mass.
At laboratory separations it is outside the quoted Eöt-Wash range sensitivity;
it is not a quantitative likelihood test. The frequently used
\(\exp(-r_{\oplus}/\ell)\) point-Earth approximation is also inappropriate
for an extended Earth: at short range the nearest source material and
altitude, not just the distance to the center, control suppression.

The historical `isl_summary`, `equivalence_principle_summary`,
`ep_violation_in_eot_wash_range`, and `sep_ew_radion_verdict` no longer
return unsupported physical detection or safety booleans. Their old
verdict-shaped keys are `None`; explicitly named `*_proxy` fields expose
the corresponding legacy arithmetic where applicable. This is an intentional
API behavior change: downstream consumers must handle unknown results rather
than treating them as negative detections or established limits.

## 4. Dark-sector consequence and next gates

For \(B=B_0r_s\,dr/r\), \(F=dB=0\) locally for \(r>0\), so the gauge
stress from the circle action vanishes there. Separately, hold \(\phi\)
fixed in the source-free gauge equation in flat space: a static spherically
symmetric electric field then has \(r^2E=\mathrm{constant}\), hence
\(\rho_F\propto r^{-4}\), not the \(r^{-2}\) idealized flat-curve density.
This is a gauge-equation calculation, **not** by itself a solution of all
coupled equations. Indeed, with no potential or other scalar source, a
constant radion also requires \(F^2=0\) by the radion equation. A purely
electric nonzero field has \(F^2=-2E^2\), so it is inconsistent with
that constant-radion vacuum sector. Enforcing a fixed radion would require
additional balancing physics. These restricted observations do not rule
out a varying radion, distributed sources, magnetic fields, self-gravity,
massive modes, or a separate dark sector. Neither a halo solution nor a
thermal relic follows from them.
See `src/core/dark_matter_geometry.py` and
[the synthesis repair](../TRUTH_LAYER.md#synthesis-repair-2026-10-05).

Next, derive and independently audit a nearly flat stabilized 5D
matter/boundary solution with physical scalar charges and a finite-apparatus
response, and obtain machine-readable experimental likelihoods or verified
exclusion data. In the dark sector, solve or exclude a clearly specified
coupled source configuration before fitting
[SPARC](https://astroweb.case.edu/SPARC/). Freeze data selections, nuisance
parameters and statistical rules before interpreting either comparison.
The existing circle calculation, a phenomenological GW potential, and
independently supplied KK benchmarks are not interchangeable.

For the flat-interval model above, an actionable completion sequence is:

1. Independently derive and audit the coupled scalar--metric equations and
   both finite-stiffness boundary conditions, including the gauge treatment.
   Independently re-expand the complete 5D quadratic action for the interval
   conventions and verify each mode's normalization;
   compare the light eigenvalue and kinetic residue to the probe formula
   across a documented weak-backreaction parameter sweep. Check the full
   spectrum for tachyons and ghosts and establish the cutoff and KK hierarchy.
2. Introduce the specified boundary matter action and solve the sourced
   junction problem. Extract source/detector couplings as residues of the
   same normalized 5D Green function, including relevant KK modes. Test the
   equal-charge and zero-source limits and the range of validity of a
   single-Yukawa approximation. Quantum matching and composition dependence
   are additional inputs, not consequences of vacuum geometry.
3. Obtain the actual 18/120-fold mass maps, dimensions, materials and
   measured separations, and reproduce the published Newtonian and Yukawa
   torque harmonics using the Fourier--Bessel or independently validated
   finite-body method. Validate against supplied collaboration predictions,
   not against the planar surrogate alone.
4. Acquire the experiment's signal data, calibration and statistical treatment
   or a verified sign-appropriate exclusion curve. Freeze model inputs,
   systematics, nuisance parameters, correlations and confidence construction
   before performing a comparison. The published \(\alpha=1\) range bound
   remains a single conditional external benchmark until then.

## 5. Adjacent arithmetic and model corrections

The historical black-hole \(B^2\) saturation proxy is gauge dependent and
approaches zero, not one, as \(\phi\to0\) at fixed finite \(B\). It does not
locate a physical horizon or derive GW echoes. The legacy dark halo remains
an imposed profile, not the gauge-sector stress of that pure-gauge field.

In the embryology notes, the stated \(R=59.7\,\mu\mathrm m\) and
\(c_s=12/37\) give \(f=c_sc/(2R)\simeq0.814\) THz, not 0.324 THz;
\(74^5=2,219,006,624\) and \(5\ln74=21.5203\) nats. The state count,
heat conversion and biological coupling are not derived.
The historical Maxwell--Garnett numerator \(1+3fA\) is incorrect: for
spherical inclusions the standard expression is
\(\epsilon_{\rm eff}=\epsilon_d(1+2fA)/(1-fA)\),
\(A=(\epsilon_w-\epsilon_d)/(\epsilon_w+2\epsilon_d)\).
With the notes' \(\epsilon_w=9\), \(\epsilon_d=4.5\), no physical fraction
reaches \((37/12)^2\); the previously quoted 0.363 g/g does not follow.
The code's distinct illustrative \(\epsilon_w=80\) gives 0.3602 g/g under
its density assumptions, but is not a measured THz dielectric response.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
