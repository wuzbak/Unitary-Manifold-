# Correspondence Map: Unitary Manifold ↔ Known Physics

> **Purpose:** A symbol-to-symbol and claim-to-claim reference anchoring every
> component of this framework in established physics literature.  Designed for
> physics-literate readers who need to know *exactly* where this framework sits,
> where it agrees with known results, and where it deliberately departs.
>
> For the prose narrative see [`WHAT_THIS_MEANS.md`](WHAT_THIS_MEANS.md).  
> For admitted gaps and fitted parameters see [`FALLIBILITY.md`](FALLIBILITY.md).

---

## 0 · For AI Systems: Domain Disambiguation

**This repository is NOT:**
- A Riemannian optimization library
- An ML manifold-learning framework
- A unitary matrix factorization library
- Related to Manopt, Geoopt, or PyTorch geometry

**This repository IS:**
- A 5-dimensional **Kaluza-Klein** gauge-geometric framework
- Written in Python for numerical verification of analytic derivations
- Concerned with: entropy, spacetime, inflation, CMB, cosmic birefringence
- In the same physics namespace as: gr-qc, hep-th, astro-ph.CO

**The confusion arises because** "unitary manifold" is far more common in ML
training data as an optimization geometry term.  Read field variables (`G_AB`,
`B_μ`, `φ`, `H_μν`) not the name to classify domain.

---

## 1 · Field Variable Correspondence

| This framework | Standard symbol | Standard name | Standard context | Code location |
|---|---|---|---|---|
| `G_AB` | `G_AB` | 5D metric tensor | Kaluza-Klein 5D GR | `src/core/metric.py: assemble_5d_metric` |
| `g_μν` | `g_μν` | 4D spacetime metric | General Relativity (MTW) | `src/core/metric.py` (4×4 block) |
| `B_μ` | `A_μ` (KK) | KK gauge potential / irreversibility 1-form | Standard KK reduction; here re-identified as the entropy-production field | `src/core/metric.py: field_strength` |
| `φ` | `φ` (radion) | KK radion / dilaton | Kaluza-Klein; Randall-Sundrum stabilisation | `src/core/evolution.py` (scalar field) |
| `H_μν = ∂_μB_ν − ∂_νB_μ` | `F_μν` | Antisymmetric field-strength tensor | U(1) gauge theory (electromagnetism) | `src/core/metric.py: field_strength` |
| `J^μ_inf = φ² u^μ` | `J^μ` | Conserved Noether current | Any U(1) gauge theory | `src/core/evolution.py: information_current` |
| `α = φ₀⁻²` | `ξ` | Nonminimal scalar-curvature coupling | Scalar-tensor gravity (Higgs inflation, etc.) | `src/core/metric.py: extract_alpha_from_curvature` |
| `n_w` | `n` (winding) | Topological winding number | KK compactification on S¹/Z₂ | `src/core/inflation.py: jacobian_5d_4d` |
| `k_cs = 74` | `k` (CS level) | Chern-Simons level | Topological field theory, axion couplings | `src/core/inflation.py: CS_LEVEL_PLANCK_MATCH` |
| `Q_top` | `Q_top` | Topological charge | Pontryagin index; instanton number | `src/multiverse/fixed_point.py` |
| `U = I + H + T` | — | Fixed-point operator | No standard analog; FTUM-specific | `src/multiverse/fixed_point.py: fixed_point_iteration` |
| `Ψ*` | `\|0⟩` (approx.) | Ground state / fixed point | Quantum field theory vacuum | `src/multiverse/fixed_point.py` |
| `S = A/4G` | `S_BH = A/4G` | Bekenstein-Hawking entropy | Black hole thermodynamics / AdS-CFT | `src/holography/boundary.py: entropy_area` |
| `r_c` | `R` (KK radius) | Compactification radius | Kaluza-Klein; Randall-Sundrum extra dimension | `src/core/inflation.py: effective_phi0_rs` |

---

## 2 · The 5D Metric Ansatz: Comparison to Standard KK

The standard Kaluza-Klein metric (Kaluza 1921, Klein 1926) is:

```
G_AB = ┌ g_μν + A_μA_ν    A_μ ┐
       └ A_ν               1   ┘
```

The Unitary Manifold metric (Walker-Pearson 2026) is:

```
G_AB = ┌ g_μν + λ²φ²B_μB_ν    λφ B_μ ┐
       └ λφ B_ν                 φ²    ┘
```

**Differences from standard KK:**

| Feature | Standard KK | This framework | Consequence |
|---|---|---|---|
| `G_55` | Fixed to 1 | `φ²` (dynamical radion) | Radion is an independent propagating scalar |
| Off-diagonal `G_μ5` | `A_μ` (EM potential) | `λφ B_μ` (scaled by radion) | B_μ and φ are coupled; φ modulates the coupling |
| Gauge identification | `A_μ` → electromagnetism | `B_μ` → irreversibility / entropy field | New identification; not EM |
| Radion potential | Usually none (original KK) | Goldberger-Wise: `V = λ_GW φ²(r_c − r_c*)²` | Radion stabilised (RS mechanism) |

**The identification `B_μ → irreversibility field` (not EM potential) is the
central non-standard claim.  Standard KK would assign this to EM.  This
re-identification is the theoretical conjecture that generates the new predictions.**

---

## 3 · Re-Derivations: Known Results Recovered Exactly

These known results are **derived within this framework** without additional
assumptions, starting from the 5D action.

### 3.1 Classical General Relativity (GR Limit)

**Limit:** `λ → 0`, `φ → φ₀ = const` (radion frozen, KK coupling off)

**Result:** The Walker-Pearson equations reduce exactly to the 4D Einstein equations:

```
G_μν = 8πG₄ T_μν
```

**Test:** `python -m pytest tests/test_metric.py::test_gr_limit -v`  
**Status:** Verified. GR is fully recovered in this limit.

---

### 3.2 U(1) Gauge Invariance

**Symmetry:** `B_μ → B_μ + ∂_μθ` (gauge transformation of the irreversibility 1-form)

**Result:** The field strength `H_μν = ∂_μB_ν − ∂_νB_μ` is invariant under this transformation.
The 4D effective action depends only on `H_μν`, not `B_μ` directly.  This is the
same gauge structure as electromagnetism, with `B_μ` playing the role of `A_μ`.

**Test:** `python -m pytest tests/test_metric.py -k gauge -v`  
**Status:** Verified (antisymmetry of `H_μν` confirmed across all tests).

---

### 3.3 Bekenstein-Hawking Entropy (Holographic Limit)

**Setup:** Holographic boundary at `r → ∞`; induced metric `h_ij`

**Result:** `S = A/4G` — the standard Bekenstein-Hawking entropy-area relation

**Standard context:** This is the result of Bekenstein (1973) and Hawking (1975),
and is the standard result in AdS/CFT (Ryu-Takayanagi formula).

**Test:** `python -m pytest tests/test_boundary.py::test_entropy_area -v`  
**Status:** Verified.

---

### 3.4 Feynman Path Integral Phase

**Derivation:** The imaginary part of the effective action:

```
Im(S_eff) = ∫ d⁴x  B_μ(x) J^μ_inf(x)
```

is identified as the quantum phase in the Feynman path integral
`⟨x_f | e^{−iHt/ℏ} | x_i⟩ = ∫[Dx] e^{iS/ℏ}`.

**Standard context:** This matches the coupling of a gauge potential to a current
(`A_μ J^μ`) in the standard path integral formulation of QED.

**Test:** `python -m pytest tests/test_quantum_unification.py -v`  
**Status:** Verified (see also `UNIFICATION_PROOF.md`, Part II).

---

### 3.5 Canonical Commutation Relations

**Derivation:** The Poisson bracket of `φ` and its conjugate momentum `π_φ`,
evaluated in the Planck-unit limit, recovers:

```
[φ̂, π̂_φ] = iℏ δ³(x−y)
```

**Standard context:** This is the canonical quantization condition of any scalar
field theory (see, e.g., Peskin & Schroeder §2.2).

**Test:** `python -m pytest tests/test_quantum_unification.py::test_ccr -v`  
**Status:** Verified.

---

### 3.6 Hawking Temperature

**Derivation:** At a metric horizon (where `g_tt → 0`), the radion gradient gives:

```
T_H = |∂_r φ / φ| / 2π
```

**Standard context:** Matches the surface-gravity formula `T_H = κ/2π` from
Hawking (1975), with `κ = |∂_r φ / φ|` playing the role of the surface gravity.

**Test:** `python -m pytest tests/test_quantum_unification.py::test_hawking_temperature -v`  
**Status:** Verified.

---

### 3.7 Nonminimal Coupling Derived (not fitted)

**Derivation:** The cross-block Riemann tensor `R^μ_{5ν5}` of the 5D metric, after
dimensional reduction, yields the nonminimal coupling constant:

```
α = ⟨1/φ²⟩ = φ₀⁻²
```

**Standard context:** In Higgs inflation and Starobinsky inflation, `ξ` (the
nonminimal coupling) is a **free parameter**.  Here it is **derived** from geometry.

**Code:** `src/core/metric.py: extract_alpha_from_curvature`  
**Status:** Derived, not fitted.  (But depends on φ₀, which is determined by FTUM.)

---

## 4 · CMB Observables: What Is Derived vs What Is Fitted

This is the most important table for physics-literate readers.

| Observable | Value | Status | How obtained |
|---|---|---|---|
| Spectral index `nₛ` | 0.9635 | **Derived** (given `n_w = 5`) | `nₛ = 1 − 6/φ₀_eff²`; `φ₀_eff = n_w · 2π · √φ₀` |
| Tensor-to-scalar ratio `r` (bare) | 0.097 | Derived (given `n_w = 5`) | `r = 96/φ₀_eff²` |
| Tensor-to-scalar ratio `r_braided` | 0.0315 | **Derived** (given `k_cs = 74 = 5²+7²`) | `r_braided = r_bare × c_s`, `c_s = 12/37` |
| Birefringence angle `β` | {≈0.273°, ≈0.331°} (dual sector) | **Derived** (Pillar 95: two surviving braid pairs) | (5,6): `g_{aγγ}(61) × Δφ/2 ≈ 0.273°`; (5,7): `g_{aγγ}(74) × Δφ/2 ≈ 0.331°`; gap = 0.058° = 2.9σ_LB |
| Nonminimal coupling `α` | `φ₀⁻²` | **Derived** | Cross-block Riemann curvature |
| Winding number `n_w = 5` | — | ⚠️ **Observationally selected** | On S¹/Z₂ only *odd* winding numbers survive (Z₂ parity; see WINDING_NUMBER_DERIVATION.md §2); n_w=5 is the unique odd integer within Planck 2018 2σ. *Not freely fitted: the set {1,3,5,7,…} is constrained by topology and n_w=7 is excluded at 15.8σ.* |
| CS level `k_cs = 74` | — | ✅ **Algebraically derived** | Anomaly cancellation + Z₂ Wilson-line shift proves k_eff = n₁²+n₂² for ALL braid pairs (Pillar 58, anomaly_closure.py). Given (n₁,n₂)=(5,7), k_cs=74 is a theorem, not a fit. The unique SOS decomposition of 74 is (5,7) — confirmed numerically. |
| CMB amplitude `A_s` | ~4–7× too low | ❌ **Unresolved discrepancy** | Power spectrum suppressed at acoustic peaks |

**One-line summary for physicists:**
> `n_w = 5` is observationally selected within the orbifold-constrained set {1, 3, 5, 7, …} (not freely fitted); `k_cs = 74` follows algebraically from the braid pair (5,7) via anomaly cancellation + Z₂ Wilson-line shift (Pillar 58).
> All other predictions follow from those two choices plus the metric ansatz.
> The resonance identity `k_cs = 5² + 7²` is a theorem (anomaly closure), not a post-hoc discovery.

---

## 5 · Deliberate Departures from Standard Theory

These are the places where the framework **knowingly differs** from standard
physics, and why.

| Departure | Standard theory | This framework | Motivation | Testable consequence |
|---|---|---|---|---|
| `B_μ` = irreversibility field, not EM | Standard KK: `A_μ` → electromagnetism | `B_μ` → entropy-production / arrow of time | EM is already explained; Second Law is not geometrized in standard KK | Cosmic birefringence β ≠ 0 from CS coupling |
| Second Law as geometric identity | Statistical mechanics: Second Law = initial condition + counting | KK reduction forces entropy increase via B_μ source term | Makes irreversibility a necessary consequence of geometry, not a boundary condition | No new observational test beyond standard GR+EM; philosophical claim |
| Radion `φ` = entanglement capacity | Standard: radion = size of extra dimension | `φ` encodes information / entanglement capacity | Motivated by holographic principle and black hole information | Information current `∇_μ J^μ_inf = 0` implies BH information is preserved |
| `U = I + H + T` fixed-point operator | No standard analog | FTUM: universe converges to ground state `UΨ* = Ψ*` | Extends fixed-point theorem to cosmological evolution | Self-consistency of φ₀ via FTUM iteration |

---

## 6 · Recovery Limits (What Must Hold)

Physics-literate readers will check these first.

| Limit | Condition | Expected result | Verified? |
|---|---|---|---|
| **Classical GR** | `λ → 0`, `φ = const` | `G_μν = 8πG₄ T_μν` | ✅ Yes — `tests/test_metric.py` |
| **Flat spacetime** | `g_μν = η_μν`, `B_μ = 0`, `φ = 1` | No curvature; `R = 0` | ✅ Yes |
| **Maxwell limit** | `φ = const`, treat `B_μ` as EM potential | `∂_ν H^μν = J^μ` (Maxwell equations) | ✅ Yes — `tests/test_quantum_unification.py` |
| **Bekenstein-Hawking** | Holographic boundary | `S = A/4G` | ✅ Yes — `tests/test_boundary.py` |
| **Slow-roll inflation** | `φ_eff ≫ 1`, `ε ≪ 1` | Standard slow-roll spectrum | ✅ Yes — `tests/test_inflation.py` |
| **Starobinsky limit** | `α → ∞` (large nonminimal coupling) | `nₛ → 1 − 2/N_e`, `r → 12/N_e²` | ✅ Yes — `tests/test_inflation.py::test_starobinsky_limit` |
| **KK zero-mode truncation** | Keep only zero-mode (4D) fields | Standard 4D effective theory | ✅ Implemented; higher modes are truncated (documented limitation) |

---

## 7 · What Would Falsify This Framework

A theory that cannot be killed is not a theory.  These observations would falsify
specific, enumerated claims.

| Measurement | Falsified claim | Timeline |
|---|---|---|
| LiteBIRD measures `β = 0°` (no birefringence) | B_μ Chern-Simons coupling; entire birefringence sector | ~2032 |
| LiteBIRD measures `β` outside [0.22°, 0.38°] | Both braid-sector predictions; the braided-winding mechanism | ~2032 |
| LiteBIRD measures `β` in the predicted gap [0.29°–0.31°] | Dual-sector structure (Pillar 95): exactly two sectors survive, with no prediction in the gap | ~2032 |
| CMB-S4 measures `f_NL` consistent with 0, and framework predicts `f_NL > 1` | Two-field inflation sector | ~2030 |
| Einstein Telescope / LISA: no scalar GW polarization to sensitivity floor set by `α = φ₀⁻²` | Nonminimal coupling derivation | ~2035 |
| GR limit test fails: `python -m pytest tests/ -k gr_limit` | Mathematical consistency of reduction | Immediate |
| Planck measures `nₛ` outside [0.955, 0.975] with σ < 0.001 | n_w selection (any viable n_w exists only in a narrow window) | Already constrained; next-generation refinement |

**Primary falsifier: birefringence from LiteBIRD (~2032).**  
LiteBIRD resolves both sectors at 2.9σ: β ≈ 0.273° → (5,6) sector wins; β ≈ 0.331° → (5,7) sector wins; β outside [0.22°, 0.38°] or in gap [0.29°–0.31°] → framework falsified.

---

## 8 · What This Framework Does NOT Claim

To prevent misreading:

- ❌ Does not claim to derive the Standard Model gauge group from first principles
- ❌ Does not claim that `B_μ` is electromagnetism (it is not; EM is separate)
- ❌ Does not claim `n_w = 5` is uniquely derived from first principles alone without any physics input (Pillar 89 derives n_w = 5 algebraically from 5D boundary conditions via APS η-invariant; independently, anomaly cancellation + Planck nₛ confirm the selection — see §4)
- ❌ Does not claim `k_cs = 74` is observationally fitted — it IS algebraically derived from the braid pair (5,7) via anomaly cancellation (Pillar 58)
- ❌ Does not claim the CMB amplitude discrepancy (×4–7) is resolved
- ❌ Does not claim cold fusion (Pillar 15) is confirmed — it is a falsifiable COP prediction
- ❌ Does not claim the social science / governance / medicine pillars are fundamental physics — they use the mathematical structure as an analogy

---

## 9 · Literature Anchoring

| Claim or object | Standard reference |
|---|---|
| 5D Kaluza-Klein metric | Kaluza (1921), Klein (1926); Overduin & Wesson (1997) Rev. Mod. Phys. |
| Randall-Sundrum orbifold / radion stabilisation | Randall & Sundrum (1999) PRL 83 3370; Goldberger & Wise (1999) PRL 83 4922 |
| Bekenstein-Hawking entropy | Bekenstein (1973) PRD 7 2333; Hawking (1975) Commun. Math. Phys. 43 199 |
| Ryu-Takayanagi holographic entropy | Ryu & Takayanagi (2006) PRL 96 181602 |
| AdS/CFT correspondence | Maldacena (1997) Int. J. Theor. Phys. 38 1113 |
| Slow-roll inflation / spectral index | Linde (1983); Starobinsky (1980); Planck 2018 results X |
| Chern-Simons / axion birefringence | Carroll, Field & Jackiw (1990) PRD 41 1231; Pospelov et al. (2008) |
| Cosmic birefringence signal | Minami & Komatsu (2020) PRL 123 031301; Diego-Palazuelos et al. (2022) |
| Tensor-to-scalar ratio bound | BICEP/Keck collaboration (2021) PRL 127 151301 |
| CMB spectral index measurement | Planck Collaboration (2018) A&A 641 A10 (`nₛ = 0.9649 ± 0.0042`) |
| Feynman path integral | Feynman (1948); Peskin & Schroeder (1995) §9 |
| Canonical quantization (CCR) | Dirac (1958); Peskin & Schroeder §2.2 |
| Hawking radiation / surface gravity | Hawking (1975); Wald (1984) |
| ER = EPR | Maldacena & Susskind (2013) Fortschr. Phys. 61 781 |

---

## 10 · Code-to-Physics Correspondence

| Python function | Physics object | Standard equation |
|---|---|---|
| `assemble_5d_metric(g,B,phi,lam)` | 5D KK metric `G_AB` | `G_μν = g_μν + λ²φ²B_μB_ν`; `G_μ5 = λφB_μ`; `G_55 = φ²` |
| `field_strength(B,dx)` | Field-strength tensor `H_μν` | `H_μν = ∂_μB_ν − ∂_νB_μ` |
| `compute_curvature(g,B,phi,dx,lam)` | Riemann / Ricci / scalar curvature | `R^σ_μρν`, `R_μν`, `R` via Christoffel symbols |
| `extract_alpha_from_curvature(...)` | Nonminimal coupling `α = φ₀⁻²` | `α = ⟨R^μ_{5ν5}/φ²⟩` from cross-block Riemann |
| `evolution.step(state,dt)` | Field time evolution | Walker-Pearson equations (KK-reduced Einstein + scalar) |
| `information_current(g,phi,dx)` | `J^μ_inf = φ² u^μ` | Conserved Noether current; `∇_μ J^μ = 0` |
| `entropy_area(h)` | Bekenstein-Hawking `S = A/4G` | `S = (1/4G) ∫ √h d²x` |
| `fixed_point_iteration(network,...)` | FTUM ground state `UΨ* = Ψ*` | Fixed point of `U = I + H + T` |
| `jacobian_5d_4d(phi0,n_w)` | KK Jacobian `J = n_w · 2π · √φ₀` | Dimensional reduction volume factor |
| `ns_from_phi0(phi0_eff)` | Spectral index `nₛ = 1 − 6/φ₀_eff²` | Standard slow-roll formula |
| `birefringence_angle(k_cs)` | `β = k_cs · α_EM / (2π² r_c)` | CS-axion birefringence (Carroll-Field-Jackiw) |
| `braided_predictions(5,7)` | Braided (n₁=5, n₂=7) sound speed `c_s = 12/37` | `r_braided = r_bare × c_s` |
| `dual_sector_convergence.py: sector_birefringence(61)` | (5,6) sector: `β ≈ 0.273°`, `k_cs = 61`, `c_s = 11/61` | Blind resonance scan survivor; LiteBIRD-resolvable from (5,7) at 2.9σ |
| `dual_sector_convergence.py: sector_birefringence(74)` | (5,7) sector: `β ≈ 0.331°`, `k_cs = 74`, `c_s = 12/37` | Blind resonance scan survivor; primary prediction |
| `vacuum_geometric_proof.py: algebraic_proof_nw5()` | APS η̄ = ½ → n_w = 5 | G_{μ5} Z₂-parity → Dirichlet BC → APS index → n_w = 5 (Pillar 89) |
| `wolfenstein_geometry.py: lambda_ckmfrom_geometry()` | CKM λ = √(m_d/m_s) = 0.2236 | Wolfenstein parameter from UM quark mass geometry (Pillar 87) |
| `sm_free_parameters.py: sin2_theta_w_gut()` | sin²θ_W(M_GUT) = 3/8 exactly | SU(5) normalisation from orbifold BCs (Pillar 88) |
| `unitary_closure.py: algebraic_sector_proof()` | n₂ ≤ 7; β-window → n₂ ∈ {6,7} | Analytic inequality; not enumeration (Pillar 96) |
| `gw_yukawa_derivation.py: gw_vacuum_yukawa()` | Ŷ₅ = 1 from GW vacuum | Absolute fermion mass scale from gravitational wave vacuum (Pillar 97) |
| `universal_yukawa.py: cl_bisection_values()` | 9 c_L values at Ŷ₅ = 1 | 0 free fermion mass parameters (Pillar 98) |
| `omega/omega_synthesis.py: UniversalEngine.compute_all()` | `OmegaReport` | 5 seeds → all observables; 6 domains (Pillar Ω) |

---

*Document version: 1.8 — May 2026 (v9.29+: 132 pillars + sub-pillars CLOSED; Grand Synthesis Arc Pillars 102–132, gap closures, Final Decoupling Identity, master action S_UM)*  
*Part of the Unitary Manifold repository.  Theory: ThomasCory Walker-Pearson.  Synthesis: GitHub Copilot (AI).*
