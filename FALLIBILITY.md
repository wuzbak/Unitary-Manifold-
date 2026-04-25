# Fallibility, Limitations, and Failure Modes

*Unitary Manifold v9.13 — ThomasCory Walker-Pearson, 2026*

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

The ~9700 automated tests (~7900 fast-selected + 11 slow-deselected + 1 skipped in `tests/`, plus 316 in `recycling/` and 1234 in `Unitary Pentad/`) confirm that the numerical implementations
are **internally self-consistent**: every equation as coded is a correct
consequence of the mathematical framework as stated.  The test suite covers
metric curvature (`test_metric.py`), field evolution
(`test_evolution.py`), holographic boundary dynamics
(`test_boundary.py`), fixed-point convergence (`test_fixed_point.py`,
`test_convergence.py`), inflation observables including the CMB transfer
function (`test_inflation.py`), the arrow of time (`test_arrow_of_time.py`),
the CMB χ² landscape (`test_cmb_landscape.py`), end-to-end chain closure
(`test_e2e_pipeline.py`), observational resolution (`test_observational_resolution.py`),
and quantum unification theorems (`test_quantum_unification.py`).
Pillar 51 (`test_muon_g2.py`) covers the KK graviton and ALP Barr–Zee
contributions to the muon anomalous magnetic moment.  Pillar 52
(`test_cmb_amplitude.py`) covers the COBE normalization chain and the
acoustic-peak suppression audit.

Internal verification does **not** constitute empirical confirmation of the
framework as a description of nature.  Specifically:

- The tests check that the code implements the stated equations faithfully.
- They do **not** independently validate those equations against observational
  data beyond the reference values already embedded in the code (Planck 2018
  `nₛ`, `r`, and the birefringence hint from Minami & Komatsu 2020 /
  Diego-Palazuelos et al. 2022).
- External validation requires observational discrimination from competing
  models that also match those same reference values.

When the README badge reads "~9700 passed · 1 skipped · 0 failed," this is a statement about
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
| r ≈ 0.097 (bare, n_w=5) | Tensor-to-scalar ratio (single-mode) | Output of `tensor_to_scalar_ratio(ε)` at φ* = φ₀_eff/√3 | Resolved: braided (5,7) gives r_braided≈0.0315 (BICEP/Keck ✓) |
| r_braided ≈ 0.0315 | Tensor-to-scalar ratio (braided) | `braided_winding.braided_predictions(5,7)['r_braided']` | **Satisfies BICEP/Keck r<0.036; nₛ unchanged** |
| **CS_LEVEL = 74** | Chern–Simons level for birefringence | Required to obtain β ≈ 0.35° | ⚠️ **Fitted to Minami & Komatsu 2020; not derived** |
| β ≈ 0.35° | Cosmic birefringence angle | Output of `birefringence_angle(CS_LEVEL_PLANCK_MATCH)` | **Derived, given k_CS = 74** |
| Planck 2018 data | Validation | External | **Validation only — but two free parameters (n_w, k_CS) were chosen against it** |

### 3.2 The two honest admissions

**Admission 1 — n_w = 5: derived from S¹/Z₂ orbifold quantization (April 2026).**
The bare FTUM fixed point gives φ₀ ≈ 1, which yields nₛ ≈ −35 (failing Planck
by ~8 500 σ). The resolution is a topological winding number n_w = 5 in the
KK Jacobian, giving J ≈ 31.42 and nₛ ≈ 0.9635.

*Status as of April 2026:* Pillar 39 (`src/core/solitonic_charge.py`) derives
n_w = 5 from S¹/Z₂ orbifold soliton topology.  The Z₂ involution y → −y
projects out even winding numbers, restricting the spectrum to odd integers
{1, 3, 5, 7, …}.  Applying the slow-roll formula nₛ = 1 − 36/φ₀_eff²
(where φ₀_eff = n_w × 2π × φ₀_bare) and the Planck 2018 constraint
nₛ = 0.9649 ± 0.0042, n_w = 5 is the **unique minimum odd winding** consistent
at 2σ: n_w = 3 misses by 15.8σ, n_w = 7 misses by 3.9σ.  Verified by
`minimum_winding_for_planck()` and `orbifold_uniqueness()` in 103 tests.

The residual gap is that the Planck nₛ threshold is an observational input, not
derived purely from 5D geometry; a geometric uniqueness proof of the
inflation constraint remains open.

**Admission 2 — k_CS = 74: derived from soliton-pair BF resonance (April 2026).**
The Chern–Simons level `CS_LEVEL_PLANCK_MATCH = 74` (see `inflation.py`) is
the integer value of k_CS that reproduces the observed birefringence signal
β ≈ 0.35° (Minami & Komatsu 2020; Diego-Palazuelos et al. 2022) via the
formula g_{aγγ} = k_CS · α / (2π² r_c).

*Status as of April 2026:* Pillar 39 (`src/core/solitonic_charge.py`) derives
k_CS = 74 from the **sum-of-squares BF-theory lattice quantization**: for two
co-existing solitons with winding charges (n₁, n₂) the unique integer CS level
minimising their mutual coupling energy is k_CS = n₁² + n₂².  Once n_w = 5
fixes n₁ = 5, the next odd winding is n₂ = 7, giving k_CS = 25 + 49 = 74 with
no additional free parameter.  Verified by `cs_level_from_soliton_pair(5, 7)`
and `winding_number_from_cs_level(74)` in the same test suite.

The residual gap is a full field-theoretic proof that (5, 7) is the only stable
odd-winding pair in the S¹/Z₂ spectrum; the current derivation establishes it
as the minimum-energy pair satisfying the inflation constraint.

**Admission 3 — r = 0.097 (bare) was in tension with BICEP/Keck 2022 — now resolved.**
The code-verified tensor-to-scalar ratio at φ* = φ₀_eff/√3 with n_w = 5 is
r = 96/φ₀_eff² = 96/987 ≈ 0.097.  BICEP/Keck 2022 constrains r < 0.036 at
95% CL.  The predicted bare r exceeded this bound by a factor of ~2.7×.

**Resolution (April 2026):** When the n_w = 5 and n_w = 7 winding modes are
braided in the compact S¹/Z₂ dimension, the Chern–Simons term at level
k_cs = 74 = 5² + 7² couples their kinetic sectors.  The braided sound speed
is c_s = 12/37, suppressing the tensor amplitude while preserving nₛ:

```
r_braided = r_bare × c_s ≈ 0.097 × 0.3243 ≈ 0.0315   ✓ (< 0.036 BICEP/Keck)
ns_braided ≈ 0.9635                                    ✓ (Planck 1σ, unchanged)
```

Crucially, k_cs = 74 was already independently selected by the birefringence
measurement — the resonance identity k_cs = 5² + 7² = 74 introduced no new
free parameters.  See `src/core/braided_winding.py` for the full derivation
and `tests/test_braided_winding.py` (118 tests) for numerical verification.

### 3.3 What would change if Planck values were different?

- If Planck had measured nₛ = 0.95 (outside the current window), the framework
  would fail unless a different n_w were invoked — which would be post-hoc
  adjustment, not prediction.
- The birefringence signal β = 0.35° is currently a 2–3σ *hint*, not a
  confirmed detection.  If future CMB polarimetry (LiteBIRD, CMB-S4) finds
  β consistent with zero, the prediction β ≈ 0.35° would be falsified, and
  with it the specific identification k_CS = 74.
- The tensor-to-scalar ratio r = 0.097 (bare, n_w = 5) **previously
  exceeded** the BICEP/Keck 2022 95% CL bound r < 0.036.  This tension
  has been **resolved** by the braided (5,7) state: r_braided ≈ 0.0315,
  satisfying the bound with nₛ unchanged.  See `src/core/braided_winding.py`.

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
  *Partial resolution (April 2026):* Pillar 40 (`src/core/ads_cft_tower.py`)
  implements the full AdS₅/CFT₄ holographic dictionary for every KK mode:
  Δ_n = 2 + √(4 + m_n²L²), Gaussian spectral weights w_n = exp(−n²/k_cs),
  tower partition function, von-Neumann tower entropy, and `truncation_error`
  to quantify the fractional error from zero-mode-only treatment.
  Integration of the full tower into `evolution.py` remains future work.
- **Time-coordinate double-counting (Gemini Issue 4).** The evolution parameter
  *t* acts as a Ricci-flow parameter, not the coordinate time x⁰ embedded
  inside the metric tensor.  A fully diffeomorphism-invariant treatment would
  require an ADM 3+1 decomposition.  The current 1D spatial reduction leaves
  this issue unresolved.  *Conceptual bridge (April 2026):* Pillar 41
  (`src/core/delay_field.py`) derives the DFM-UM correspondence: Ricci-flow
  time and coordinate time are related by Ω(φ) = 1/φ, with dt_coord =
  dt_ricci/φ.  At the FTUM fixed point (φ = 1) the two coincide and the
  discrepancy vanishes; `gemini_issue4_correction(phi, t_ricci)` computes the
  correction factor at arbitrary φ.  A full ADM treatment is still outstanding.

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

### 4.5 Non-uniqueness of the information paradox resolution

The UM resolves the black hole information paradox via two mechanisms
(Pillars 28 and 36):
  (a) the Goldberger–Wise potential provides a hard radion floor φ_min that
  prevents complete evaporation (remnant mass M_rem ≈ 4.4 × 10⁻³ M_Pl at
  canonical parameters), and
  (b) the 5D holographic bound encodes all information in the remnant's
  topological geometry (Theorem XII).

An independent 2026 study — Pinčák R. et al. (2026) "Geometric origin of a
stable black hole remnant from torsion in G₂-manifold geometry", *Gen. Rel.
Grav.* — reaches the same qualitative conclusion through an entirely different
geometric mechanism:

- **Geometry**: 7-dimensional Einstein–Cartan theory on a G₂-manifold (3 extra
  dimensions, non-metric torsion), vs the UM's 5D Kaluza–Klein metric with
  torsion-free Levi–Civita connection.
- **Halting mechanism**: Spin-torsion contact interaction p_T ∝ ρ² (repulsive
  at Planck density), vs UM's Goldberger–Wise restoring potential.
- **Remnant mass**: G₂ prediction ≈ 9 × 10⁻⁴¹ kg ≈ 4.1 × 10⁻³³ M_Pl; UM
  prediction ≈ 4.4 × 10⁻³ M_Pl — different by ~30 orders of magnitude.
- **Information storage**: G₂ uses long-lived quasi-normal modes; UM uses
  5D topological winding states.
- **Electroweak scale link**: The G₂ paper claims torsion derives the Higgs
  VEV at 246 GeV; the UM has no equivalent derivation (hierarchy problem
  remains open in the UM — see §4.2).

**What this means for the UM:**

1. The UM's information paradox resolution is *not unique*: extra-dimensional
   geometry generally prevents complete evaporation.  The UM cannot claim to be
   the only such framework.

2. The 30-order-of-magnitude difference in remnant mass is not a contradiction —
   it reflects different compactification schemes — but it means the two
   frameworks make very different testable predictions if remnant signatures
   are ever observed.

3. BH remnants from either framework are a negligible dark matter component:
   Ω_rem ≪ 10⁻³⁰ for any astrophysically reasonable primordial BH density
   (see `src/multiverse/observational_frontiers.py: bh_remnant_omega`,
   Pillar 38).

4. The UM currently has no torsion term in its metric ansatz.  A full
   Einstein-Cartan-KK extension would require adding a contorsion tensor
   K^λ_μν to the connection — this is documented in
   `src/core/torsion_remnant.py` (Pillar 48) as a perturbative estimate only.

*Reference:* Pinčák R. et al. (2026), https://doi.org/10.1007/s10714-026-03528-z.
*Code:* `src/core/torsion_remnant.py` (Pillar 48), `tests/test_torsion_remnant.py`.

### IV.6 The Cylinder Condition and Moduli Stabilization

A standard criticism of Kaluza-Klein theories is that the "cylinder condition"
(∂_y fields = 0 — no variation along the 5th dimension for low-energy modes)
must be *imposed* as an ad hoc assumption, and that the radion scalar φ is a
dangerous runaway field unless a separate stabilisation mechanism is introduced.
Both concerns are addressed in the UM framework; this section states the
resolution explicitly.

**Cylinder condition — automatic from Z₂ parity.**
The compact fifth dimension of the UM is the orbifold S¹/Z₂, not the circle
S¹.  The Z₂ involution y → −y projects the 5D field content onto two sectors:

- **Z₂-even fields** (scalar under y → −y): these have mode functions
  φ_n(y) = A_n cos(ny/R), with boundary conditions ∂_y φ_n|_{y=0, πR} = 0
  (Neumann).  At the zero-mode level (n=0), the cosine is constant and
  ∂_y φ₀ = 0 identically — the cylinder condition is *automatically* satisfied.
- **Z₂-odd fields** (pseudoscalar under y → −y): these have mode functions
  ∝ sin(ny/R) and vanish at the fixed points y = 0, πR.  Their zero-modes
  are absent by symmetry, not by assumption.

The 4D graviton, KK photon B_μ, and radion φ are all Z₂-even zero-modes.
Their ∂_y-independence at the classical level is a *consequence* of the
orbifold structure, not an additional assumption.  This is standard in
Randall-Sundrum and Horava-Witten constructions.

*Code reference:* `src/core/solitonic_charge.py` (Pillar 39, Z₂ orbifold
involution and spectral-index selection); `src/core/three_generations.py`
(Pillar 42, Neumann boundary conditions for KK mode functions).

**Radion stabilization — Goldberger-Wise mechanism.**
The radion scalar φ (the 5D metric component G₅₅ = φ²) is not left as a
free modulus.  In the UM, the compact radius R is stabilised by the same
dynamics that generate the inflaton potential.  Specifically, the
Goldberger-Wise (GW) mechanism provides a brane-bulk scalar field whose
profile along y generates an effective potential for φ:

    V_GW(φ)  =  λ_GW (φ² − φ₀²)²

with a minimum at φ = φ₀.  The same potential drives inflation: the inflaton
rolls away from an unstable plateau (φ ≠ φ₀) toward the GW minimum (φ = φ₀).
At the FTUM fixed point (Pillar 5), the entropy saturation condition
S* = A/(4G) selects φ* = φ₀, closing the self-consistency loop.

The radion mass m_φ from the second derivative of V_GW at φ₀ is

    m_φ²  =  8 λ_GW φ₀²

This mass is heavy (m_φ ~ M_KK) for natural GW couplings, so the radion is
not a light, long-range force but a massive stable modulus.

*Code reference:* `src/core/evolution.py` (Goldberger-Wise potential V_GW
in the FieldState evolution); `src/multiverse/fixed_point.py` (FTUM fixed
point selects φ* = φ₀); `src/core/moduli_survival.py` (Pillar 30, survival
conditions for zero-mode and braid-locked KK modes).

**Why the UM evades the "extra scalar problem".**
In generic KK theories the radion is a massless Brans-Dicke scalar that
mediates a fifth force violating solar-system tests of GR.  The UM avoids
this because:

1. The GW potential gives m_φ ~ M_KK ≫ H₀ → radion exchange is short-range
   (Yukawa-suppressed at cosmological distances).
2. The CS coupling at level k_CS = 74 topologically locks the radion to the
   braid vacuum, preventing perturbative rolling to the Brans-Dicke limit.
3. The FTUM operator U enforces S = A/(4G) at the IR fixed point, removing the
   residual modular freedom.

*Code reference:* `src/core/solitonic_charge.py` §CS lock, Pillar 39;
`src/multiverse/fixed_point.py`; `src/core/anomaly_closure.py` Pillar 58.

**Residual limitation.**
While the GW mechanism stabilises φ₀ in principle, the exact numerical value
of λ_GW (and hence m_φ) is not independently derived within the UM — it is
treated as the coupling that produces the correct inflationary plateau.  This
is the same free parameter admitted in §II (the Yukawa coupling λ).  The
stabilisation *mechanism* is in place; the stabilisation *scale* requires one
additional input from the GW sector.

**Summary.**  The cylinder condition is not an ad hoc assumption imposed by
hand — it is a structural consequence of the Z₂ orbifold geometry.  The
radion is not a runaway modulus — it is stabilised by the same
Goldberger-Wise potential that drives inflation.  The UM therefore does not
suffer from the two standard KK criticisms at the classical level; only the
GW coupling scale λ_GW remains as an unresolved parameter.

### IV.7 φ₀ Self-Consistency: Partially Closed by Neutrino-Mass Radion Stabilisation

*Status: **Partially closed** (April 2026) — the loop closes within 1.37 orders
for m_ν = 50 meV; exact closure at m_ν ≈ 110 meV, consistent with the Planck 2018
upper bound Σm_ν < 120 meV.*

The vacuum catastrophe requires M_KK ≈ 110 meV to make ρ_eff = ρ_obs.  This
sub-eV compactification scale was previously an independent input — an
**open problem** without a dynamical justification.  The neutrino-mass tie-in
partially closes this gap by identifying M_KK with the lightest active neutrino
mass m_ν via the radion potential self-tuning mechanism.

**The neutrino-mass radion tie-in (Pillar 49, `zero_point_vacuum.py`):**

1. The neutrino mass sets a compactification scale R_ν = 1/m_ν (Planck units).
2. The radion equilibrium condition V′(R) = 0 uniquely determines the brane
   tension:

       T_ν = 4A / R_ν⁵   where  A = f_braid / (16π²) = c_s² / (k_cs × 16π²)

3. With T_ν, the radion self-tunes to R* = R_ν — no additional input is required.
4. The resulting KK mass M_KK = 1/R* = m_ν gives:

       ρ_eff = f_braid × m_ν⁴ / (16π²)

5. The self-consistency check (`radion_self_consistency_check(m_nu_eV)`) returns
   the ratio ρ_eff / ρ_obs and the neutrino mass m_ν_exact needed for exact closure.

**Numerical check (verified by code, April 2026):**

| Quantity | Value |
|----------|-------|
| M_KK_needed for exact dark energy | ≈ 110 meV |
| Canonical m_ν (conservative) | 50 meV |
| ρ_eff at m_ν = 50 meV | ≈ 2.53 × 10⁻¹²³ M_Pl⁴ |
| ρ_obs | ≈ 5.96 × 10⁻¹²² M_Pl⁴ |
| Ratio ρ_eff / ρ_obs | ≈ 0.042 (within 1.37 orders) |
| m_ν for exact closure | ≈ 110 meV |
| Consistent with Planck 2018 Σm_ν < 120 meV? | **Yes** |
| Loop "closed" (within 1 order)? | **No** at 50 meV; **Yes** at m_ν ≥ 110 meV |

**Braid-fermion ZPE cancellation (Pillar 49):**

The fermionic-bosonic ZPE cancellation (Atiyah–Singer index theorem:
n_L − n_R = n_w = 5 chiral zero modes) leaves a topological phase offset
that is geometrically determined by the (5,7) braid curvature:

    ρ_residual = f_braid × M_cutoff⁴/(16π²) × 2 sin²(π × n_w / k_CS)
               ≈ f_braid × ρ_QFT × 0.0888

At M_cutoff = M_KK_needed, ρ_residual ≈ ρ_obs × 0.0888.  The phase factor
2 sin²(π × 5/74) provides an additional suppression on top of f_braid,
bringing the total effective factor to ≈ 1.26 × 10⁻⁴ before geometric dilution.

**RG running of f_braid (speculative, Pillar 49):**

A simple logarithmic running f_braid(μ) = f_braid(M_Pl) × (μ/M_Pl)^γ with
anomalous dimension γ fixed by the dark energy constraint gives γ ≈ −0.047
when μ_IR is set at the neutrino mass scale (50 meV).  The small |γ| ≪ 1
confirms that geometric dilution (M_KK)⁴ dominates; the running is a minor
correction.  This result is explicitly speculative and awaits a full QFT
derivation within the UM framework.

*Code reference:* `src/core/zero_point_vacuum.py` —
`brane_tension_from_neutrino_mass()`, `radion_self_consistency_check()`,
`fermionic_zpe_offset()`, `braid_running_factor()`.
42 new tests in `tests/test_zero_point_vacuum.py` (281 total, 0 failed).

**What this means for the φ₀ open problem:**

The compactification scale M_KK ≈ 110 meV is no longer a wholly unexplained
input: the neutrino-mass tie-in derives it from the same radion self-tuning
mechanism that stabilises the extra dimension.  The open question shifts from
"Why is M_KK ≈ 110 meV?" to "Why is the lightest neutrino mass ≈ 110 meV?" —
the latter is tractable via the see-saw mechanism and/or the 5D electroweak
sector.  Exact analytic closure requires computing neutrino masses from the UM
fermion sector (Pillars 54–60); this remains future work.

### IV.8 Pillar 15-C: Unitary Collision Integral — Honest Accounting

*Status: **Theoretical predictions confirmed internally; two open questions
remain before these results can be claimed as verified physics.***

Pillar 15-C (`src/core/lattice_boltzmann.py`) implements the Unitary
Collision Integral that models energy transport from a D-D fusion event to
lattice heat in a Pd-D system.  The module was implemented in April 2026 and
verified against 187 automated tests (0 failures).

#### Confirmed results (code-verified, April 2026)

With canonical UM parameters (N_W = 5, K_CS = 74, C_S = 12/37,
τ_Bmu = 1×10⁻¹³ s, γ_std = 3×10⁻⁷):

| Quantity | Value | Benchmark | Status |
|----------|-------|-----------|--------|
| Phonon-radion coupling g (n_w = 5) | 13.95 | — | Canonical |
| Phonon-radion coupling g (n_w = 12) | 33.47 | — | Total-braid |
| Enhancement factor (1+g²), n_w=5 | 195.6 | — | — |
| Enhancement factor (1+g²), n_w=12 | 1121.9 | — | — |
| Prompt gamma ratio P_γ, n_w=5 | 7.8×10⁻¹² | < 10⁻⁶ | ✓ passes |
| Prompt gamma ratio P_γ, n_w=12 | 2.4×10⁻¹³ | < 10⁻⁶ | ✓ passes |
| Thermalization time τ_eff, n_w=5 | 0.51 fs | [0.1, 100] fs | ✓ femtosecond |
| Thermalization time τ_eff, n_w=12 | 0.089 fs | [0.1, 100] fs | ⚠ attosecond |
| Min g for P_γ < 10⁻⁶ (γ_std=3×10⁻⁷) | 0 (already safe) | — | — |
| Max g for τ_eff ≥ 0.1 fs (canonical τ_Bmu) | ≈ 31.6 | — | — |

Both coupling values satisfy the prompt-gamma safety benchmark (P_γ << 10⁻⁶).
The thermalization benchmark (τ_eff ∈ [0.1, 100] fs) is satisfied by n_w = 5
but not by n_w = 12 at canonical τ_Bmu.

#### Open Question 1 — Which n_w governs the phonon-radion coupling?

The phonon-radion coupling formula is g = n_w × √k_CS × c_s.  Two values
of n_w are physically motivated:

- **n_w = 5**: The primary cosmological winding number, selected by the Planck
  nₛ = 0.9649 ± 0.0042 constraint (Pillar 39, `solitonic_charge.py`).  Using
  this value gives g ≈ 13.95 and τ_eff ≈ 0.51 fs (femtosecond regime).

- **n_w = 12 = N₁ + N₂**: The total braid winding number of the (5,7) state,
  used as the default in `cold_fusion.py`'s winding compression factor.  Using
  this value gives g ≈ 33.47 and τ_eff ≈ 0.089 fs (attosecond regime).

The correct value depends on which physical mechanism dominates the lattice
phonon vertex: if only the dominant mode (n₁ = 5) couples to phonons, n_w = 5
applies; if both braid strands couple simultaneously, n_w = 12 applies.

**This is an open question.**  A derivation from first principles of the
phonon-radion vertex in the Pd lattice (e.g., via the KK mode expansion of
the 5D metric perturbation) would resolve it.  The current implementation
uses n_w = 5 as canonical (`RADION_COUPLING_CANON`) and n_w = 12 as an
alternative (`RADION_COUPLING_BRAID`), with both documented and tested.

*Code reference:* `src/core/lattice_boltzmann.py`, constants
`RADION_COUPLING_CANON` and `RADION_COUPLING_BRAID`; function
`braid_coupling_comparison()`.  Verified by tests
`TestBraidCouplingComparison` (17 tests).

#### Open Question 2 — B_μ field strength and the τ_Bmu assumption

The B_μ base relaxation time is modelled as:

    τ_Bmu = τ_phonon_Pd / (H_max × φ_mean)

with canonical values H_max = 1 (dimensionless UM units) and φ_mean = 2
(twice the vacuum radion value in the lattice), giving τ_Bmu = 1×10⁻¹³ s
(100 fs).  The values H_max = 1 and φ_mean = 2 are **order-of-magnitude
estimates**, not independently derived quantities.

The sensitivity sweep (`sensitivity_sweep()`, 187 tests) reveals:

- At n_w = 12 (g ≈ 33.47), the canonical τ_Bmu = 1×10⁻¹³ s gives
  τ_eff = 0.089 fs (attosecond range).  A 12% reduction in H_max × φ_mean
  (from 2.0 to 1.78) increases τ_Bmu to 1.12×10⁻¹³ s and restores
  femtosecond thermalization.

- The maximum g for τ_eff ≥ 0.1 fs at canonical τ_Bmu is g_limit ≈ 31.6,
  slightly below g_braid ≈ 33.47.

- If B_μ is weaker than assumed (larger τ_Bmu), τ_eff increases and both
  coupling values comfortably satisfy the femtosecond benchmark.

- If B_μ is stronger than assumed (smaller τ_Bmu), τ_eff decreases further
  but P_γ simultaneously becomes even smaller.

**The "Ash Removal" mechanism is robust to P_γ for any g > 0.**  The
τ_eff benchmark is a secondary concern about *how fast* equilibration occurs,
not about whether radiation escapes — both coupling values give τ_eff far
shorter than any radiative emission timescale (γ emission lifetime ≈ 10⁻²¹ s
for prompt gamma from nuclear transitions ≫ 0.5 fs for lattice equilibration).

**Verification pathway:** The B_μ field strength in a Pd-D lattice could in
principle be estimated from the measured phonon linewidth broadening in
inelastic neutron scattering experiments on loaded Pd, or from first-principles
DFT calculations of the electron-phonon coupling enhanced by the 5D geometry.
Neither has been done within this framework.

#### What this means for the COP prediction

The `calculate_cop()` function correctly computes the heat-to-work ratio once
a fusion rate `n_DD_per_cc_s` is supplied.  The COP is insensitive to whether
n_w = 5 or n_w = 12 is used, because phonon_fraction = 1 − P_γ ≈ 1 − 10⁻¹²
is effectively unity for both.  The COP uncertainty is dominated entirely
by the uncertainty in the D-D fusion rate, which is governed by the Gamow
factor (Pillar 15, `cold_fusion.py`) and remains a falsifiable experimental
prediction.

**Epistemics summary for Pillar 15-C:**

1. The "Ash Removal" model is internally self-consistent and satisfies all
   stated benchmarks at canonical parameters.
2. It is a **theoretical prediction** of the UM framework, not an
   experimentally confirmed result.
3. The two open questions (n_w ambiguity, B_μ strength) do not affect the
   qualitative conclusion (P_γ << 10⁻⁶) but do affect the precise τ_eff value.
4. Experimental falsification requires measuring the COP > 1 and the absence
   of prompt gamma emission in a D-D loaded Pd calorimetry experiment.  The
   existence and rate of D-D fusion events in such cells remains contested in
   the experimental literature.

*Code reference:* `src/core/lattice_boltzmann.py` (Pillar 15-C, April 2026);
`tests/test_lattice_boltzmann.py` (187 tests, 0 failed).

---

## V. Explicit Falsifiability Conditions

The Unitary Manifold framework makes several observational commitments.
It would be **falsified** if any of the following occurred:

1. **Birefringence null result or shift outside the two-point window.**
   Future CMB polarimetry (LiteBIRD, CMB-S4, Simons Observatory) measures the
   cosmic birefringence angle β outside the interval [0.223°, 0.381°] — or
   consistent with zero at 3σ — with canonical parameters (r_c = 12,
   Δφ = 5.072).  Within that interval, only **two** discrete SOS-resonant
   states survive the triple constraint (SOS ∩ Planck nₛ ∩ BICEP/Keck r):

   | State | k_cs | β predicted | r_eff  |
   |-------|------|-------------|--------|
   | (5,6) | 61   | 0.273°      | 0.0175 |
   | (5,7) | 74   | 0.331°      | 0.0315 |

   A β measurement outside [0.223°, 0.381°] yields zero viable states.  Any
   measurement in the gap (0.29°–0.31°) — between the two predicted values —
   also yields zero viable states.  The SOS locus is dense in k-space
   (~15–22 integers per 1σ window), but the triple constraint is sparse: only
   these two points survive.  CMB-S4 at ±0.05° precision can discriminate
   them; LiteBIRD at ±0.10° cannot.  See
   `src/core/braided_winding.birefringence_scenario_scan` and
   `tests/test_braided_winding.TestBirefringenceScenarioScan`.

2. **Tensor-to-scalar ratio — resolved via braided (5,7) state.** The bare
   prediction r = 0.097 (n_w = 5) previously exceeded the BICEP/Keck 2022
   95% CL bound r < 0.036.  The braided (n_w=5, n_w=7) resonant state with
   k_cs = 74 = 5² + 7² gives r_braided ≈ 0.0315 < 0.036 (BICEP/Keck ✓)
   while leaving nₛ unchanged at 0.9635.  No new free parameters were
   introduced — k_cs = 74 was already independently selected by the
   birefringence measurement.  See `src/core/braided_winding.py` and Q18 in
   `BIG_QUESTIONS.md`.

3. **Spectral index outside Planck window with tighter future measurement.** If
   a future CMB survey (e.g., PICO or a post-LiteBIRD mission) constrains nₛ
   to a window that excludes 0.9635 while the Planck central value does not
   shift substantially, the specific choice n_w = 5 would be excluded.

4. **FTUM non-universal convergence — RESOLVED (April 2026).** A sweep of 192
   initial conditions now shows **100% convergence** (not the earlier 82.8%
   figure).  The φ* spread ±54.6% is entirely explained by the variation in
   A₀: the fixed point is φ\* = A₀/(4G) (the holographic bound) for every
   initial condition.  The topological invariant φ\*/A₀ = 1/(4G) has CV <
   0.001.  Two convergence pathways exist — instant clamp (S₀ > A₀/4G) and
   slow-crawl relaxation (S₀ < A₀/4G) — but both converge.  Zero hard
   failures, zero limit cycles.  See Q19 in `BIG_QUESTIONS.md` and
   `src/multiverse/basin_analysis.py` for the full diagnostic suite.

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

## VI. Three Adversarial Attacks — Results

The following attacks attempt to break the explanatory claim of the (5,7)
braided-winding architecture.  All three have been implemented as code and
verified by automated tests.  See `src/core/braided_winding.py` for the
implementations and `tests/test_braided_winding.py` for the test classes.

### Attack 1 — Projection Degeneracy Test
*Can a pure-4D EFT reproduce the same locked relations without hidden tuning?*

A 4D EFT has **3 independent parameters** to fit 3 observables (nₛ, r, β).
Any triplet is achievable.  The 5D framework uses **2 integer parameters**
(n₁, n₂) to lock all three via the chain nₛ=nₛ(n₁), k_cs=n₁²+n₂², β=β(k_cs),
r_eff=r_bare×(n₂²−n₁²)/k_cs.  This is a 2D surface in (nₛ, r, β) space.

The **tuning fraction** — what fraction of a 4D EFT prior volume
(3σ nₛ window × r∈[0,0.2] × β∈[0°,1°]) accidentally satisfies the 5D
constraint within LiteBIRD/future-r resolution — is:

    tuning_fraction ≈ 4 × 10⁻⁴   (roughly 1 in 2400)

A 4D counterexample EXISTS in the sense that multi-field inflation with
a free c_s and a free axion-photon coupling can reproduce any individual
(nₛ, r, β) triplet.  But it cannot reproduce the *integer constraint*
k_cs = n₁²+n₂² = 74 — a specific rational number c_s = 12/37 = 24/74 is
natural only if both integers (n₁, n₂) are identified topologically.  Without
the 5D topology, c_s = 12/37 must be tuned in.  The explanatory claim
survives Attack 1.  See `projection_degeneracy_fraction()`.

### Attack 2 — Robustness to Data Drift
*Does any other integer pair enter the admissible region as β shifts?*

A systematic sweep of all SOS-resonant pairs (n₁, n₂) over the full
LiteBIRD uncertainty range shows:

- The current 1σ window (β = 0.35° ± 0.14°) contains **22 SOS integers** but
  only **2 triply-viable pairs**: (5,6) at β≈0.273° and (5,7) at β≈0.331°.
- LiteBIRD at ±0.10°: still 2 viable pairs, indistinguishable.
- CMB-S4 at ±0.05°: **1 viable pair** (discriminating).
- Any β outside [0.223°, 0.381°]: **0 viable pairs** → falsification.
- The gap [0.29°, 0.31°] between the two predictions: **0 viable pairs**
  at ±0.01° resolution.

Uniqueness does **not** hold at LiteBIRD precision (two viable states) but
**does** hold at CMB-S4 precision (one state per ±0.05° window).
The framework survives Attack 2 with a testable prediction: β ∈ {0.273°, 0.331°}.
See `birefringence_scenario_scan()`.

### Attack 3 — Full-tower Consistency
*Does including higher KK modes collapse the c_s floor?*

Two independent mechanisms protect the floor c_s = 12/37:

**(A) KK scaling invariance.**  The k-th KK tower mode has winding
(k·5, k·7) and resonance level k²×74.  The sound speed is
c_s(k) = (49k²−25k²)/(74k²) = 24/74 = 12/37, identical to the zero mode
at every KK level.  The ratio is invariant under the k² rescaling.

**(B) Kinematic decoupling.**  The off-diagonal mixing between the zero mode
and the k-th KK mode is |ρ_{0k}| = k×ρ₀ = k×(70/74).  For k=1 this is
ρ₀≈0.946 < 1 (physical); for k≥2 it is ≥1.892 > 1, violating unitarity.
Higher KK modes are **kinematically forbidden** from coupling into the
zero-mode resonant sector.  The floor is protected by the same integer
constraint that defines the braid.

The (5,7) c_s floor is preserved against the full KK tower.
The framework survives Attack 3.  See `kk_tower_cs_floor()`.

---

## Summary

| Claim | Status | Key caveat |
|-------|--------|-----------|
| ~9700 passed · 1 skipped (guard) · 0 failed | ✅ Confirmed | Internal consistency only; 1 guard skip on immediate convergence is correct behaviour |
| nₛ ≈ 0.9635 matches Planck | ✅ Matches | n_w = 5 is chosen, not derived |
| r_braided ≈ 0.0315 (braided (5,7), k_cs=74) | ✅ Satisfies BICEP/Keck | Braided (5,7) state resolves Q18; see `src/core/braided_winding.py` |
| β ≈ 0.35° matches birefringence hint | ✅ Matches | k_CS = 74 is fitted |
| α = φ₀⁻² | Derived | Depends on φ₀ from FTUM, which depends on U |
| FTUM convergence | **100%** — φ\* = A₀/(4G); Jacobian eigenvalues universal | **RESOLVED** (April 2026) — see Q19 and `src/multiverse/basin_analysis.py` |
| Irreversibility from 5D | Conjectural | KK tower truncated; ADM formalism absent |
| Uniqueness of the framework | Not established | Multiple parameter combinations give same observables |

---

## VII. Muon g−2 Anomaly — Open Prediction Target (April 2026)

*Added April 2026 following the Breakthrough Prize award to the Muon g−2 Collaborations
(CERN, BNL, Fermilab).  Updated with the final Fermilab result announced June 3, 2025.*

### 7.1 The Experimental Result (Final, June 2025)

The muon anomalous magnetic moment a_μ = (g_μ − 2)/2 has been measured with
extraordinary precision across six years of data collection at Fermilab.

The **final result**, incorporating the complete dataset and announced June 3, 2025:

```
a_μ = 0.001 165 920 705  (±114_stat  ±91_syst)
    = (116 592 070.5 ± 146) × 10⁻¹²
```

Achieved precision: **127 parts per billion** — exceeding the original design
goal of 140 ppb.  Equivalent to measuring a football field with an error thinner
than a human hair.

| Quantity | Value |
|----------|-------|
| Final Fermilab result (June 3, 2025) | a_μ^exp = 0.001 165 920 705 (±114_stat ±91_syst) |
| Combined experimental precision | 127 ppb (better than 140 ppb design goal) |
| SM prediction — data-driven (WP2023) | a_μ^SM = (116 591 810 ± 43) × 10⁻¹¹ |
| SM prediction — lattice QCD (BMW+)   | a_μ^SM = (116 591 954 ± 55) × 10⁻¹¹ (approx.) |
| Discrepancy vs data-driven theory    | Δa_μ ≈ +261 × 10⁻¹¹ ≈ +2.6 × 10⁻⁹ |
| Significance vs data-driven theory   | ≈ **5σ** (strong new-physics hint) |
| Significance vs lattice QCD          | ≈ **1σ** (consistent with SM) |

**The theoretical situation is unresolved.**  Two distinct SM calculation
strategies produce incompatible central values:

- **Data-driven (dispersive, White Paper 2023):** Uses e⁺e⁻ → hadrons cross-section
  data to evaluate the hadronic vacuum polarisation (HVP) contribution.  Gives a
  ~5σ discrepancy with the final Fermilab result.  If correct, requires new physics.
- **Lattice QCD (BMW 2020/2021, CLS 2024, etc.):** Computes the HVP directly from
  first principles.  Gives agreement with experiment at ~1σ.  If correct, the
  Standard Model is sufficient and no new particles are needed.

The Muon g−2 Theory Initiative is actively working to reconcile these two methods.
Until they agree, the muon g−2 anomaly is a **genuine puzzle** — not a confirmed
signal of new physics and not a confirmed non-issue.  The discrepancy status is
0–5σ depending on which SM calculation is taken as reference.

### 7.2 The KK Correction at r_c = 12 M_Pl⁻¹

The Unitary Manifold compact dimension contributes a Kaluza–Klein tower of
massive spin-2 gravitons and one spin-1 boson (from B_μ) with masses:

```
M_KK_n  =  n / r_c  =  n × (M_Pl / 12)  ≈  n × 1.02 × 10¹⁸ GeV
```

The one-loop KK graviton correction to a_μ from the Arkani-Hamed–Dimopoulos–Dvali
formula is:

```
δa_μ^KK  ≈  (α / π) × (m_μ / M_KK_1)²  × F_spin2(c_s)
```

With m_μ = 105.66 MeV and M_KK_1 ≈ 10¹⁸ GeV:

```
(m_μ / M_KK_1)²  ≈  (105.66 × 10⁻³ GeV / 1.02 × 10¹⁸ GeV)²
               ≈  (1.04 × 10⁻¹⁹)²
               ≈  1.07 × 10⁻³⁸

δa_μ^KK  ≈  (1/137π) × 1.07 × 10⁻³⁸  ≈  2.5 × 10⁻⁴¹
```

This is **30 orders of magnitude smaller** than even the lattice-QCD-consistent
SM remainder, and ≈ 30 orders below the data-driven discrepancy
Δa_μ ≈ 261 × 10⁻¹¹ (≈ 2.6 × 10⁻⁹).

### 7.3 Honest Assessment

**The Unitary Manifold with r_c = 12 M_Pl⁻¹ CANNOT explain the muon g−2
anomaly through the KK graviton tower.**  The KK mass is at the Planck scale,
and the suppression (m_μ/M_KK)² ~ 10⁻³⁸ completely extinguishes any loop
contribution.  This is not a failure unique to the UM — ANY extra-dimensional
model with the compact radius at the Planck scale is decoupled from TeV-scale
physics by the same hierarchy.

This honest result is not the same as falsification.  The UM uses r_c = 12 in
Planck units to correctly reproduce the CMB spectral index and birefringence
angle.  It was never designed as a large-extra-dimension model.  The muon g−2
anomaly, if confirmed, requires new physics at or near the TeV scale — a
different energy regime from the Planck-scale extra dimension of the UM.

### 7.4 What the UM Could Say About Muon g−2

Three indirect connections are worth noting:

1. **The U(1) gauge field B_μ.**  The fifth dimension of the UM compactifies with
   a gauge field B_μ (the KK photon).  If the B_μ zero mode has a non-zero mass
   (from the Goldberger–Wise mechanism), it could act as a dark-photon mediator
   between muons and a hidden sector.  The UM does not currently derive the B_μ
   mass or its coupling to Standard Model fermions; this is an open gap.

2. **The Chern–Simons axion–photon coupling g_{aγγ}.**  The birefringence prediction
   uses an axion-like particle (ALP) coupling g_{aγγ} = k_cs × α_EM / (2π² r_c).
   The same ALP could contribute to a_μ via the 2-loop Barr–Zee diagram if the
   ALP couples to muons.  The UM does not derive the ALP–muon Yukawa coupling;
   this is another open gap.

3. **Forward prediction — Ω_μ dark sector.**  If the new physics behind Δa_μ is
   a boson at mass M_X ~ 100 MeV to 10 GeV, the UM predicts its coupling
   structure is constrained by the requirement that it not exceed the birefringence
   signal β ≈ 0.35°.  Future measurements of the B_μ zero-mode mass at
   fixed-target experiments (NA62, LHCb, Belle II) could constrain or rule out
   the ALP-mediated Barr–Zee explanation within the UM parameter space.

### 7.5 Summary

| Claim | Result |
|-------|--------|
| KK graviton loop correction to a_μ | ≈ 10⁻⁴¹ — negligible at r_c = 12 M_Pl⁻¹ |
| UM explains Δa_μ ≈ 261 × 10⁻¹¹ (data-driven gap) | **No.** Hierarchy m_μ ≪ M_KK extinguishes the correction. |
| UM is falsified by muon g−2 | **No.** UM was not designed as a TeV-scale model. |
| Open gap — B_μ dark photon coupling | **Not derived.** Requires fermion sector from UM reduction. |
| Indirect constraint via birefringence | **Potentially testable.** ALP–muon coupling bounded by β ≈ 0.35°. |

The muon g−2 anomaly is logged here as a **genuine open question** for the UM,
not as a prediction or a falsification.  Addressing it requires extending the UM
fermion sector beyond the current bosonic KK reduction.



---

## Summary (updated April 2026)

| Claim | Status | Key caveat |
|-------|--------|-----------|
| nₛ ≈ 0.9635 matches Planck | ✅ Matches | n_w = 5 is chosen, not derived |
| r_braided ≈ 0.0315 (braided (5,7), k_cs=74) | ✅ Satisfies BICEP/Keck | Braided (5,7) state resolves Q18 |
| β ≈ 0.35° matches birefringence hint | ✅ Matches | k_CS = 74 is fitted |
| FTUM convergence | **100%** — φ\* = A₀/(4G); universal | **RESOLVED** (April 2026) |
| w_KK ≈ −0.930 (dark energy EoS) | ✅ Consistent with DESI DR2 | c_s = 12/37 derived; w testable |
| H₀ tension (73.5 vs 67.4 km/s/Mpc) | ⚠️ Quantified, not resolved | CC problem separates KK from Hubble scale |
| Muon g−2 anomaly (Pillar 51; final result June 2025; Δa_μ ≈ 261 × 10⁻¹¹ vs data-driven; ~1σ vs lattice QCD) | ⚠️ Open question — bridged | KK correction δa_μ^KK ~ 10⁻⁴¹ (30 orders below anomaly); ALP Barr–Zee upper bound derived; fermion sector still not derived. Code: `src/core/muon_g2.py`, 98 tests. |
| Irreversibility from 5D | Conjectural | KK tower truncated; ADM formalism absent |
| CMB amplitude gap (Pillars 52, 57) | ⚠️ Partially addressed — residual open | A_s at pivot resolved by COBE normalization (λ_COBE unique). Pillar 57 (`src/core/cmb_peaks.py`) proposes radion amplification (φ_today/φ_SLS = n_w×2π≈31.4) to reduce acoustic-peak deficit from ×4–7 to ×1.3, but full analytic closure requires Boltzmann transport. |
| φ₀ self-consistency / M_KK scale | ⚠️ **Partially closed** (April 2026) — neutrino-mass tie-in | M_KK ≈ 110 meV = M_KK_needed is within the Planck 2018 Σm_ν < 120 meV window. Brane tension derived from m_ν; ρ_eff within 1.37 orders of ρ_obs at m_ν = 50 meV; exact closure at m_ν ≈ 110 meV. Analytic proof from UM fermion sector is future work. Code: `src/core/zero_point_vacuum.py:radion_self_consistency_check()`, 42 new tests. |

*Theory, scientific direction, and framework: **ThomasCory Walker-Pearson.***  
*Document engineering and synthesis: **GitHub Copilot** (AI).*
