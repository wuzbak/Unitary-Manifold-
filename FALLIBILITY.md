# Fallibility, Limitations, and Failure Modes

*Unitary Manifold v9.0 — ThomasCory Walker-Pearson, 2026*

---

This document answers three questions that any referee or skeptical expert will
immediately ask:

1. **Where could this framework be wrong even if the code is correct?**
2. **Under what conditions does it stop working or become ambiguous?**
3. **What observations would falsify it outright?**

It is written in the same clinical tone expected of a refereed submission.
Nothing here is defensive; all of it is honest.

---

## I. Scope of Verification

The 286 automated tests in `tests/` confirm that the numerical implementations
are **internally self-consistent**: every equation as coded is a correct
consequence of the mathematical framework as stated.  The test suite covers
metric curvature (`test_metric.py`), field evolution
(`test_evolution.py`), holographic boundary dynamics
(`test_boundary.py`), fixed-point convergence (`test_fixed_point.py`,
`test_convergence.py`), and inflation observables including the CMB transfer
function (`test_inflation.py`).

Internal verification does **not** constitute empirical confirmation of the
framework as a description of nature.  Specifically:

- The tests check that the code implements the stated equations faithfully.
- They do **not** independently validate those equations against observational
  data beyond the reference values already embedded in the code (Planck 2018
  `nₛ`, `r`, and the birefringence hint from Minami & Komatsu 2020 /
  Diego-Palazuelos et al. 2022).
- External validation requires observational discrimination from competing
  models that also match those same reference values.

When the README badge reads "286/286 Tests Passing," this is a statement about
**code correctness**, not about **physical correctness**.

---

## II. Axiomatic Dependence

The entire predictive chain hangs on a small set of assumptions that are
**postulated, not derived**.  If any of these assumptions are physically
unjustified, the conclusions of the framework do not follow, regardless of the
internal consistency of the mathematics.

| Assumption | Where used | Status |
|------------|-----------|--------|
| Smooth 5D Kaluza–Klein manifold with compact S¹ (or S¹/Z₂) extra dimension | `metric.py` → `assemble_5d_metric`; `inflation.py` → `jacobian_5d_4d` | **Postulated** |
| Specific 5D metric block structure: G₅₅ = φ², off-diagonal = λφB_μ | `metric.py` → `assemble_5d_metric`; `evolution.py` → `_compute_rhs` | **Postulated** |
| Identification of the fifth dimension with physical irreversibility | `evolution.py` docstring (Gemini Issue 4 note); throughout | **Conjectural** |
| Identification of φ with entanglement capacity | `README.md`; `evolution.py` docstring | **Conjectural** |
| Walker–Pearson field equations as the correct dimensional reduction | `evolution.py`; `metric.py` | **Postulated** |
| FTUM operator structure U = I + H + T | `fixed_point.py` | **Postulated** |
| Holographic entropy–area relation S = A/4G at the boundary | `fixed_point.py` → `apply_irreversibility` | **Assumed (standard AdS/CFT)** |

The sentence that must be said plainly:
> **If any of these assumptions are physically unjustified, the conclusions of
> the framework — including nₛ, r, β, and α — do not follow.**

---

## III. Circularity Audit

This section answers the question that most speculative theories quietly
avoid: *which outputs are genuinely derived, and which are fitted to observations?*

### 3.1 Derivation chain

| Quantity | Role | Source | Honest status |
|----------|------|--------|---------------|
| 5D metric ansatz G_AB | Structural assumption | Postulated | **Free choice** |
| KK dimensional reduction | Dimensional projection | Standard KK, adapted | **Standard; not novel** |
| Walker–Pearson equations | Field equations | Derived from 5D Einstein–Hilbert action under the metric ansatz | **Derived, given the ansatz** |
| Fixed-point operator U | Convergence operator | Constructed from assumed I, H, T decomposition | **Derived, given U's definition** |
| φ₀ (bare) | FTUM fixed-point radion vev | Output of `fixed_point_iteration`; converges to ≈1 in Planck units | **Derived, given U** |
| α = φ₀⁻² | Nonminimal coupling | Derived via KK cross-block Riemann curvature R^μ\_{5ν5} | **Derived, given φ₀** |
| **n_w = 5** (winding number) | Topological multiplier in KK Jacobian J = n_w · 2π · √φ₀ | Required to obtain φ₀_eff ≈ 31.42 and nₛ ≈ 0.9635 | ⚠️ **Chosen to fit Planck; not derived from topology** |
| φ₀_eff = J · φ₀ | Effective 4D inflaton vev | Derived from n_w via `jacobian_5d_4d` | **Derived, given n_w** |
| nₛ ≈ 0.9635 | Scalar spectral index | Output of `ns_from_phi0(phi0_eff)` | **Derived, given n_w** |
| r ≈ 0.0028 | Tensor-to-scalar ratio | Output of `tensor_to_scalar_ratio(ε)` | **Derived, given n_w** |
| **CS_LEVEL = 74** | Chern–Simons level for birefringence | Required to obtain β ≈ 0.35° | ⚠️ **Fitted to Minami & Komatsu 2020; not derived** |
| β ≈ 0.35° | Cosmic birefringence angle | Output of `birefringence_angle(CS_LEVEL_PLANCK_MATCH)` | **Derived, given k_CS = 74** |
| Planck 2018 data | Validation | External | **Validation only — but two free parameters (n_w, k_CS) were chosen against it** |

### 3.2 The two honest admissions

**Admission 1 — n_w = 5 is fitted, not derived.**
The bare FTUM fixed point gives φ₀ ≈ 1, which yields nₛ ≈ −35 (failing Planck
by ~8 500 σ). The resolution is a topological winding number n_w = 5 in the
KK Jacobian, giving J ≈ 31.42 and nₛ ≈ 0.9635. The value n_w = 5 is
*motivated* by S¹/Z₂ orbifold topology and Chern–Simons winding, but it is
**not uniquely derived** from the rest of the framework.  Any integer n_w
between 4 and 6 produces a phenomenologically viable nₛ; n_w = 5 is chosen
because it is the minimum value consistent with Planck at 1σ.  A compelling
framework would derive n_w from first principles (e.g., from quantisation
conditions on the compact dimension, anomaly cancellation, or a uniqueness
theorem for the KK tower).  This is currently an open gap.

**Admission 2 — k_CS = 74 is fitted, not derived.**
The Chern–Simons level `CS_LEVEL_PLANCK_MATCH = 74` (see `inflation.py`) is
the integer value of k_CS that reproduces the observed birefringence signal
β ≈ 0.35° (Minami & Komatsu 2020; Diego-Palazuelos et al. 2022) via the
formula g_{aγγ} = k_CS · α / (2π² r_c).  The framework does not derive why
the Chern–Simons level should be 74 from any deeper principle.  This is a free
parameter.  It would become a prediction only if k_CS could be fixed
independently — for example, by anomaly cancellation in the 5D gauge theory,
or by a quantisation condition on the compact dimension.

### 3.3 What would change if Planck values were different?

- If Planck had measured nₛ = 0.95 (outside the current window), the framework
  would fail unless a different n_w were invoked — which would be post-hoc
  adjustment, not prediction.
- The birefringence signal β = 0.35° is currently a 2–3σ *hint*, not a
  confirmed detection.  If future CMB polarimetry (LiteBIRD, CMB-S4) finds
  β consistent with zero, the prediction β ≈ 0.35° would be falsified, and
  with it the specific identification k_CS = 74.
- The tensor-to-scalar ratio r ≈ 0.0028 is a genuine forward prediction that
  has **not** been used to fit any parameter; it follows from nₛ via the
  slow-roll consistency relation and is testable by next-generation B-mode
  experiments.

---

## IV. Known Failure Modes and Regimes of Uncertainty

These are not implementation bugs.  They are **conceptual uncertainties
intrinsic to the framework**, documented here so that future work can address
them systematically.

### 4.1 Numerical sensitivity

- **Grid resolution and stability.** The semi-implicit field updater in
  `evolution.py` requires dt ≤ 0.001 for lattice sizes N ≤ 24 with dx = 0.1
  to avoid singular matrix inversion in `linalg.inv(g)`.  Long-time stability
  beyond the tested number of steps has not been characterised; users should
  not extrapolate evolution results beyond the validated regime.
- **Zero-mode truncation.** The simulation tracks only the KK zero-mode (4D
  projected) fields; higher KK modes are truncated.  As documented in
  `evolution.py`, apparent entropy increase in the zero-mode sector may
  correspond to information encoded in the truncated KK tower rather than true
  irreversible loss.  This means the irreversibility claim — central to the
  framework — is not yet demonstrated at the level of the full KK spectrum.
- **Time-coordinate double-counting (Gemini Issue 4).** The evolution parameter
  *t* acts as a Ricci-flow parameter, not the coordinate time x⁰ embedded
  inside the metric tensor.  A fully diffeomorphism-invariant treatment would
  require an ADM 3+1 decomposition.  The current 1D spatial reduction leaves
  this issue unresolved.

### 4.2 Model non-uniqueness

- Alternative 5D extensions can produce emergent irreversibility without the
  specific Walker–Pearson structure.  The framework does not demonstrate that
  its metric ansatz is the *unique* 5D completion consistent with the
  4D physics.
- The Goldberger–Wise double-well potential V = λ(φ² − φ₀²)² is a
  *choice* motivated by radion stabilisation literature.  Other potentials (e.g.,
  Coleman–Weinberg, KKLT-type) may yield qualitatively similar inflation while
  predicting different spectral tilts.
- The RS1 orbifold variant (n_w = 7, k_RC = 12; see `effective_phi0_rs`)
  also produces nₛ ≈ 0.963 — matching Planck equally well with a different
  winding number.  The existence of multiple parameter combinations that all
  fit the same data undermines the "uniqueness" of any single choice.

### 4.3 Phenomenological fragility

- The nₛ prediction depends sensitively on φ₀_eff through the slow-roll
  formula nₛ = 1 − 6/φ₀_eff².  A 5% change in φ₀_eff shifts nₛ by
  ~0.006, comparable to the Planck 1σ uncertainty.  This means the prediction
  is in Planck's window partly because φ₀_eff ≈ 31.42 is almost exactly
  what is needed — and n_w = 5 was chosen to produce that value.
- Inflationary observables assume 60 e-folds of slow-roll inflation beginning
  from the inflection point φ* = φ₀_eff / √3.  The number of e-folds is
  not derived; it is a standard assumption.  Alternative pre-inflationary
  histories could exit the slow-roll regime at different field values and
  predict a different nₛ.
- The holographic fixed point (FTUM) convergence is demonstrated numerically
  for a specific choice of initial conditions, friction parameter γ = 5.0,
  and tolerance 10⁻⁶.  Convergence for all physically reasonable initial
  conditions has not been proven analytically.

### 4.4 Interpretational risks

- The identification of φ with "entanglement capacity" is conjectural and is
  not derived from a quantum-information calculation.  It is a physical
  interpretation, not a theorem.
- The identification of the fifth geometric dimension with the arrow of time
  is motivated by the framework's construction but is not mandated by any
  uniqueness argument.  Other theories (loop quantum gravity, causal dynamical
  triangulations, causal set theory) achieve an emergent arrow of time without
  a compact extra dimension.

---

## V. Explicit Falsifiability Conditions

The Unitary Manifold framework makes several observational commitments.
It would be **falsified** if any of the following occurred:

1. **Birefringence null result.** Future CMB polarimetry (LiteBIRD, CMB-S4,
   Simons Observatory) measures the cosmic birefringence angle β consistent
   with zero at 3σ or better.  The framework predicts β ≈ 0.35°; a confirmed
   null result cannot be accommodated without abandoning k_CS = 74.

2. **Tensor-to-scalar ratio outside the predicted range.** The framework
   predicts r ≈ 0.0028 from the slow-roll consistency relation r = 16ε at
   φ* = φ₀_eff / √3.  A confirmed detection of r > 0.01 at high significance
   would be in tension with this prediction (though the value of r depends on
   n_w, so tension could in principle be resolved by adjusting n_w — which
   would itself represent a falsification of the specific n_w = 5 claim).

3. **Spectral index outside Planck window with tighter future measurement.** If
   a future CMB survey (e.g., PICO or a post-LiteBIRD mission) constrains nₛ
   to a window that excludes 0.9635 while the Planck central value does not
   shift substantially, the specific choice n_w = 5 would be excluded.

4. **No fixed-point convergence for varied initial conditions.** If the FTUM
   iteration `fixed_point_iteration` fails to converge for a broad sweep of
   physically reasonable initial entropy S₀, boundary area A₀, and topology
   charge Q_top, the existence of a universal fixed point Ψ* would be
   undermined.  The current demonstration is restricted to a single default
   initial state.

5. **Violation of holographic entropy–area scaling.** If future quantum-gravity
   experiments or black-hole thermodynamics measurements find that the
   Bekenstein–Hawking relation S = A/4G breaks down systematically at a
   specific scale, the foundational entropy contraction dS/dt = κ(A/4G − S)
   used in `apply_irreversibility` would lose its grounding.

6. **Derivation of nₛ from a competing theory with fewer free parameters.**
   If a simpler model — with no freely chosen winding number — reproduces the
   same set of observables (nₛ, r, β, α), the Unitary Manifold's claim to
   uniqueness or predictive economy would be negated by Occam's razor.

---

## Summary

| Claim | Status | Key caveat |
|-------|--------|-----------|
| 286/286 tests pass | ✅ Confirmed | Internal consistency only |
| nₛ ≈ 0.9635 matches Planck | ✅ Matches | n_w = 5 is chosen, not derived |
| r ≈ 0.0028 | Forward prediction | Not yet constrained; derives from n_w |
| β ≈ 0.35° matches birefringence hint | ✅ Matches | k_CS = 74 is fitted |
| α = φ₀⁻² | Derived | Depends on φ₀ from FTUM, which depends on U |
| FTUM convergence | Demonstrated numerically | Single initial condition; not proven analytically |
| Irreversibility from 5D | Conjectural | KK tower truncated; ADM formalism absent |
| Uniqueness of the framework | Not established | Multiple parameter combinations give same observables |

The framework is internally coherent and makes several forward predictions
that are testable by experiments currently in operation or under construction.
Its present weakness is not the code, but the gap between the two fitted
parameters (n_w, k_CS) and a first-principles derivation of those integers.
Closing that gap — or demonstrating that no such closing is possible — is the
most important outstanding theoretical task.
