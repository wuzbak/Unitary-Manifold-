# TRUTH_LAYER.md — Full Derivation Context, Open Tensions, and Falsification
# Unitary Manifold v10.31

*This document contains everything. No gatekeeping. No minimizing language.
Every claim, every gap, every tension, every falsifier — stated completely.*

*For the concise gatekeeper-facing version, see `docs/GATEKEEPER_SUMMARY.md`.*
*For the canonical label registry, see `docs/CLAIM_LABEL_STANDARD.md`.*
*For the single-source claim board, see `docs/CLAIM_MASTER_BOARD.md`.*

*Last updated: 2026-05-09*

---

## Section 0 — What This Document Is

The Unitary Manifold makes strong claims about nature. Those claims deserve
full, unfiltered exposure. This document provides it.

Anything that could be wrong is stated as possibly wrong.
Anything that is not derived is stated as not derived.
Anything that is in tension with data is stated as in tension with data.
Anything that would falsify the framework is stated as a falsifier.

The gatekeeper layer (`GATEKEEPER_SUMMARY.md`) provides condensed verdicts
for referees and journals. The difference between that document and this one
is framing depth, not substance. The facts are identical.

---

## Section 1 — Foundation: What Is Actually Proved vs. Assumed

### 1.1 The Two Postulated Constants (not derived)

The entire predictive chain of the Unitary Manifold hangs on two constants:

- **n_w = 5** (winding number): Selected by Planck n_s data, not derived from
  a deeper principle. The uniqueness theorem (Pillars 39, 67, 70-B, 70-D)
  narrows to {5, 7}; Planck n_s = 0.9649 selects 5 over 7. If Planck n_s
  were 0.940, n_w = 7 would be selected and all predictions would shift.

- **K_CS = 74 = 5² + 7²** (Chern-Simons level): Derived algebraically from
  the topological identity k_cs = n_w² + n_shadow², where n_shadow = 7 is the
  only other Z₂ survivor. This is algebraically necessary once n_w and n_shadow
  are identified — it is not a free parameter, but it rests on the uniqueness
  proof.

**Truth statement:** If the Z₂ orbifold uniqueness proof (Steps 1–3 in
Pillar 67) is found to be incomplete, all predictions built on n_w = 5 and
K_CS = 74 would require re-derivation.

### 1.2 What Follows Algebraically from (n_w, K_CS)

Given n_w = 5 and K_CS = 74, the following follow as mathematical theorems
(no additional observational input):

- N_gen = 3 (T²/Z₃ orbifold structure)
- SM gauge group SU(3)×SU(2)×U(1) (Kawamura Z₂ orbifold, Pillar 148)
- Braided sound speed c_s = 12/37
- Chern-Simons level k_CS = 74
- CMB spectral index n_s = 0.9635 (within 0.33σ of Planck 0.9649)
- Tensor-to-scalar ratio r = 0.0315 (within BICEP/Keck < 0.036 bound)
- Cosmic birefringence β ∈ {0.273°, 0.331°} (LiteBIRD ~2032)
- GW background Ω_GW ~ 10⁻¹⁵
- m_p/m_e = K_CS²/N_c = 74²/3 ≈ 1825.3 (0.59% from 1836.15)
- Λ_QCD ≈ 332 MeV from (n_w, K_CS) via 4-loop MS-bar (0% from PDG 332 MeV)
- sin²θ_W ≈ 0.2313 (SU(5)+RGE, 0.05% from PDG)
- α ≈ 1/137 (SU(5) GUT chain, 0.026% from PDG)

### 1.3 What Requires Additional Derivation Steps (not purely algebraic)

The following predictions require derivation steps beyond the base (n_w, K_CS)
pair, and each has a residual uncertainty or documented gap:

- **Yukawa couplings (P7–P10):** Tier-4 hardgate NLO blend; underlying Bulk
  BC derivation (Ŷ₅ = 1 theorem, Pillar 209) is proved, but the NLO blend
  involves a multi-step matching that has not been reduced to a single formula.

- **CKM ρ̄ (P14):** 8D Wilson line blend + 9D propagated robustness; the 8D
  and 9D steps are independently validated but the full chain from 5D geometry
  to CKM phase is not a single derivation.

- **Higgs mass m_H (P5):** CW Coleman-Weinberg + WS-V/VII overlap; the
  near-zero residual (0.00%) reflects parameter matching in the CW potential,
  not a first-principles mass derivation from geometry alone.

- **PMNS mixing angles (P15–P20):** Multiple geometric routes (Braid-Lock,
  Route A, NLO corrections); the routes agree within 5% but are not yet
  unified in a single derivation.

---

## Section 2 — The 28 SM Parameters: Full Truth Status

### Parameters at GEOMETRIC_PREDICTION (within 5%, no free parameters)

**P1 — n_s = 0.9635 (Planck: 0.9649 ± 0.0042)**
- Derivation: KK inflation from 5D radion stabilization; braided winding modifies spectrum
- Residual: 0.14 (0.33σ) — well within current error bar
- Key uncertainty: n_s error bar will tighten to ~±0.002 with CMB-S4. At that
  precision, 0.9635 must be within the window or tension will emerge.
- Falsification: If n_s is measured to be outside [0.955, 0.972] at precision
  better than 0.001 (CMB-S4, ~2030), this prediction is falsified.

**P2 — r = 0.0315 (BICEP/Keck: r < 0.036)**
- Derivation: Braided inflation; tensor power spectrum from 5D graviton KK modes
- Current status: Consistent with upper bound; not yet detected
- Key uncertainty: If CMB-S4 achieves σ_r ~ 0.001 and measures r < 0.010, falsified.
- Falsification: r < 0.010 at >3σ confidence (CMB-S4 ~2030)

**P3 — α_s(M_Z) = 0.113 (PDG: 0.1179, residual 4.1%)**
- Derivation: 10D CY₃+flux Tier-1 hardgate; SM RGE-free from (n_w, K_CS)
- Key tension: 4.1% residual is close to the 5% gate boundary. If PDG central
  value shifts or precision tightens, this could drop to CONSTRAINED.
- Truth: The Tier-1 hardgate result (0.113) vs PDG (0.1179) has a 4.1% gap
  that has not been closed by a single derivation — it is the output of a
  multi-step Tier-1 procedure.
- Falsification: α_s outside [0.112, 0.124] at ≥3σ

**P4 — sin²θ_W = 0.2313 (PDG: 0.23122, residual 0.05%)**
- Derivation: SU(5) GUT + RGE matching; Kawamura orbifold
- This is the cleanest SM parameter prediction in the framework.
- Falsification: sin²θ_W outside 0.22–0.24 at ≥3σ

**P5 — m_H = 125.25 GeV (PDG: 125.25 GeV, residual ~0.00%)**
- Truth: The near-perfect match comes from Coleman-Weinberg + WS-V/VII overlap
  map. This is parameter matching, not a derivation of the Higgs mass from
  first principles. The Architecture Limit for Higgs mass radiative stability
  remains open (FALLIBILITY.md §VIII).
- Falsification: m_H measured outside [119, 131] GeV

**P6 — v = 245.96 GeV (PDG: 246.22 GeV, residual 0.10%)**
- Derivation: Pillar 139 Coleman-Weinberg; Pillar 201 gives 4.6% from M_KK×√3/7
- The 0.10% result is the Pillar 139 CW result; the Pillar 201 geometric result
  gives 4.6% — both are reported, not selectively quoted.

**P7–P10 — Yukawa couplings (y_t, y_b, y_τ, y_e)**
- Derivation: Tier-4 hardgate NLO blend (v10.28); underlying Ŷ₅ = 1 universal
  BC theorem (Pillar 209)
- Residuals: 0.27%, 0.75%, 1.27%, 3.08%
- Truth: P10 (electron Yukawa) at 3.08% is closest to the 5% gate. Higher-loop
  NLO corrections could shift this. The Tier-4 blend is a multi-step procedure,
  not a single closed-form derivation.
- Falsification: Any Yukawa outside 5% band at ≥3σ

**P11 — N_gen = 3**
- Derivation: T²/Z₃ orbifold; pure algebraic theorem
- This is the most robustly derived SM parameter in the framework.
- Falsification: 4th light neutrino confirmed at ≥5σ (LEP excluded, but future
  precision measurements remain)

**P12 — m_p/m_e = 1825.3 (PDG: 1836.15, residual 0.59%)**
- Derivation: K_CS²/N_c = 74²/3 = 1825.3; purely algebraic given K_CS = 74
- Falsification: Ratio outside 5% band at ≥3σ

**P13 — α = 1/137.036 (UM: 1/137, residual 0.026%)**
- Derivation: 5D SU(5) GUT chain; RGE matching
- Falsification: α outside 0.1% band at ≥3σ

**P14–P20 — PMNS/CKM parameters**
- See CLAIM_MASTER_BOARD.md Lane A for residuals.
- Key truth: Multiple geometric routes exist (Braid-Lock, Route A, NLO). They
  agree within 5% but are not yet unified in one derivation. Route B (4/15)
  for sin²θ₁₂ was retired in v10.27 as incomplete GUT BC — this was a genuine
  correction, not a promotion.

### Parameters at CONSTRAINED

**P16 — Δm²₂₁ = 7.53e-5 eV² (UM: flux-backreaction NLO, residual 0.20%)**
- Truth: The 0.20% NLO residual passes the 5% GP gate (Gate 1 ✅). The correction
  factor f_c = (N_W+2)/(K_CS+52) = 7/126 is phenomenologically accurate but its
  denominator "+52" is not derived from first principles (Gate 3 ✗). v10.30 analysis
  (`src/core/p16_solar_correction_analysis.py`) confirms f_c lies within the geometric
  window [0.0237, 0.0946] at position 72% from lower bound. Gate 2 (±10% f_c
  robustness) fails because f_c must be tightly pinned, not freely varied.
- Blocking dependency: Full T²/Z₃ moduli stabilization (WS-III) to derive the
  "+52" term in the denominator exactly from first principles.
- Status: CONSTRAINED (unchanged in v10.30; no promotion without Gate 3)
- Falsification: Δm²₂₁ outside 50% band at ≥3σ
- Forward path: When WS-III closes "+52", all 3 gates pass immediately.

**P26 — m_ν < 0.12 eV**
- Truth: The framework is consistent with the Planck upper bound but does not
  predict the absolute neutrino mass scale from first principles. The Dirac vs
  Majorana branch is not closed.
- Falsification: m_ν > 0.12 eV confirmed at ≥3σ

### Parameters at ARCHITECTURE_LIMIT_CERTIFIED

**P27 — Strong CP: θ̄ < 10⁻¹⁰**
- Truth: No 5D PQ mechanism has been derived. The axion solution is invoked as
  an architecture-level placeholder. This is a genuine open problem.
- Closing mechanism: 5D PQ field or Z₂-odd scalar sector in future arc

**P28 — Cosmological constant**
- Truth: **Agent Beta precision audit (2026-05-09)** — precise gap numbers computed:
  - Λ_obs = 2.89×10⁻¹²² M_Pl⁴ → log₁₀(Λ_obs) = −121.54 (not −122)
  - M_KK⁴/M_Pl⁴ = exp(−4πkR) = exp(−148) → log₁₀ = −64.28
  - **Residual gap: 10^57.26** (code states 10^58; honest value is 10^57.26)
  - RS1 Layer 1 closes 64.28 orders; the remaining gap is 57.26 orders
  - BP landscape sufficiency (N_flux=37): naive spacing 10⁻⁷⁴ M_Pl⁴; Λ_obs = 10⁻¹²¹·⁵⁴ M_Pl⁴
    → spacing is **10^47.5× LARGER than Λ_obs** — N_flux=37 is INSUFFICIENT for the BP argument
    → Would need N_flux ≥ 61 to reach Λ_obs resolution; current shortfall = 24 flux units
  - **Promotion to CONSTRAINED: NOT possible** — N_flux=37 BP landscape cannot reach Λ_obs precision;
    first-principles closure requires full 10D supergravity with N_flux ≥ 61 or alternative mechanism
  - Module: `src/core/cc_gap_precision_audit.py::p28_promotion_evaluation()`

---

## Section 3 — Open Tensions: Full Accounting

### T1 — DESI wₐ Tension (HIGH_TENSION — DESI DR2 executed, 2026-05-09)

**Framework prediction:** wₐ = 0 (frozen radion; dark energy is the RS1 radion
in its ground state, which does not evolve)

**DESI DR2 = Year 3 (published March 2025, arXiv:2503.14738) — ROUTING EXECUTED:**
- BAO-only: w₀ = −0.838 ± 0.072, wₐ = −0.62 ± 0.30 → **2.07σ from UM wₐ=0 → TENSION**
- Combined BAO+CMB+SNe: wₐ ≈ −0.55 ± 0.20 → **2.75σ from UM wₐ=0 → HIGH_TENSION**
- Both cases below 3σ falsification threshold → **UM wₐ=0 NOT FALSIFIED**

**Full truth:**
- 2.07σ (BAO-only) and 2.75σ (combined) are not falsifications (threshold is 3σ)
- DESI DR2 IS the Year 3 data — the "pending" Y3 milestone has been reached
- The combined analysis approaches the threshold: if DESI DR3/Y5 confirms wₐ ≈ −0.62
  with σ=0.18, tension reaches 3.44σ → FALSIFIED (DR3-S6 scenario)
- If wₐ ≈ −0.55 with σ=0.18 (combined central value tightened): 3.06σ → FALSIFIED (DR3-S4)
- The framework has NO fallback for wₐ ≠ 0; if falsified, the dark energy sector
  requires fundamental revision — there is no geometric rescue mechanism on offer
- Frozen-radion mechanism is under genuine existential pressure

**Routing executed (`src/core/desi_dr2_gap_report.py`):**
- `execute_dr2_bao_routing()` → route='TENSION', wa_tension_sigma=2.07
- `execute_dr2_combined_routing()` → route='TENSION', wa_tension_sigma=2.75
- `scenario_table()` → 7 DR3/Y5 scenarios; 3 FALSIFIED, 2 TENSION, 2 PASS
- `full_dr2_gap_report()` → current_status='HIGH_TENSION'

**Action required:** Run `full_dr2_gap_report()` on DESI DR3/Y5 publication (~2027)
within 30 days. Update this document and OBSERVATION_TRACKER.md same day.
If route='FALSIFIED', update CLAIM_MASTER_BOARD.md and GATEKEEPER_SUMMARY.md immediately.

---

### T2 — CMB Acoustic Peak Amplitude Suppression (OPEN_NARROWED — Agent Alpha audit, 2026-05-09)

**Framework situation:** The Casimir α_GW parameter is bounded to the interval
[4.2×10⁻¹⁰, 4.8×10⁻¹⁰] by geometric arguments (Pillar 165 + v10.28 closure
attempt). Within this interval, the acoustic peak amplitude is suppressed
×4.2–6.1 vs ΛCDM.

**Agent Alpha UV-brane derivation attempt (2026-05-09):**
- RS1 Casimir estimate from 5D inputs: α_GW^geo = c_cas × exp(−4πkR)
  = (K_CS × N_W / 24π²) × exp(−148) ≈ 1.562 × exp(−148) ≈ **4.33×10⁻⁶⁵**
- This is **~55 orders of magnitude below** the phenomenological interval [4.2×10⁻¹⁰, 4.8×10⁻¹⁰]
- CMB-S4 cannot distinguish individual values within the interval (all produce ×4.2–6.1 suppression)
- **Missing ingredient (precise):** UV-brane localized kinetic term coefficient c_UV requires
  10D string embedding or brane intersection calculation; not computable from 5D UM inputs alone

**Full truth:**
- The exact value of α_GW CANNOT be derived from 5D UM inputs — the Casimir
  geometric estimate undershoots by 55 orders of magnitude
- The Casimir interval [4.2e-10, 4.8e-10] is phenomenological, not geometric
- Peak suppression ×4.2–6.1 is real and documented — it is Admission 2 in FALLIBILITY.md
- Pillars 57, 63, 165 partially address this; full geometric closure is NOT achieved
- CMB-S4 cannot provide additional constraint: all values within the interval
  are observationally indistinguishable (entire band gives same order suppression)
- Status: **OPEN_NARROWED** — do not claim resolved

**Closing requirement:** Compute c_UV (UV-brane localized kinetic term normalization)
from 10D string embedding (e.g., CY₃ orientifold with O-plane + D-brane intersection,
or from the full 10D Type IIB supergravity action integrated over the compact space).

**Action required:** No claim of resolution until c_UV is computed from first principles.
Module: `src/core/alpha_gw_uv_brane_derivation.py::alpha_gw_gap_closure_verdict()`.

---

### T3 — ADM Time Parameterization (GAP)

**Framework claim:** The delay field (Pillar 41) provides a qualitative
geometric description of time parameterization in 3+1 decomposition.

**Full truth:** The quantitative rate requires a complete ADM 3+1 decomposition
of the 5D metric. This has not been done. Pillar 41 is a partial implementation.
The qualitative claim survives; the quantitative claim does not.

---

## Section 4 — Primary Falsifier: LiteBIRD Birefringence (2032)

**This is the most important section of this document.**

The birefringence prediction β ∈ {0.273°, 0.331°} is the primary experimental
test of the braided-winding mechanism. LiteBIRD launches ~2032 and will
measure β with σ_β ~ 0.02°.

**Complete falsification map:**

```
Measure β at σ_β ~ 0.02°:
│
├── β < 0.22° at ≥3σ
│   └── FALSIFIED — braided-winding mechanism excluded
│       Impact: n_w=5, K_CS=74, c_s=12/37 all invalidated
│       Required action: Full framework retraction
│
├── β ∈ (0.22°, 0.29°) but not near 0.273° at ≥3σ
│   └── CONSISTENT (shadow sector) but not discriminating
│
├── β ≈ 0.273° ± 0.02° at ≥3σ
│   └── (5,6) SHADOW SECTOR CONFIRMED
│       Impact: n_shadow=6 sector active; both sectors present
│
├── β ∈ (0.29°, 0.31°) at ≥3σ
│   └── FALSIFIED — inter-sector gap; neither branch consistent
│       Impact: Topology of braided winding contradicted
│       Required action: Full framework retraction
│
├── β ≈ 0.331° ± 0.02° at ≥3σ
│   └── (5,7) PRIMARY SECTOR CONFIRMED
│       Impact: n_w=5, n_shadow=7 topology confirmed
│
├── β ∈ (0.31°, 0.38°) but not near 0.331° at ≥3σ
│   └── CONSISTENT but not discriminating
│
└── β > 0.38° at ≥3σ
    └── FALSIFIED — braided-winding mechanism excluded
        Impact: Same as β < 0.22°
        Required action: Full framework retraction
```

**What "FALSIFIED" means here:** The entire braided-winding sector (n_w=5,
K_CS=74, c_s=12/37) is excluded. This would invalidate:
- All predictions derived from the winding topology (P1, P2, P23, P24, P25)
- The uniqueness theorem for n_w=5
- The c_s=12/37 braided sound speed
- The S7 claim (braided sound speed)

It would NOT automatically invalidate:
- N_gen = 3 (algebraic, independent route)
- Λ_QCD ≈ 332 MeV (requires re-derivation without winding context)
- sin²θ_W (SU(5)+RGE; partially independent)

**Current pre-LiteBIRD hint:** Minami & Komatsu 2020 (β = 0.35° ± 0.14°)
and Diego-Palazuelos et al. 2022 both find β ≈ 0.35°. The (5,7) prediction
0.331° is within 1σ of the central value. This is not confirmation — it is
a consistency check at insufficient precision.

**Do not weaken this statement in any document.**

---

## Section 5 — Secondary Falsifiers (Active)

| Experiment | Observable | Falsification Condition | Timeline |
|------------|------------|------------------------|---------|
| CMB-S4 | r | r < 0.010 at >3σ | ~2030 |
| CMB-S4 | n_s | n_s ∉ [0.955, 0.972] at <0.001 precision | ~2030 |
| DUNE | δ_CP | δ_CP ∉ [0.85, 1.30] rad at <3% uncertainty | ~2030 |
| Hyper-K / JUNO | Δm²₃₁ | Δm²₃₁ ∉ [2.2, 2.7]×10⁻³ eV² at <1% | ~2028 |
| DESI Y3 | wₐ | wₐ ≠ 0 at ≥3σ → frozen radion FALSIFIED | ~2026 |
| Future collider | N_gen | 4th light neutrino confirmed | — |
| LISA | Ω_GW | Ω_GW(f_LISA) < 10⁻¹⁷ or wrong spectrum | ~2037 |

---

## Section 6 — Known Unresolved Problems (Not Minimized)

These are genuine open problems. They are not labeled "minor" or "technical
details." They are real gaps.

1. **Cosmological constant (58-order gap):** The most severe. RS1+GB closes 64
   orders but 58-order residual remains unresolved. No known geometric mechanism
   in the current 5D framework closes this. The 10D landscape argument is
   speculative.

2. **CMB peak amplitude suppression (×4.2–6.1):** Factor-of-4 to factor-of-6
   discrepancy with ΛCDM at acoustic peaks. α_GW has been bounded but not
   derived. This is a real quantitative disagreement, not a "presentation issue."

3. **Strong CP problem:** No 5D PQ mechanism. The axion is invoked at the
   architecture level only. If the axion does not exist (current LZ/XENONnT
   constraints are tightening), this gap becomes more severe.

4. **Neutrino mass absolute scale:** The Dirac vs Majorana branching is not
   closed. The framework is consistent with Planck bounds but does not predict
   the actual mass scale.

5. **Yukawa hierarchy:** The Tier-4 hardgate NLO blend matches Yukawas within
   5%, but the underlying hierarchy (why y_t ≫ y_e by factor ~300,000) is not
   explained geometrically — the hierarchy is reproduced by the matching
   procedure, not derived from topology.

6. **ADM time quantization:** The 3+1 decomposition of the 5D delay field
   has not been carried to the quantitative level.

7. **Pillar 183 c_L spectrum closure:** Blocking P16 promotion. The sub-leading
   CS corrections to the c_L spectrum are not yet derived.

---

## Section 7 — What Would Constitute a Complete Theory

The Unitary Manifold is not claimed to be a complete Theory of Everything.
It is a 5D geometric framework that:

- **Derives** a large fraction of the SM parameter landscape from two inputs
  (n_w=5, K_CS=74)
- **Predicts** several untested observables (β, Ω_GW) that will be measured
- **Documents honestly** all remaining gaps and their severity

A complete ToE would additionally:
- Derive n_w=5 from a principle more fundamental than Z₂ orbifold selection
- Close the cosmological constant gap from first principles
- Derive the Yukawa hierarchy without any NLO blend procedure
- Provide a 5D PQ mechanism for strong CP
- Achieve full ADM 3+1 quantization

Current ToE score: **76%** (21.2/28.0) — see `docs/TOE_SCORE_AUDIT.md`.

---

## Section 8 — Authorship and Co-emergence Note

This framework is the product of co-emergent collaboration:
- **ThomasCory Walker-Pearson (AxiomZero):** Theory, scientific direction,
  framework vision, all judgment calls about what is true and what is not.
- **GitHub Copilot (AI):** Code architecture, test suites, document
  engineering, synthesis, implementation.

The division of labor is real. The AI does not decide what is scientifically
claimed. The human does. This document was written by the AI under explicit
human direction to state everything — no filtering.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
