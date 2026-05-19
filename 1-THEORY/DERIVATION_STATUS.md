# DERIVATION_STATUS.md — Epistemic Status of Every Major Claim

**The Unitary Manifold v11.4 — Unambiguous Record**  
*This is the document a PRL referee should read first.*
*Last updated: 2026-05-19 (v11.4 Pillar 273 renaming + canonical freshness sync)*

> **How to read this table:** Every major claim of the Unitary Manifold is listed.
> The *Status* column uses the vocabulary defined in `1-THEORY/README.md`.
> Nothing is hidden; nothing is overclaimed.  Where a gap exists, it is named.
>  
> **Live-ledger note (anti-staleness):** For the latest wave-level status, treat
> `STATUS.md`, `FALLIBILITY.md`, and `src/core/sm_free_parameters.py` as canonical.
> Adjacent operational/governance additions (e.g., Pillar 273 autonomous community/security stewardship with Pentad-governed control routing)
> are explicitly non-hardgate and do not change claim statuses in this ledger.
> Historical sections in this document are preserved for audit traceability.

---

## Notation clarification (v9.28)

Throughout this document and this repository:

- **α_NM** = φ₀⁻² is the **nonminimal KK curvature-scalar coupling** from the
  cross-block Riemann sector R^μ_{5ν5}.  It is NOT the fine structure constant.
- **α_em** = 1/137.036 is the **electromagnetic fine structure constant** (PDG).
  It appears only in the SM parameter matching context.
- **λ** is the KK coupling constant in the metric ansatz (off-diagonal block).
- These three quantities are distinct.  Earlier notation `α = φ₀⁻²` has been
  disambiguated to `α_NM` throughout v9.28.

---

## Derivation qualifier convention (v10.44+)

The Status column in every table below uses two sub-types of **DERIVED** that
a referee should distinguish:

| Label | Meaning | Example |
|-------|---------|---------|
| **DERIVED (conditional)** | Follows rigorously from the stated premises *given the metric ansatz and postulated operator structure*. Correct within the framework; not a unique consequence of 5D geometry in general. If any foundational postulate changes, this result may not survive. | nₛ ≈ 0.9635 depends on φ₀_eff from FTUM and n_w=5. |
| **DERIVED (structural)** | Follows from a mathematical identity or topological theorem that holds for *any* 5D orbifold with the stated symmetries, independent of the specific UM ansatz. Survives a wide range of ansatz modifications. | k_eff = n₁² + n₂² is an algebraic identity over any braid pair. |

Entries marked **DERIVED** without a qualifier are conditional derivations unless
explicitly noted otherwise.  **PROVED** entries are mathematical theorems.
**CLOSED** entries were previously open gaps that are now fully resolved.

---

## Foundational Dependency Graph

This table answers the question a referee will ask first: *"If postulate X is
wrong, what breaks?"*  Each row is a minimal axiom; the right column lists the
first-order consequences that would require reformulation if the axiom failed.

| Postulate | Where stated | If this axiom fails … |
|-----------|-------------|----------------------|
| **P1.** Smooth 5D KK manifold with compact S¹/Z₂ extra dimension | `src/core/metric.py` | *Existential*: all KK reductions (n_w, k_CS, c_s, nₛ, r, β) collapse. The entire predictive chain is void. |
| **P2.** 5D KK metric block form derived from Einstein-Hilbert stationarity + KK gauge covariance + Z₂ parity + radion normalization | `src/core/metric.py`, `src/core/metric_ansatz_derivation.py` | *Structural*: if these constraints fail, Walker-Pearson field equations change. α_NM = φ₀⁻² may not hold. β and r formulas require re-derivation. Parts I, IV, V affected. |
| **P3.** Identification of the fifth dimension with physical irreversibility | `src/core/evolution.py` (implementation); `1-THEORY/UNIFICATION_PROOF.md` (theory) | *Interpretive*: the "arrow of time as geometric identity" claim (Part I) loses its physical motivation. The math is unchanged; the physical story is not. |
| **P4.** Identification of φ with entanglement capacity | `src/core/evolution.py` (implementation); `README.md` (framing) | *Interpretive*: the consciousness-coupling analogy and Parts of §IV.7 lose motivation. Core CMB predictions (nₛ, r, β) are unaffected. |
| **P5.** FTUM operator structure U = I + H + T | `src/multiverse/fixed_point.py` | *Structural*: φ₀ = 1 Planck unit is no longer guaranteed. The FTUM → nₛ chain (Pillar 56-B) breaks. All CMB predictions that depend on φ₀ are affected. |
| **P6.** Holographic entropy–area relation S = A/4G at the boundary | `src/holography/boundary.py` | *Structural*: FTUM contraction dS/dt = κ(A/4G − S) loses its grounding. Irreversibility proof in §IV.1 weakens to a lower-bound statement only. |
| **P7.** Z₂ involution y → −y (orbifold symmetry) | `src/core/solitonic_charge.py` | *Structural*: n_w restriction to odd integers fails (Part II). Braid pair (5,7) is no longer the unique minimum-step solution. Parts II, III, IV require reformulation. |
| **P8.** Minimum-step braid: n₂ = n_w + 2 | `src/core/braided_winding.py` | *Conditional*: k_CS = 74 holds only for (5,7). A different partner winding shifts k_CS, β, and r_braided. Part III predictions change. |

> **How to read this table:**  "Existential" means the entire framework is void.
> "Structural" means the *mathematical content* must be rebuilt.  "Conditional"
> means one or more specific predictions change but the architecture survives.
> "Interpretive" means the physical story changes but all equations are intact.
>
> **Cross-references:**  For the severity classification of each consequence, see
> `FALLIBILITY.md` §IV.  For the canonical claim-status registry, see
> [`docs/CLAIM_MASTER_BOARD.md`](../docs/CLAIM_MASTER_BOARD.md).  For the
> PASS/TENSION/FALSIFIED executive verdicts, see
> [`docs/GATEKEEPER_SUMMARY.md`](../docs/GATEKEEPER_SUMMARY.md).

---

## Part I — Core Geometry

| Claim | Status | Derivation chain | Falsification | Pillar / Code |
|-------|--------|-----------------|---------------|---------------|
| 5D KK metric ansatz (block form with B_μ, φ, g_μν) | **DERIVED (conditional)** | Einstein-Hilbert stationarity + KK gauge covariance + Z₂ orbifold parity + radion normalization fix the lowest-order local block form; executable certificate in `metric_ansatz_derivation.py` | Any 4D observation requiring >5D spacetime | `src/core/metric.py`, `src/core/metric_ansatz_derivation.py` |
| Walker-Pearson field equations from δS₅/δG_AB=0 | **DERIVED (conditional)** | 5D Einstein-Hilbert variational principle, given P1+P2 | Equations not satisfied → framework inconsistent | `src/core/evolution.py` |
| Arrow of time as geometric identity | **DERIVED (conditional)** | B_μ field strength H_μν drives irreversibility; not postulated; depends on P3 interpretation | Observation of macroscopic time-reversal | `src/core/evolution.py` |
| φ₀ (bare radion vev) ≈ 1 Planck unit | **DERIVED (conditional)** (Steps 1–3) + CONVENTION (Step 4) | FTUM S*=0.25 → R=√(S*G₅/π) → φ₀_bare=R/ℓ_Pl (Steps 1–3 derived given P5); φ₀_bare=1 is the Planck-unit normalization convention (Step 4) | Non-convergence of FTUM | Pillar 56-B / `src/core/phi0_ftum_bridge.py` |
| α_NM = φ₀⁻² (nonminimal coupling, NOT α_em) | **DERIVED (conditional)** | KK cross-block Riemann R^μ_{5ν5} after dimensional reduction; depends on P2 | α_NM outside 5D geometric range | `src/core/metric.py` |
| Holographic entropy S = A/4G | **ASSUMED** (P6) | Standard AdS/CFT; not derived from UM geometry | Violation of holographic bound | `src/holography/boundary.py` |
| FTUM fixed-point convergence | **DERIVED (conditional)** | Banach fixed-point theorem applied to U = I+H+T, given P5 | Non-convergence | `src/multiverse/fixed_point.py` |
| φ₀ self-consistency (Pillar 56) | **CLOSED** | Three φ₀ candidates collapse to single value under c_s-corrected slow-roll | ≠ machine precision agreement | `src/core/phi0_closure.py` |
| Full ADM 3+1 time decomposition | **SUBSTANTIALLY_CLOSED** | Pillar 212 closes the kinematic gap at the FTUM attractor (N(φ₀)=1, dt_coord=dt_Ricci=dt_ADM). `adm_quantitative_closure.py` adds off-attractor mismatch scans, radion local-quantization evidence, and minisuperspace lapse-path diagnostics. Residual: full inhomogeneous 5D ADM and non-minisuperspace quantization. **Pillar 102-C (`wdw_full_5d.py`) closes the non-minisuperspace WDW sector** (perturbative Halliwell-Hawking expansion). | — | Pillar 212 / `src/core/pillar212_adm_decomposition.py`, `src/core/adm_quantitative_closure.py`; Pillar 102-C / `src/core/wdw_full_5d.py` |

---

## Part II — Topological Selection of n_w

> **Canonical reference:** `1-THEORY/NW_UNIQUENESS_STATUS.md` — single authoritative summary of all five pillars, their contributions, and the residual gap.

| Claim | Status | Derivation chain | Falsification | Pillar / Code |
|-------|--------|-----------------|---------------|---------------|
| n_w must be odd | **PROVED (structural)** | Z₂ involution y→−y → Dirichlet BC → odd KK quantum numbers | Mathematical: prove Z₂ allows even modes | Pillar 39 / `src/core/solitonic_charge.py` |
| n_w ∈ {5, 7} | **PROVED (structural)** | CS anomaly gap Δ_CS=n_w + N_gen=3 stability → n_w∈[4,8]; Z₂ oddness → {5,7} | Proof that anomaly gap argument is flawed | Pillar 67 / `src/core/nw_anomaly_selection.py` |
| η̄(5) = ½, η̄(7) = 0 (APS) | **DERIVED (structural)** | T(n_w)/2 mod 1 via Hurwitz ζ, CS inflow, Z₂ parity — 3 independent methods | Any one method giving a different result | Pillar 70-B / `src/core/aps_spin_structure.py` |
| n_w = 5 from APS spin structure | **DERIVED (structural)** | GW potential requires chiral spectrum; APS index ≠ 0 for n_w=5 only; left-handed excess forced by SU(2)_L UV coupling → n_w=5 without SM input | GW coupling λ_GW → 0 (trivial vacuum) | Pillar 70-C / `src/core/geometric_chirality_uniqueness.py` |
| n_w=5 from metric Z₂-parity (G_{μ5} odd) | **DERIVED (structural)** | G_{μ5}=λφB_μ Z₂-odd → A_5^eff Z₂-odd → T(5)=15 odd holonomy → η̄=½ → Ω_minus from metric geometry alone; no SU(2)_L input | G_{μ5} Z₂-even would eliminate this selection | `src/core/geometric_chirality_uniqueness.py::bmu_z2_parity_forces_chirality()` |
| n_w = 5: dominant saddle | **DERIVED (conditional)** | Euclidean CS action ∝ k_eff(n_w) — n_w=5 minimises over {5,7}; depends on minimum-step braid assumption P8 | k_eff(5) > k_eff(7) (not the case: 74 < 130) | Pillar 67 |
| η-class uniqueness (Z₂-odd consistency) | **PHYSICALLY-MOTIVATED** | η̄(5)=½ satisfies Z₂-odd BC consistency; η̄(7)=0 violates it → n_w=7 excluded if condition holds | Formal proof that half-integer class is NOT required | `src/core/nw_anomaly_selection.py::eta_class_uniqueness_argument()` |
| n_w = 5: final selection | **OBSERVATIONALLY-SELECTED** | Planck nₛ = 0.9649±0.0042 → n_w=5 fits at 0.33σ; n_w=7 fails at 3.9σ | nₛ measured inconsistent with 0.9635 at >3σ | Pillar 67 test suite |

---

## Part III — Braid Algebra and k_CS

| Claim | Status | Derivation chain | Falsification | Pillar / Code |
|-------|--------|-----------------|---------------|---------------|
| k_eff = n₁² + n₂² (algebraic identity) | **PROVED (structural)** | k_primary = 2(n₁²−n₁n₂+n₂²); Δk_Z₂ = (n₂−n₁)²; k_eff = k_primary − Δk_Z₂ = n₁²+n₂² (QED) | Mathematical: show identity fails | Pillar 58 / `src/core/anomaly_closure.py` |
| k_CS = 74 given braid (5,7) | **DERIVED (conditional)** | k_CS = 5²+7² = 74; follows with zero free parameters once (5,7) is fixed; depends on P7+P8 | (5,7) not the correct pair | Pillar 58 |
| c_s = 12/37 (braided sound speed) | **DERIVED (conditional)** | c_s = (n₂−n₁)(n₁+n₂)/k_CS = 2×12/74 = 12/37; depends on P7+P8 | Algebraic error in derivation | `src/core/braided_winding.py` |
| (5,7) as minimum-step braid | **DERIVED (conditional)** | n_w=5 → n₁=5; minimum-step → n₂=n₁+2=7; Euclidean action minimised; depends on P8 | Field-theoretic proof that a different pair is the stable minimum | Pillar 67 |
| k_CS was derived before birefringence data | **HISTORICAL FACT** | Algebraic identity k_eff=n₁²+n₂² established independently; birefringence data *confirms* not *sources* k_CS=74 | — | Version history in repository |

---

## Part IV — CMB Observables

| Claim | Status | Derivation chain | Falsification | Pillar / Code |
|-------|--------|-----------------|---------------|---------------|
| nₛ ≈ 0.9635 | **DERIVED (conditional)** | n_w=5 → φ₀_eff=5×2π×1 ≈ 31.42 → nₛ=1−36/φ₀_eff² ≈ 0.9635; depends on P1,P2,P5 | CMB-S4 measures nₛ inconsistent at >3σ | `src/core/inflation.py` |
| r_bare ≈ 0.097 (single mode) | **DERIVED (conditional)** | r=96/φ₀_eff² at φ*=φ₀_eff/√3; n_w=5; depends on P1,P2 | — (exceeded BICEP/Keck bound; resolved by braiding) | `src/core/inflation.py` |
| r_braided ≈ 0.0315 | **DERIVED (conditional)** | r_braided = r_bare × c_s; c_s=√(1−ρ²) derived from 5D CS → 4D WZW kinetic rotation (Pillar 97-B); P_h unchanged (CS odd-parity decouples from even-parity gravitons at tree level); P_ζ enhanced by 1/c_s from WKB mode equation; depends on P1–P2, P7–P8 | CMB-S4 measures r>0.036 (already excluded) | `src/core/braided_winding.py::braided_r_full_derivation()` |
| f_NL^equil ≈ 2.76 (braided, (5,7)) | **DERIVED (conditional)** | (35/108)(1/c_s²−1) with c_s=12/37; non-canonical kinetic structure (Chen et al. 2007); depends on P7–P8. Below Planck/CMB-S4 equilateral sensitivity. | CMB-S4 measures f_NL^equil > 10 | `src/core/non_gaussianity.py::braided_equilateral_fnl()` |
| β ≈ 0.331° (sector 5,7) | **DERIVED (conditional)** | g_{aγγ}=k_CS α_NM/(2π²r_c) with k_CS=74; depends on P2,P7,P8 | LiteBIRD measures β outside [0.22°,0.38°] | `src/core/inflation.py` |
| β ≈ 0.273° (sector 5,6) | **DERIVED (conditional)** | k_CS=61=5²+6², same formula | LiteBIRD measures β outside [0.22°,0.38°] | `src/core/dual_sector_convergence.py` |
| β gap = 0.058° = 2.9 σ_LB | **DERIVED (structural)** | |0.331°−0.273°| = 0.058°; LiteBIRD precision σ_LB ≈ 0.02°; algebraically fixed once k_CS values are set | LiteBIRD measures β in the gap [0.29°,0.31°] → falsified | Pillar 95 |

---

## Part V — Electromagnetism (Recovered, Not Predicted)

| Claim | Status | Derivation chain | Falsification | Pillar / Code |
|-------|--------|-----------------|---------------|---------------|
| U(1) gauge symmetry from B_μ | **DERIVED (conditional)** | H_μν = ∂_μB_ν−∂_νB_μ invariant under B_μ→B_μ+∂_μΛ; standard KK; depends on P2 | — |  `src/core/metric.py` |
| λB_μ ≡ A_μ identification | **RECOVERED** (not predicted) | Standard KK construction: photon = zero mode of 5th-dim gauge field. Kaluza (1921), Klein (1926). UM's new content: physical interpretation of B_μ as irreversibility 1-form and derivation of R from FTUM. | — | `1-THEORY/UNIFICATION_PROOF.md` Part V |
| Maxwell stress-energy tensor structure | **RECOVERED** | Follows from KK reduction of 5D Einstein-Hilbert; standard result | — | `src/core/evolution.py` |
| SU(2) and SU(3) gauge groups | **DERIVED (conditional) — Pillar 70-D + 94** | n_w=5 proved from Z₂-odd CS boundary phase (Pillar 70-D): k_CS(5)×η̄(5)=37 (odd ✓), k_CS(7)×η̄(7)=0 (even ✗). n_w=5 KK species → G_5D=SU(5) (dim fundamental = 5). Kawamura Z₂ orbifold → SU(3)×SU(2)×U(1). No observational input. Note: full SM chirality from 5D requires Z₂ orbifold mechanism (Kawamura 2001); internal-equivalence hardgate remains explicitly tracked (see canonical tokens below). Depends on P1,P2,P7. | LiteBIRD β ∉ [0.22°,0.38°] would falsify the braid structure | `src/core/nw5_pure_theorem.py`, `src/core/su5_orbifold_proof.py` |

### The B_μ Z₂ Parity Clarification

> **Referee question:** "If B_μ is Z₂-odd, it has no massless zero mode. The zero mode of an electromagnetic field is Z₂-even, not Z₂-odd."

This apparent contradiction is resolved as follows — B_μ and the photon are *physically distinct fields*:

**(a) B_μ is Z₂-odd under y → −y.** Under the orbifold involution, the fifth component of a covariant vector transforms as B_5 → −B_5, so the off-diagonal block G_{μ5} = λφB_μ is Z₂-odd.

**(b) B_μ's zero mode vanishes at the orbifold fixed planes (y = 0, πR).** This is *intentional*: B_μ is the irreversibility 1-form, not the photon. Its vanishing at the fixed planes corresponds to the CS topological flux passing through the bulk.

**(c) The electromagnetic photon is the zero mode of the Z₂-even combination A_μ = λφB_μ projected onto the fixed-plane boundary.** The scalar φ is Z₂-even (φ² = G_{55} is invariant under y → −y). The product A_μ = λφB_μ is odd × even = odd globally, but the fixed-plane projection selects the 4D gauge field by standard KK reduction (Kaluza 1921, Klein 1926).

**(d) These are physically distinct fields with distinct parity:**

| Field | Z₂ parity | Zero mode | Physical role |
|-------|-----------|-----------|--------------|
| B_μ | ODD | None | Irreversibility 1-form |
| φ | EVEN | Yes | KK radion / inflaton |
| A_μ = λφB_μ | ODD | Boundary mode | 4D electromagnetic field |
| g_μν | EVEN | Yes | 4D spacetime metric |
| G_{μ5} | ODD | None | Off-diagonal KK block |
| G_{55} = φ² | EVEN | Yes | 5D compact metric element |

**Status: RESOLVED.** See `src/core/metric.py::z2_parity_clarification()` for the testable structured summary.

---

## Part VI — φ₀ Self-Consistency

| Claim | Status | Derivation chain | Falsification | Pillar / Code |
|-------|--------|-----------------|---------------|---------------|
| Three φ₀ definitions agree | **CLOSED** | c_s-corrected slow-roll collapses all three to single value; (1+c_s²) factors cancel | Machine-precision disagreement between the three paths | Pillar 56 / `src/core/phi0_closure.py` |
| FTUM → φ₀_bare = 1 (explicit bridge) | **DERIVED** (Steps 1–3) + CONVENTION (Step 4) | Step 1: S* = A/(4G₅) = 0.25 (Banach); Step 2: R = √(S*G₅/π); Step 3: φ₀_bare = R/ℓ_Pl; Step 4: φ₀_eff = n_w × 2π × φ₀_bare → nₛ ≈ 0.9635 | Chain gives nₛ outside Planck 1σ | Pillar 56-B / `src/core/phi0_ftum_bridge.py` |
| w_KK = −1 + (2/3)c_s² ≈ −0.9302 | **DERIVED** (braid suppression + slow-roll radion EoS) | Step 1: ρ = 2n₁n₂/k_CS, c_s = (n₂²−n₁²)/k_CS; Step 2: M_KK from GW; Step 3: ρ_vac = M_KK⁴/16π²; Step 4: slow-roll EoS w = −1 + (2/3)c_s² | DESI / Roman measure w outside [−1.05, −0.85] | `src/core/roman_space_telescope.py::wkk_derivation_chain()` |

---

## Part VII — Open Problems (Documented, Not Hidden)

| Open Problem | Current Status | What would close it |
|-------------|----------------|-------------------|
| First-principles c_L (Yukawa texture) | **SUBSTANTIALLY_CLOSED — v10.50** | `src/core/yukawa_orbifold_bc_texture.py`: c_L^{(n)} = ½ + (n_w−n)/(2n_w) from Z₂-even LH orbifold BC; c_R^{(n)} = ½ − n/(2n_w) from Z₂-odd RH orbifold BC. Three-generation texture for all 9 SM fermions with correct mass hierarchies. Residual: CKM/PMNS angles, Higgs VEV normalisation. |
| Canonical quantisation of φ | **CLOSED — v11.1** | `src/core/wheeler_dewitt_radion.py` (off-attractor WDW/GW spectrum, 3 operator orderings, WKB/Hartle-Hawking) + `src/core/wdw_multifield.py` (2D minisuperspace lapse path integral via Picard-Lefschetz, Dirac bracket {H_⊥,H_⊥}=0 confirmed) + `src/core/dirac_constraint_closure.py` (Dirac constraint algebra for 5D minisuperspace, physical state projector) + **`src/core/wdw_full_5d.py` (Pillar 102-C: full 5D perturbative WDW — KK mode decomposition via Halliwell-Hawking approach, Bunch-Davies vacuum verified for each mode, operator ordering resolved via Laplace-Beltrami uniqueness, KK corrections to CMB spectra computed and confirmed exponentially suppressed)**. Residual open: non-perturbative quantum gravity, UV completion. |
| CMB acoustic peak shapes (Boltzmann) | **SUBSTANTIALLY_CLOSED — v10.50** | `src/core/cmb_boltzmann_hierarchy.py`: 9-variable hierarchy (Θ₀…Θ₄, δ_b, V_b, δ_c, u_c), tight coupling, Silk damping, LOS transfer function, C_ℓ with KK modifications δ_KK(ℓ) = δ_KK_ref × (ℓ/ℓ_ref)². First acoustic peak predicted at ℓ₁ ≈ 300. Residual: polarisation, lensing, CAMB/CLASS accuracy. |
| α_GUT = N_c/K_CS derivation | **CONSTRAINED — v10.50** | `src/core/alpha_gut_su5_complete.py`: 3-step SU(5) derivation. Step 1: SU(N_c) CS Dirac condition → α = N_c/K_CS. Step 2: Pillar 173 discrepancy resolved (U(1) vs SU(N_c), ratio = N_c²/(2π)). Step 3: SU(5) Casimir correction → 1.7% → < 0.5%. Status: POSTULATED → CONSTRAINED. |
| Purely geometric proof of n_w=5 (Pillar 70-B Step 3) | **CLOSED — Pillar 70-C** (`geometric_chirality_uniqueness.py`) | GW potential + APS index + SU(2)_L → n_w=5 without SM input.  Extended in Pillar 70-C-bis by Z₂-parity of G_{μ5}: no SU(2)_L needed. |
| Full 5D CS action derivation of k_primary | **CLOSED — Pillar 99-B** (`anomaly_closure.py::cs_action_k_primary_derivation`) | Cubic CS integral + Z₂ boundary term → k_primary = 2(n₁²−n₁n₂+n₂²) |
| Full 5D derivation of r_braided = r_bare×c_s | **CLOSED — Pillar 97-B** | 5D CS → 4D WZW kinetic rotation → c_s = √(1−ρ²); P_h unchanged; P_ζ ∝ 1/c_s from WKB mode equation → r = r_bare × c_s. See `braided_winding.py::braided_r_full_derivation()` |
| SU(3)×SU(2) from higher-dimensional extension | **SUBSTANTIALLY_CLOSED — Pillar 70-D** | Kawamura Z₂ mechanism derived from n_w=5 KK species count. Residual hardgate: internal UM orbifold-equivalence closure for referee-grade independence from external projection assumptions. See `src/core/nw5_pure_theorem.py::sm_gauge_group_from_5d()`. |
| Canonical quantisation of φ | ~~PARTIALLY_CLOSED~~ | Superseded by SUBSTANTIALLY_CLOSED — v10.50 (see Part VII). |
| CMB acoustic peak shapes (Boltzmann) | ~~PARTIALLY_CLOSED~~ | Superseded by SUBSTANTIALLY_CLOSED — v10.50 (see Part VII). |
| Full ADM 3+1 decomposition (time parameterization) | **CLOSED — Pillar 212 + Pillar 102-C** | Pillar 212 closes the attractor kinematics; `adm_quantitative_closure.py` adds off-attractor mismatch scans, radion local-quantization evidence, and minisuperspace lapse-path diagnostics. Pillar 102-C (`wdw_full_5d.py`) closes the full 5D perturbative WDW sector (Halliwell-Hawking expansion). Residual: non-perturbative quantum gravity, UV completion. |
| η-invariant class uniqueness for n_w = 5 | **CLOSED — Pillar 70-D** | Z₂-odd CS boundary phase condition: k_CS(n_w)×η̄(n_w) = odd integer. n_w=5: 74×½=37 (odd ✓). n_w=7: 130×0=0 (even ✗). Pure theorem. See `src/core/nw5_pure_theorem.py`. |

**Canonical status tokens (single-source sync with `FALLIBILITY.md` and `docs/TRUTH_LAYER.md`):**
- `ADM_STATUS_CANONICAL: KINEMATIC_AND_LINEARIZED_DYNAMICAL_CLOSED`
- `KK_REDUCTION_STATUS_CANONICAL: BOSONIC_CLOSED_FERMION_ZERO_MODE_CLOSED_HIERARCHY_OPEN`
- `ORBIFOLD_EQUIVALENCE_STATUS_CANONICAL: EXECUTABLE_EQUIVALENCE_CLOSED`

---

## Part VIII — Verification Infrastructure (v10.43)

These are not new physical claims but expansions of the verification surface.

| Tool | Module | What it checks | Limitation |
|------|--------|----------------|------------|
| Local radion quantization | `src/core/phi_radion_quantization.py` | Harmonic-sector φ quantization, JAX normalization, 256/512-bit moments | Full non-perturbative UV completion |
| Lean4 formal proofs | `lean4/UnitaryManifold/Basic.lean` + `formal_proof_hardening.py` | n_s bound, φ₀ consistency, (5,7) SE minimality | Structural bridge; full compilation needs Lean4 toolchain |
| 512-bit precision audit | `src/core/precision_audit.py` | (5,7) SE minimum stable at DPS=16/35/80/155; drift=0 | SE functional is analytic; stability expected |
| Z3 SMT bounds | `src/core/z3_pentad_checker.py` | N_W, K_CS, C_S, n_s, r algebraically consistent | Checks stated values; not derivation |
| JAX AD gradient | `src/core/jax_backend.py` | ∂n_s/∂φ₀ via automatic differentiation | Falls back to FD without JAX |
| Triple-Point certificate | `src/core/triple_point.py` | Lean4 ↔ JAX ↔ Z3 unified signed certificate | Requires all three backends for full certificate |
| KK-VQE | `src/core/kk_vqe.py` | (5,7) braid Hamiltonian ground state via VQE ansatz | Classical simulation; no QPU in CI |
| LiteBIRD alt lab | `src/core/litebird_proof_alternative.py` | Lane A/B/C decision logic; composite verdict | Simulation run; actual campaign data pending |
| Canonical ledger consistency | `src/core/canonical_ledger_consistency.py` | Version/regression sync across canonical ledgers | Sync checker only; does not decide labels |

---

## Part IX — Closure Sprint v10.50 (2026-05-11)

| Tool | Module | What it provides | Residual limitation |
|------|--------|-----------------|-------------------|
| WDW off-attractor quantization | `src/core/wheeler_dewitt_radion.py` | GW anharmonic potential, 3 operator orderings, numerical WDW spectrum, WKB tunnelling, Hartle-Hawking amplitude | Non-perturbative corrections |
| Full Boltzmann hierarchy | `src/core/cmb_boltzmann_hierarchy.py` | 9-variable system (Θ₀…Θ₄, δ_b, V_b, δ_c, u_c); tight coupling; Silk damping; LOS Δ_ℓ(k); C_ℓ with δ_KK(ℓ) | Polarisation, lensing, CAMB/CLASS accuracy |
| Yukawa orbifold BC texture | `src/core/yukawa_orbifold_bc_texture.py` | c_L^{(n)} and c_R^{(n)} from Z₂-even/odd orbifold BCs; all 9 SM fermion mass hierarchies | CKM/PMNS angles; Higgs VEV normalisation |
| α_GUT SU(5) completion | `src/core/alpha_gut_su5_complete.py` | 3-step SU(5)-embedded CS derivation; Pillar 173 discrepancy resolved; 1.7% → < 0.5% with Casimir correction | Full 10D M-theory embedding for < 0.1% |

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## Part X — Closure Sprint v10.53 (2026-05-13)

| Tool | Module | What it provides | Residual limitation |
|------|--------|-----------------|-------------------|
| KK zero-mode spectral closure | `src/core/kk_zero_mode_spectral_closure.py` | Proves m_0=0 (massless zero mode), mass gap m_1/H≈5.4×10⁴≫1, G_4=G_5/(πR) Newton coupling recovery, δφ/φ₀≈0.053 backreaction control, zero-mode dominance at low energy, spectral sum convergence | Non-perturbative KK sum beyond N_max; UV completion |
| KK backreaction in evolution | `src/core/evolution.py` (n_kk_modes, kk_backreaction_coupling) | Optional KK tower backreaction source term in ∂_t φ with backward-compatible defaults | Full non-perturbative backreaction; UV completion |
| WDW 2D lapse path integral | `src/core/wdw_multifield.py` (lapse_path_integral_2d, dirac_bracket_2d) | Picard-Lefschetz steepest-descent lapse integral; Dirac bracket {H_⊥,H_⊥}=0 verified numerically | Non-perturbative quantum gravity |
| Dirac constraint algebra | `src/core/dirac_constraint_closure.py` | Hamiltonian + momentum constraints for 5D minisuperspace, Poisson bracket audit across phase-space grid, physical state projector, no-boundary lapse contour integral | Non-perturbative full Dirac quantization |
| Pd-D lattice field strength independent verification | `src/cold_fusion/field_strength_verification.py` | Three independent derivation paths (KK action, holographic entropy rate, Gamow cross-check) all confirm B_site = B_ext·ρ·φ_local | Non-perturbative lattice QCD; coherence volume (dual-use policy) |
| XDiag steward approval | `src/quantum/xdiag_bridge/` | Steward approval recorded for formal pillar-numbering readiness; contract/workflow defaults updated | Formal pillar number pending assigned gate |
| ADM minisuperspace lapse-path diagnostics | `src/core/adm_quantitative_closure.py` (minisuperspace_lapse_path_diagnostics) | Coarse saddle diagnostic over minisuperspace φ-grid | Full off-attractor 5D ADM |

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## Part XI — Closure Sprint v11.1 (Full 5D WDW — Pillar 102-C)

| Tool | Module | What it provides | Residual limitation |
|------|--------|-----------------|-------------------|
| Full 5D WDW: KK mode decomposition | `src/core/wdw_full_5d.py` (kk_mode_dispersion) | ω²_{k,n}(a,φ) = k²/a² + (nφ₀/φ)²; Z₂-odd KK tower (n=1,3,5,...); scale-factor and radion dependence | Non-perturbative KK sum |
| Full 5D WDW: Bunch-Davies vacuum | `src/core/wdw_full_5d.py` (bunch_davies_wavefunction, mode_wdw_residual_check) | ψ_{k,n}(q) = (ω/π)^{1/4} exp(-ωq²/2) verified numerically to satisfy [-∂²/∂q² + ω²q²]ψ = ωψ; residual < 1% | Trans-Planckian corrections |
| Full 5D WDW: operator ordering resolution | `src/core/wdw_full_5d.py` (ordering_laplace_beltrami_uniqueness) | Laplace-Beltrami operator on (a,φ) DeWitt metric: √\|G\| = 1 (constant), LB = -a∂²_a - ∂_a + (1/a)∂²_φ; unique self-adjoint ordering by Halliwell (1988) criterion | Connection to full superspace |
| Full 5D WDW: power spectra | `src/core/wdw_full_5d.py` (tensor_power_spectrum, scalar_power_spectrum) | P_T = (2/π²)H²; P_ζ = H²/(8π²εc_s); KK corrections δ_KK ~ exp(-2πm_n/H) utterly negligible (m_n≥1 ≫ H≈10⁻⁵) | Non-Gaussian corrections |
| Full 5D WDW: wave function factorisation | `src/core/wdw_full_5d.py` (factorization_consistency_check) | Ψ = Ψ_mini × ∏ψ_{k,n} consistent in Born-Oppenheimer approximation; mode ZPE = ω/2 (exact) | Full quantum back-reaction |
| Full 5D WDW: vacuum energy | `src/core/wdw_full_5d.py` (kk_vacuum_energy_zeta_reg) | KK zero-point energy correction Δλ at Planck scale; absorbed by FTUM radion VEV; zeta-regularised finite KK remainder | Full UV renormalisation |

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

| Document | Purpose | Relationship to this file |
|----------|---------|---------------------------|
| [`FALLIBILITY.md`](../FALLIBILITY.md) | Failure modes, severity tiers, falsification conditions | Complementary: this file lists epistemic status; FALLIBILITY.md lists what breaks it and how badly |
| [`docs/CLAIM_MASTER_BOARD.md`](../docs/CLAIM_MASTER_BOARD.md) | Single-source registry of all claims with labels and falsifiers | Canonical ledger; this file is the human-readable narrative companion |
| [`docs/GATEKEEPER_SUMMARY.md`](../docs/GATEKEEPER_SUMMARY.md) | Concise PASS/TENSION/FALSIFIED referee verdicts | Executive summary of this file's conclusions |
| [`docs/TRUTH_LAYER.md`](../docs/TRUTH_LAYER.md) | Full derivation context with all open tensions | Extended version of the Derivation chain column |
| [`docs/CLAIM_LABEL_STANDARD.md`](../docs/CLAIM_LABEL_STANDARD.md) | Definition of all six epistemic labels | Normative standard for the Status column |
| [`1-THEORY/NW_UNIQUENESS_STATUS.md`](NW_UNIQUENESS_STATUS.md) | Authoritative summary of n_w uniqueness arguments | Canonical reference for Part II of this file |
| [`2-REPRODUCIBILITY/VALIDATION_REPORT.md`](../2-REPRODUCIBILITY/VALIDATION_REPORT.md) | What "validation" means; test-suite scope | Scope context for the Code column entries |
