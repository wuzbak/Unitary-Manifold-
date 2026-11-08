<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# Planar radion dynamics: reduction, constraints, and exact checks

## Scope and conventions

Take the four-dimensional Einstein-frame action

\[
 S_4=\int d^4x\sqrt{-g}\left(R[g]-\frac32(\nabla\psi)^2\right),
 \qquad
 ds_4^2=q_{ab}dx^a dx^b+r^2(dy^2+dz^2),
\]

with a flat two-dimensional transverse plane, \(r>0\), \(\psi=\ln\phi\),
and \(B_\mu=0\). The two-dimensional coordinates are \(x^a\). The null
conformal gauge convention is

\[
 q=-e^{2\sigma}du\,dv,\quad q_{uv}=q_{vu}=-e^{2\sigma}/2,\quad
 R[q]=8e^{-2\sigma}\sigma_{uv},\quad
 \Box_q f=-4e^{-2\sigma}f_{uv}.
\]

All displayed equations use this signature and these null-coordinate
normalizations. The conversion to the evolution solver's \((t,x)\)
coordinates is \(u=t-x,\ v=t+x\), with no \(1/\sqrt2\): hence
\(\partial_u=(\partial_t-\partial_x)/2\),
\(\partial_v=(\partial_t+\partial_x)/2\), and
\(q=e^{2\sigma}(-dt^2+dx^2)\). The symbolic null-coordinate helper names
its transverse dummy coordinates \(x,y\); those are not the solver's
longitudinal \(x\). The reduction assumes a trivial circle bundle, no vector
flux, and a globally vanishing KK vector when used as a global truncation;
locally setting the vector to zero does not establish those global
topological conditions.

In the full circle-reduced theory the vector equation is
\(\nabla_\mu(\lambda^2e^{3\psi}F^{\mu\nu})=0\). At \(B=0\), \(F=0\);
this equation and the vector stress and scalar source vanish identically.
Thus compatible zero-vector initial data define a consistent classical
sector, not an approximation that drops nonzero vector stress. Transverse
isotropy and reflection symmetry remove polarization and mixed components;
the direct full-component curvature checks retain the transverse equation
rather than assuming it is redundant. These statements do not select a
photon sector or prove stability against symmetry-breaking perturbations.

## Circle and transverse reductions, including boundary terms

For the circle ansatz
\[
 ds_5^2=e^{-\psi}g_{\mu\nu}dx^\mu dx^\nu+e^{2\psi}dz^2
\]
the local density identity is
\[
 \sqrt{-G}R[G]=\sqrt{-g}\left(R[g]-\frac32(\nabla\psi)^2+\Box_g\psi\right).
\]
Thus the \(\Box_g\psi\) term is a bulk divergence, not an extra radion
equation. With the outward-normal convention for \(K\), the reduced
five-dimensional Gibbons--Hawking--York term contains the opposite normal
derivative. Per unit circle period its density is
\[
 2\sqrt{|H_5|}\,K_5
   =\sqrt{|h_E|}\left(2K_E-n\cdot\nabla\psi\right),
\]
so the \(+\,\Box_g\psi\) bulk divergence cancels the
\(-n\cdot\nabla\psi\) term, leaving the four-dimensional Einstein-frame GHY
term. For nonnull boundaries use the oriented normal convention in this
identity; spacelike pieces carry the usual
\(\epsilon=n_\mu n^\mu=-1\) multiplier in the Lorentzian action:
\(S_{\rm GHY}=2\epsilon\int\sqrt{|h|}K\), in the normalization of the bulk
action here. The same oriented \(\epsilon\) multiplies both sides of the
displayed density identity (or is absorbed into oriented \(K\)). Signs
reverse if the normal or \(K\) convention is reversed.

For the planar transverse metric above,
\[
 R[g]=R[q]-\frac4r\Box_q r-\frac2{r^2}(\nabla r)^2,\qquad
 \sqrt{-g}=r^2\sqrt{-q}.
\]
The integrated-by-parts identity is therefore
\[
 \sqrt{-g}R[g]=\sqrt{-q}\left(r^2R[q]+2(\nabla r)^2\right)
             -4\sqrt{-q}\nabla_a(r\nabla^a r).
\]
On a two-dimensional boundary whose normal lies in the base, the last term
contributes (per unit transverse coordinate area)
\(-4\int\sqrt{|h|}\,r\,n\cdot\nabla r\). Meanwhile
\(K_4=K_q+2n\cdot\nabla r/r\) and
\(\sqrt{|h_4|}=r^2\sqrt{|h_q|}\), so the reduced 4D GHY term contributes
\(+4\int\sqrt{|h_q|}\,r\,n\cdot\nabla r\). These cancel, leaving the
two-dimensional \(2\int\sqrt{|h_q|}\,r^2K_q\) term. Include \(\epsilon\)
for spacelike boundaries as above. This bookkeeping specifies the action
whose bulk equations follow; it is not a claim that arbitrary boundary data
have been prescribed.

The resulting ungauged bulk action per unit transverse coordinate area is
\[
 S_2=\int d^2x\sqrt{-q}\left[
 r^2R[q]+2(\nabla r)^2-\frac32r^2(\nabla\psi)^2\right].
\]

## Variation before conformal gauge

Discarding only the stated boundary terms, variation with respect to
\(q^{ab}\) gives
\[
 E_{ab}=(q_{ab}\Box-\nabla_a\nabla_b)r^2
 +2r_a r_b-q_{ab}(\nabla r)^2
-\frac32r^2\psi_a\psi_b+\frac34q_{ab}r^2(\nabla\psi)^2=0.
\]
The scalar equations are
\[
 2rR[q]-4\Box r-3r(\nabla\psi)^2=0,\qquad
 \nabla_a(r^2\nabla^a\psi)=0.
\]
Only after these covariant variations, choose the conformal null gauge. Since
\(q_{uu}=q_{vv}=0\), the metric equations reduce to
\[
 E_{uu}=-2r C_u,\quad E_{vv}=-2r C_v,\qquad
 C_u=r_{uu}-2\sigma_u r_u+\frac34r\psi_u^2,\quad
 C_v=r_{vv}-2\sigma_v r_v+\frac34r\psi_v^2.
\]
Thus the two null constraints are consequences of the ungauged metric
variation; they are not discarded by gauge fixing. The \(r\)- and
\(\psi\)-equations become the evolution equations
\[
 r_{uv}=-\frac{r_ur_v}{r},\qquad
 \psi_{uv}=-\frac{r_u\psi_v+r_v\psi_u}{r},\qquad
 \sigma_{uv}=\frac{r_ur_v}{r^2}-\frac34\psi_u\psi_v.
\]
In particular, \(\sigma\) has its own evolution equation. Evolving all three
wave equations and imposing the two constraints on initial data is
consistent; the constraints need not replace the \(\sigma\)-equation.

`src/physics/planar_radion/derivation.py` constructs the pre-gauge null metric
variation and checks its components, rather than assigning constraint
status flags. It also differentiates \(rC_u\) and \(rC_v\), substitutes the
differentiated evolution equations, and simplifies both propagation
residuals to zero without using either constraint:
\[
 \partial_v(rC_u)=0,\qquad \partial_u(rC_v)=0.
\]

## Direct four-dimensional Ricci check

For \(ds^2=-e^{2\sigma}du\,dv+r^2(dx^2+dy^2)\), direct Christoffel and Ricci
construction from the metric matrix gives
\[
\begin{aligned}
 R_{uu}&=-\frac2r(r_{uu}-2\sigma_u r_u),&
 R_{vv}&=-\frac2r(r_{vv}-2\sigma_v r_v),\\
 R_{uv}&=-2\sigma_{uv}-2r_{uv}/r,&
 R_{xx}=R_{yy}&=4e^{-2\sigma}(rr_{uv}+r_ur_v).
\end{aligned}
\]
The symbolic implementation computes the Ricci tensor from that actual
four-dimensional metric and checks the five component differences against
these expressions. The equations imply
\(R_{ab}=\frac32\psi_a\psi_b\), \(R_{xx}=R_{yy}=0\), exactly the trace-reversed
Einstein--scalar equations for the stated action. In particular,
\(R_{uu}-\frac32\psi_u^2=-2C_u/r\) and likewise for \(v\). This is an
independent metric-level check of the null constraints and their
normalization.

The source also directly constructs the five-dimensional diagonal uplift
\[
 ds_5^2=e^{2\sigma-\psi}(-dt^2+dx^2)
       +r^2e^{-\psi}(dX^2+dY^2)+e^{2\psi}dz^2
\]
and computes its full Ricci tensor from Christoffels. The tests verify all
25 covariant components simplify to zero after substitution of the three
evolution equations and the two null constraints. This is a direct metric
check of the forward reduced-solution-to-uplift implication for this ansatz;
it is not a test of a fully off-shell component identity. The converse follows
analytically from the circle ansatz: in four-dimensional Einstein-frame
notation the mixed component vanishes and
\[
 R^{(5)}_{mn}=R^{(E)}_{mn}
-\frac32\partial_m\psi\partial_n\psi
+\frac12g^{(E)}_{mn}\Box_E\psi,\qquad
 R^{(5)}_{zz}=-e^{3\psi}\Box_E\psi.
\]
For finite real \(\psi\), the \(zz\) equation sets \(\Box_E\psi=0\);
the base equations then give \(R^{(E)}_{mn}=\frac32\partial_m\psi\partial_n\psi\),
the trace-reversed Einstein--scalar equation. This converse identity is an
analytic circle-reduction formula, not an additional SymPy residual test.

## Frozen-spectator obstruction

For the fixed-product metric \(g=q+r_0^2(dx^2+dy^2)\), the two-dimensional
identity \(R_{ab}[q]=q_{ab}R[q]/2\) makes the base Einstein tensor vanish
identically, \(G_{ab}=0\); the source constructs this product metric,
computes its Christoffels, Ricci tensor, scalar curvature and Einstein tensor,
and simplifies those base components to zero. The transverse components are
\(G_{xx}=G_{yy}=-r_0^2R[q]/2\). This does **not** assert vacuum
\(G_{\mu\nu}=0\) for the full product. Instead, the full Einstein--scalar
equation \(G_{\mu\nu}=T_{\mu\nu}\) on the base sets
\(T_{uu}=\frac32\psi_u^2=T_{vv}\) (with the stated action normalization).
For a real canonical scalar this forces \(\psi_u=\psi_v=0\). The transverse
Einstein equation then requires \(R[q]=0\); equivalently, variation of the
unfrozen reduced radion gives \(2r_0R[q]=0\). The executable negative
example sets \(\sigma_{uv}=1\), giving both nonzero curvature and radion
residual. Thus a frozen radion does not support a nonflat planar base with
this real scalar.

## Exact homogeneous branch and Kasner map

For a homogeneous solution on a domain \(r^2=at+b>0\), \(a\ne0\), the exact
quadratures are
\[
 r=\sqrt{at+b},\qquad
 \psi=\psi_0+\frac{P}{a}\log\frac{at+b}{\ell^2},\qquad
 \sigma=\sigma_0+\frac{3P^2-a^2}{4a^2}
                       \log\frac{at+b}{\ell^2}.
\]
They satisfy both null constraints and all three evolution equations by
direct substitution. This is valid for either sign of \(a\), restricted to
the interval where \(at+b>0\). For \(b=0\), write \(k=(3P^2-a^2)/(4a^2)\).
Proper time is proportional to \(|t|^{k+1}\) and the four-dimensional
Kasner-scalar exponents are
\[
 p_\parallel=\frac{k}{k+1},\quad
 p_\perp=\frac{1}{2(k+1)}\quad(\text{twice}),\qquad
 q_\psi=\frac{P}{a(k+1)}.
\]
The exact identities are \(p_\parallel+2p_\perp=1\) and
\(p_\parallel^2+2p_\perp^2+\frac32q_\psi^2=1\). These are coordinate
power-law solutions on the positive-\(r^2\) patch; they make no global
completeness claim.

## Bessel exact periodic coupled branch

On the exact areal-radius branch \(r^2=t\), the scalar equation reduces to
\[
 \psi_{tt}+t^{-1}\psi_t-\psi_{xx}=0.
\]
Each Fourier mode has exact solutions \(J_0(|k|t)\), \(Y_0(|k|t)\); the
symbolic check uses the regular \(J_0(|k|t)\cos(kx)\) standing mode. For any
periodic solution of this equation,
\[
 \partial_t\left[t\int_0^L\psi_t\psi_x\,dx\right]=0
\]
follows by substituting the wave equation and integrating the spatial
derivative \(\frac{t}{2}\partial_x(\psi_t^2+\psi_x^2)\) over the period.
On a periodic interval of length \(L\), \(k=2\pi n/L\); exact integration
gives zero charge for the standing Bessel mode. The null constraints become
\[
 \sigma_x=\frac32t\psi_t\psi_x,\qquad
 \sigma_t=-\frac1{4t}+\frac34t(\psi_t^2+\psi_x^2).
\]
Their cross-derivative compatibility and the \(\sigma\) wave equation reduce
exactly to the scalar wave equation. The period of \(\sigma\) is preserved
when the conserved charge \(t\int_0^L\psi_t\psi_xdx\) is initially zero.
Thus the periodic standing Bessel mode, with \(\sigma\) obtained by these
exact quadratures, is a coupled solution, not a frozen-metric test field.
A traveling-wave combination can carry nonzero charge and then cannot give a
periodic \(\sigma\) for this ansatz. This derivation is local on \(t>0\) and
makes no global continuation claim.

## Well-posedness boundary and verification status

In \((t,x)\), let \(F_r,F_\psi,F_\sigma\) denote the right sides of
\[
\begin{aligned}
r_{tt}-r_{xx}&=-(r_t^2-r_x^2)/r,\\
\psi_{tt}-\psi_{xx}&=-2(r_t\psi_t-r_x\psi_x)/r,\\
\sigma_{tt}-\sigma_{xx}&=(r_t^2-r_x^2)/r^2
                         -\frac34(\psi_t^2-\psi_x^2).
\end{aligned}
\]
For each \(f\in\{r,\psi,\sigma\}\), set \(W_f=(f_t,f_x)^T\). Its first-order
system is
\[
\partial_t W_f+A\partial_xW_f=(F_f,0)^T,\qquad
A=\begin{pmatrix}0&-1\\-1&0\end{pmatrix}=A^T,
\]
with eigenvalues \(\pm1\). The direct sum over three fields is symmetric
hyperbolic. Include \(f_t=(W_f)_1\) to retain field zero modes; the reduction
constraint \((W_f)_2-f_x=0\) has zero time derivative and is imposed on the
initial data. On a periodic spatial interval, for \(s\ge4\), \(r\ge r_*>0\),
and bounded \(H^s\times H^{s-1}\) fields/velocities, the standard
commuted-energy estimate for
\[
 E_s\asymp\sum_{f}\bigl(\|f\|_{H^s}^2+\|f_t\|_{H^{s-1}}^2\bigr)
\]
has the form \(\frac{d}{dt}E_s\le C_{r_*,M}(1+E_s)\) while these bounds hold.
This follows from symmetry of \(A\), the one-dimensional Sobolev algebra
property at these indices, and smooth composition by \(1/r\) on \(r\ge r_*\).
It gives local \(H^s\times H^{s-1}\) existence, uniqueness, and continuous
dependence for compatible Cauchy data; \(C_u=C_v=0\) propagate by the
explicit identities above. Continuation requires control of those norms and
staying in \(r>0\); no global existence, singularity resolution, or
unrestricted-domain claim follows.

For the variational action, fix the induced metric and \(\psi\) (equivalently
\(\phi=e^\psi\)) on each nonnull boundary component; the reduced boundary
term is \(2\epsilon\int\sqrt{|h_q|}\,r^2K_q\). For spacelike temporal
boundaries \(\epsilon=-1\) with the outward-normal convention used above.
The Cauchy problem specifies compatible data on an initial slice; it does
not independently prescribe arbitrary values on both temporal ends of a
slab. Residual conformal transformations \(u\mapsto U(u)\),
\(v\mapsto V(v)\) remain, with
\(\sigma\mapsto\sigma-\frac12\log(U'V')\) for orientation-preserving maps.

The SymPy routines and tests are the executable evidence: metric variations,
differentiated constraints, direct 4D Ricci components, all 25 direct 5D
uplift Ricci components, homogeneous branch, and Bessel-mode/quadrature
residuals are exact simplifications. The GHY cancellation and local
well-posedness statement are analytic boundary-bookkeeping and energy-method
arguments, not encoded by SymPy or Lean.
Existing `docs/TRUTH_LAYER.md` text on the Maxwell lane describes a separate
prescribed-background test field and explicitly keeps self-consistent
gravity/radion evolution open; it should not be read as a claim about this
analytically constrained scalar sector, nor as evidence that a general
coupled numerical problem is solved.

## Implementation and independent numerical acceptance (2026-11-03)

The physical-time solver is `src/physics/planar_radion/evolution.py`. It evolves
all three fields and velocities with periodic centered second-order spatial
differences and classical RK4, without modifying `src/core/evolution.py` or
its declared relaxation time. The conformal coordinate \(t\) is not in
general proper time: along fixed spatial coordinates,
\(d\tau=e^\sigma dt\). No entropy-production law or arrow of time is inferred
from this time-reversal-invariant action.

The initial-data constructor enforces the periodic momentum compatibility
condition and rejects incompatible mean or Nyquist modes. Its default
centered scalar derivative introduces second-order initial-data error;
the spectral antiderivative does not turn sampled data into an exact
continuum solution. Independent analytic scalar derivatives can be supplied.
The acceptance runner samples exact Bessel data independently, and separately
tests the approximate constructor with non-Bessel scalar position/velocity
profiles.

State validation rejects nonfinite/complex data, nonpositive transverse
scale, invalid grids, incompatible trajectories, and overflow/underflow of
the uplifted metric. RK stages are checked without clipping or projection.
The conservative wave CFL guard is a numerical restriction, not a proof of
global nonlinear stability or an automatic curvature-resolution criterion.

The implementation is a self-contained package under `src/physics/planar_radion/`.
The existing tracked-entry ceiling in `src/core/` is preserved, rather than
raised to accommodate this capability.

`src/physics/planar_radion/geometry.py` constructs all Christoffels and Ricci
components directly from five-dimensional metric jets. Its slab mode uses
fourth-order spacetime differences, including mixed derivatives, on saved
metric values. It never substitutes the evolution RHS for time derivatives.
The norm is a positive orthonormal-frame component norm, not the indefinite
Ricci contraction or Ricci scalar alone.

The generated [acceptance packet](../../2-REPRODUCIBILITY/planar_radion_acceptance.json)
binds its runner and three source modules by SHA-256, records the baseline
HEAD and scientific package versions, and rejects source changes during
execution. It is not a full-worktree frozen regression receipt. All 12
declared gates passed, including 58 exact symbolic residual identities,
spatial/time refinement, absolute tolerances and six negative controls.
Identity counts describe checked expressions, not independent physics claims.

Parameters were fixed before measurement: dimensionless reference length
one, period \(2\pi\), \(1\le t\le1.5\), meshes \(32,64,128,256\), and
\(\Delta t\le0.1\Delta x\). Second-order acceptance requires observed orders
between 1.8 and 2.2 on the finer comparisons, finest exact-solution field
RMS below \(10^{-4}\), and finest constraint/uplift norms below \(10^{-3}\).
These are engineering acceptance limits, not observational error bars.

| Family | Finest six-field RMS error | Maximum null constraint | Maximum 5D Ricci frame norm |
|---|---:|---:|---:|
| Bessel amplitude 0.04 | \(1.54\,10^{-7}\) | \(5.28\,10^{-8}\) | \(2.29\,10^{-6}\) |
| Bessel amplitude 0.12 | \(4.93\,10^{-7}\) | \(4.75\,10^{-7}\) | \(8.58\,10^{-6}\) |
| Two Bessel modes (0.04, 0.025) | \(2.36\,10^{-7}\) | \(2.86\,10^{-7}\) | \(4.30\,10^{-6}\) |
| Exact conformal coordinate pullback | \(3.09\,10^{-7}\) | \(1.02\,10^{-6}\) | \(4.87\,10^{-6}\) |
| Independent mixed-mode initial data | No analytic reference | \(6.92\,10^{-7}\) | \(2.75\,10^{-5}\) |

Constraints use the canonical definitions above with
\(\partial_u=(\partial_t-\partial_x)/2\) and
\(\partial_v=(\partial_t+\partial_x)/2\), and are maximized across the saved
trajectory. These corrected diagnostics are half the previously reported
values; no evolution equation, convergence gate or scientific scope changed.
The source-bound packet was regenerated, not merely rehashed. The Ricci oracle
audits nine midpoint snapshots, retaining five interior times; this is
explicitly not a full-trajectory curvature bound. Errors include all three
fields and velocities in dimensionless normalization. For independent
initial data, the finest nested-grid difference is \(4.04\,10^{-6}\) with
observed self-convergence orders 1.994 and 1.999. The fixed-mesh timestep
comparison gives order 4.0105. The coordinate pullback exercises spatial
area variation and mixed derivatives, but does not claim a physical
gravitational area wave.

The benchmark ladder also tests homogeneous scalar solutions of both
signs, curved vacuum Kasner uplifts, and a locally flat Milne control.
Independent connection-based Riemann tests distinguish the curved branches
(\(K=4.5/T^4\)) from the Milne branch despite nonzero metric second
derivatives in both. The six integration negative controls detect an
injected constraint error, incompatible periodic data, a scalar wave with
fixed spectators, a missing transverse equation, wrong frame conversion,
and wrong scalar normalization. Unit tests additionally reject invalid RK
stages and degenerate/overflowing metrics.

### Reproduction and verification boundary

Use an environment with the repository's NumPy, SciPy, SymPy, pytest and
Navigator bootstrap dependencies installed. This session restored missing
test dependencies in an isolated virtual environment, not the system Python.

```bash
python TOOLS/checks/run_planar_radion_acceptance.py \
  --output 2-REPRODUCIBILITY/planar_radion_acceptance.json
python -m pytest tests/test_planar_radion_derivation.py \
  tests/test_planar_radion_evolution.py tests/test_planar_radion_geometry.py \
  tests/test_planar_radion_acceptance.py tests/test_metric.py \
  tests/test_evolution.py tests/test_action_derived_flow.py \
  tests/test_action_to_evolution_contract.py \
  tests/test_pillar1131_offdiagonal_exact_reduction_closure.py \
  tests/test_pillar1132_adm_homogeneous_hyperbolic_evolution.py -q -m ""
python proof/VERIFY.py
python proof/ALGEBRA_PROOF.py
```

Results: acceptance exited zero with every gate true; combined targeted
suite **274 passed**; both isolated proof-entry scripts exited zero. The
pre-change interface baseline passed 119 tests; the additional action/ADM
baseline passed 49 tests including slow checks. Those baselines overlap and
are not added together as a distinct-test total.
The final packaged rerun also included `COMPACTIFICATION/test_maps.py`:
**280 passed**, comprising the same 274 physics tests and six inventory
tests. Directory-entry limits and the technical note's internal links pass.
The repository-wide link audit instead stops at the pre-existing dangling
`12-AZ-IP/01-axiom-os/AxiomZero/IDENTITY.md` path; no whole-repository link
clearance is claimed.

The broad `tests/`, `recycling/` and canonical Pentad command, with slow
tests enabled and `--maxfail=1`, was attempted under a 180-second execution
bound. After restoring missing PyYAML it exceeded that bound and returned
124, without a complete result. Partial progress is not a passed-test total.
There is **no new full-repository regression all-clear**, full formal-build
claim, version increase or pillar allocation. The historical regression
marker is not replaced.

The resulting capability is constrained local physical-time evolution and
vacuum uplift in the specified massless zero-vector planar circle sector.
Vector backreaction, potentials, orbifold physics, generic polarizations,
unrestricted 5D evolution, singularity resolution, empirical confirmation
and derivation of the old relaxation law remain outside this result.

## Pillar registration update (v38.6 — Sprint DB, 2026-11-07)

This module is now certified by **Pillar 1135**
(`src/core/pillar_1129_1168/pillar1135_planar_radion_physical_time_certification.py`),
which invokes the acceptance evidence above directly (no reimplementation)
and exposes it as a fail-closed certificate:
`PLANAR_RADION_RESTRICTED_PHYSICAL_TIME_EVOLUTION_CERTIFIED`, with the
specific subcase `PLANAR_MASSLESS_ZERO_VECTOR_CONSTRAINT_COMPATIBLE_PHYSICAL_TIME_EVOLUTION_CERTIFIED`.
This is a certified constraint-compatible, nonconstant,
coordinate-time propagating-scalar evolution, restricted to the perimeter
documented above. It does not close either of Pillar 1130's residual
obligations (`T_RELAXATION_LAW_DECLARED_NOT_DERIVED`,
`PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED`) at the framework level; the
action-to-evolution contract still reads `DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN`.
See `docs/TRUTH_LAYER.md#sprint-db-planar-radion-physical-time-certification`
and `docs/CLAIM_MASTER_BOARD.md` for the full synchronized record.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
