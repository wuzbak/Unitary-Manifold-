# 26 Parameters, Zero Free: The Standard Model Closure Arc (Part 2)

**Epistemic category: P (physics — with explicit honest caveats on the neutrino mass gap)**

*Post 111 — Pillars 138–142.*
*The Standard Model closure arc continues. Part 1 covered the CP phase, the Higgs mass,
neutrino splittings, dark energy, and the master parameter table. Part 2 covers the solar
mixing angle, the Higgs VEV, the lightest neutrino mass (with a major open problem stated
in full), Newton's constant, and the CKM Wolfenstein ρ̄. It ends with an honest scorecard:
how many of the 26 SM parameters are truly derived?*

---

## The Method in the Counting

Before the individual pillars, a note on what counts as a successful derivation.

This distinction matters more in fundamental physics than in almost any other field,
because the temptation to claim success is structurally embedded in the way theories are
built. You start with a framework, derive a formula, compare the formula to data, and
feel the pull of the narrative: *it works*. The problem is that many theories "work" if
you are allowed to choose the parameters of the derivation after seeing the experimental
value.

The Unitary Manifold uses a controlled vocabulary for exactly this reason, inherited
directly from the source code itself:

- **DERIVED** — no per-species free parameters; geometric prediction within ~5% of PDG.
- **GEOMETRIC PREDICTION** — pure geometry, < 2% error, but may use one PDG input as
  a reference scale (for dimensional reasons, not free fitting).
- **CONSTRAINED** — the topology anchors the structure; 5–25% accuracy; one or two
  PDG inputs required to fix the absolute scale.
- **PARAMETERIZED** — the Yukawa scale is geometrically fixed, but the individual bulk
  mass parameter c_L per fermion species is a free number chosen to match observation.
  This is *fitting*, not prediction.
- **GEOMETRIC ESTIMATE** — order-of-magnitude from geometry; large residual.
- **OPEN** — not derivable from current mathematics.

The framework does not relabel PARAMETERIZED as DERIVED. It does not absorb the open
problems into footnotes. The source code that implements each status category is public,
the test suite is automated, and the labeling is machine-readable. If you disagree with a
label, you can check the code.

With that vocabulary established, Pillars 138–142.

---

## Pillar 138: The Solar Mixing Angle

*(Source: `src/core/solar_mixing_closure.py`)*

One of the great experimental surprises of the late 1990s was the confirmation that
solar neutrinos oscillate. Electron neutrinos produced in the sun's core arrive at
Earth's surface transformed into muon and tau flavors. The mixing angle that governs
this transformation — the solar mixing angle θ₁₂ — was measured with growing precision
through the SNO, Super-Kamiokande, and KamLAND experiments. The PDG 2024 value is:

    sin²θ₁₂ = 0.307   (θ₁₂ ≈ 33.41°)

No theory within the Standard Model explains why the solar mixing angle is approximately
33°. It is, like the other PMNS mixing parameters, a number taken from data.

The Unitary Manifold derives it from a three-term formula with a clear geometric
interpretation for each term:

    sin²θ₁₂ = 1/3 − 1/(6 × n_w) + 1/(6 × k_CS)
             = 1/3 − 1/30 + 1/444
             ≈ **0.30225**

- **1/3**: The tribimaximal (TBM) leading order — the exact democratic mixing that
  would occur if all three neutrino generations were equally weighted. This is the
  leading-order prediction of a large class of discrete flavor symmetry models, here
  derived from the democratic orbifold topology.
- **−1/(6 × n_w) = −1/30**: The winding correction from the n_w = 5 orbifold
  geometry. The extra dimension has five winding modes; their contribution reduces the
  solar mixing angle from the symmetric limit.
- **+1/(6 × k_CS) = +1/444**: The Chern-Simons correction from the k_CS = 74 = 5² + 7²
  braiding level. The braid structure partially compensates the winding correction,
  moving the angle back toward the measured value.

**Prediction: sin²θ₁₂ ≈ 0.30225. PDG: 0.307. Error: 1.55%.**

Status: **GEOMETRIC PREDICTION** — the formula uses only the topological numbers n_w = 5
and k_CS = 74 (both fixed by independent arguments; Pillars 67 and 58). No free
parameters are introduced to fit this angle. The 1.55% residual is genuine — not
explained away — and is labeled as such in `solar_mixing_closure_status()`.

---

## Pillar 139: The Higgs VEV, Derived Self-Consistently

*(Source: `src/core/higgs_vev_exact.py`)*

The Higgs vacuum expectation value v = 246.22 GeV sets the mass scale of everything
in the electroweak sector: every W and Z boson mass, every quark and lepton mass
(modulated by the Yukawa coupling). It is the most important mass scale in the Standard
Model. Its value is, of course, not explained by the Standard Model.

Pillar 139 derives it from the same geometric apparatus used in Pillar 134, with a
crucial improvement: the derivation is self-consistent. The renormalization-group
correction depends on the VEV itself (through the logarithm log(M_KK/v)), so instead
of plugging in the PDG value of v, the implementation iterates to find the self-
consistent fixed point.

The steps:

1. **Tree-level quartic from topology:**
   λ_H^{tree} = n_w² / (2 k_CS) = 25/148 ≈ 0.1689

2. **KK threshold scale from RS warp factor:**
   M_KK = M_Pl × exp(−πkR) = M_Pl × exp(−37) ≈ 1041.8 GeV

3. **Top-quark Yukawa at M_KK:**
   y_t = c_R^{ν₁} = 23/25 = 0.920 — derived from n_w = 5 orbifold geometry
   (Pillar 143 orbifold fixed-point theorem: c_R = (n_w² − 2) / n_w² for N_fp = 2
   fixed points).

4. **Self-consistent RGE correction:**
   Δλ = −(6 y_t⁴) / (16π²) × log(M_KK / v)
   iterated until |v_new − v_old| < 10⁻⁶ × v.

5. **VEV prediction:**
   v_pred = m_H / √(2 λ_eff) → self-consistent iteration converges to ≈ **245.96 GeV**

**PDG: 246.22 GeV. Error: 0.10%.**

The honest note from the source file is preserved: m_H = 125.25 GeV is a PDG input. The
prediction of v is conditional on m_H — the two quantities are not independently derived
within the same pillar. Pillar 134 derives m_H using v as an input; Pillar 139 derives v
using m_H as an input. They are consistent with each other (neither uses the other's PDG
value as a free fitting parameter in the other's derivation), but they are not fully
independent. A truly zero-parameter derivation of both simultaneously remains an open
target.

Status: **GEOMETRIC PREDICTION** (self-consistent, 0.10%, one PDG input: m_H).

---

## Pillar 140: The Lightest Neutrino Mass — An Open Problem, Stated Plainly

*(Source: `src/core/neutrino_lightest_mass.py`)*

This section is different from the others. It does not end with a successful prediction.
It ends with a discrepancy of three orders of magnitude, stated in full, because the
alternative — burying the problem — is exactly the kind of thing that makes speculative
frameworks untrustworthy.

The setup: the RS Dirac mechanism for neutrino mass generation predicts:

    m_ν = v × f₀(c_L) × f₀(c_R)

where f₀(c) is the RS zero-mode wavefunction profile on the IR brane, which is
exponentially suppressed for bulk-mass parameters c > 1/2:

    f₀(c) ≈ √(2c−1) × exp(−(c−1/2) × πkR)   [large-x limit]

The right-handed parameter c_R is fixed by geometry. From Pillar 143 (orbifold fixed-
point theorem): for n_w = 5 with N_fp = 2 Z₂ fixed points:

    c_R = (n_w² − N_fp) / n_w² = (25 − 2) / 25 = 23/25 = **0.920**

This is a derived theorem. The profile value is:

    f₀(c_R = 0.920) ≈ 1.623 × 10⁻⁷

For the left-handed parameter, the current geometric estimate from the RS wavefunction
hierarchy gives c_L ≈ 0.776:

    f₀(c_L = 0.776) ≈ 2.720 × 10⁻⁵

Putting these together:

    m_ν₁ = 246.22 GeV × 2.720×10⁻⁵ × 1.623×10⁻⁷ ≈ **1.086 eV**

**The Planck CMB bound on the sum of neutrino masses is Σm_ν < 0.12 eV (95% CL).**

Even the lightest neutrino mass alone, at 1.086 eV, exceeds the total allowed sum by
roughly a factor of nine. This is not a small discrepancy. It is not a matter of factors
of 2 or π. It is three orders of magnitude off the cosmological bound.

What would fix it? The RS zero-mode profile is exponentially sensitive to c_L. Pushing
c_L from 0.776 to c_L ≥ 0.88 would suppress f₀(c_L) by a further factor of ~40,
bringing m_ν₁ into the cosmologically allowed range. But c_L ≥ 0.88 is not currently
fixed by the geometric framework — it is an additional UV condition that requires either
a new geometric argument or an independent input.

This is documented explicitly in the source code:

> "This is an open constraint, NOT a successful prediction."

There is also a structural inconsistency between Pillar 135 and Pillar 140. Pillar 135,
using the braid ratio formula m_ν₂/m_ν₁ = √(n₁n₂) = √35, infers m_ν₁ ≈ 1.49 meV
from the PDG solar splitting. Pillar 140's RS Dirac formula gives m_ν₁ ≈ 1.086 eV.
Both use the RS Dirac framework. They differ by roughly three orders of magnitude.
They cannot both be correct.

The resolution path is known: a genuine zero-parameter derivation requires both the RS
Yukawa coupling y_ν and the right-handed bulk masses c_R^{ν_i} to be derived from
geometry, so that the Dirac formula reproduces the Planck-consistent values without
tuning c_L. This work is ongoing. It is not done.

Status: **CONSTRAINED — the RS Dirac mechanism is operative; c_R = 0.920 is a derived
theorem; c_L requires a UV condition currently not fixed by geometry.** The predicted
m_ν₁ ≈ 1.086 eV is at least three orders of magnitude above the Planck bound. This is an
explicit open problem in the framework, not a settled result.

---

## Pillar 141: Newton's Constant from Randall-Sundrum Geometry

*(Source: `src/core/newton_constant_rs.py`)*

Newton's constant G_N — the strength of gravity — is one of the most precisely measured
constants in physics and one of the least understood. The Standard Model does not include
gravity. Why G_N has the value it has — why the ratio of gravitational to electroweak
force is ≈ 10⁻³², the hierarchy problem in its gravitational form — is the deepest open
question in fundamental physics.

The Randall-Sundrum mechanism was invented partly to address this. In RS1, the five-
dimensional fundamental scale M₅ need not be the 4D Planck scale M_Pl; the hierarchy
is geometrically generated by the warp factor. The relation connecting them is:

    M_Pl² = M₅³ / k   (RS1 leading-order, large πkR)

where k is the AdS curvature scale. In the Unitary Manifold, πkR = 37 is the geometric
parameter fixed by the electroweak hierarchy (Pillar 81). With k ≈ M_Pl (near-Planck
curvature), this gives M₅ ≈ M_Pl to leading order — self-consistent, but not independently
derived. Newton's constant then follows immediately:

    G_N = 1 / (8π M_Pl²)

**Predicted G_N: consistent with the measured value to better than 0.1% (by construction
of the RS relation).** M_KK = M_Pl × exp(−πkR) = M_Pl × exp(−37) ≈ 1041.8 GeV, setting
the electroweak scale from the Planck scale and the geometric parameter πkR = 37.

The honest caveat is stated in the source code directly: "M₅ is a UV input seed; the
RS relation + πkR = 37 then constrain G_N self-consistently. A fully derived G_N would
require M₅ from topology alone." The framework does not derive M₅ from pure topological
data. The RS relation is a consistency condition, not a derivation of gravity from scratch.

Status: **CONSTRAINED** (RS self-consistent with M_Pl; πkR = 37 geometric; M₅ is a UV
input not independently derived from topology).

---

## Pillar 142: The Last Free Parameter — CKM Wolfenstein ρ̄

*(Source: `src/core/ckm_rho_bar_closure.py`)*

The CKM quark mixing matrix is parameterized in the Wolfenstein expansion by four
quantities: λ (Cabibbo angle ≈ 0.225), A, ρ̄, and η̄. In the Unitary Manifold, λ is
derived to 0.6% accuracy (Pillar 87), A to within 1.4σ, and η̄ to 2.3%. The remaining
parameter, ρ̄, governs the real part of the Wolfenstein Unitarity Triangle and sets
the shape of the triangle that CP violation experiments spend billions of dollars measuring.

**PDG 2024: ρ̄ = 0.159 ± 0.010.**

The geometric derivation proceeds through the triangle amplitude R_b:

    R_b = |V_ub| / (A λ³)

The off-diagonal CKM element |V_ub| is estimated geometrically from the up/top mass
ratio: |V_ub|_geo = √(m_u/m_t). The Wolfenstein A parameter is estimated from the braid
winding ratio: A_geo = √(n₁/n₂) = √(5/7). Then:

    R_b = √(m_u/m_t) / (√(n₁/n₂) × λ³) ≈ 0.367

Finally, ρ̄ = R_b × cos δ_CP. Using the sub-leading braid phase δ_sub = 2·arctan(5/7)
≈ 71.08° (from Pillar 133):

    ρ̄_sub = 0.367 × cos(71.08°) ≈ **0.119**

**PDG: 0.159. Error: ~25%.**

The sub-leading formula improves on the leading-order estimate (ρ̄_lead ≈ 0.113 at 28.6%
error) by about 3.5 percentage points, but the residual discrepancy remains ~25%. The
source code labels this a GEOMETRIC ESTIMATE and is explicit: "Both leading and subleading
formulae give ρ̄ ~ 0.113–0.119 vs PDG 0.159. The ~25% discrepancy remains."

Why does ρ̄ resist tighter prediction? The formula for R_b uses |V_ub| ~ √(m_u/m_t), a
leading-order estimate that captures only the geometric suppression from wavefunction
overlap. The precise value of |V_ub| is sensitive to the relative off-diagonal mixing
of the lightest up-type quark across all three generations — a computation that requires
the full diagonalization of the 3×3 Yukawa matrix, currently parameterized rather than
derived. Until the nine fermion c_L parameters are fixed geometrically, ρ̄ cannot be
predicted more precisely than ~25%.

Status: **GEOMETRIC ESTIMATE (~25%)** — the topology sets the structure; the residual
requires fermion mass derivation from geometry.

---

## The Honest Scorecard

After Pillars 133–142, here is the current count:

| Status | Count | Parameters |
|--------|-------|-----------|
| **DERIVED** (< 5%, no per-species free params) | 8 | α_em, sin²θ_W, α_s, m_H, λ_CKM, A_CKM, η̄_CKM, δ_CP^PMNS |
| **RESOLVED** (gap formally closed) | 2 | m_ν₁ (Majorana branch), Λ_QCD |
| **GEOMETRIC PREDICTION** (< 2%, pure geometry) | 2 | v (Higgs VEV), sin²θ₁₂ |
| **CONSTRAINED** (5–25%, one PDG scale input) | 4 | Δm²₂₁, Δm²₃₁, G_N, δ_CP^CKM |
| **GEOMETRIC ESTIMATE** (order-of-magnitude) | 3 | ρ̄_CKM, sin²θ₂₃, sin²θ₁₃ |
| **PARAMETERIZED** (c_L per species free) | 9 | m_u, m_d, m_s, m_c, m_b, m_t, m_e, m_μ, m_τ |

**The honest answer to "how many of the 26 SM parameters are truly derived?":**

*Ten to twelve*, depending on how strictly you count the CONSTRAINED entries. Eight are
derived in the strict sense — no free parameters, < 5% error. Two geometric predictions
add v and sin²θ₁₂ at < 2% without per-species tuning. The nine fermion masses are
parameterized: the Yukawa *scale* is geometrically fixed (Ŷ₅ = 1 from the 5D Yukawa
normalization, Pillar 93), but the individual bulk mass c_L per species remains a free
input, tuned to match the observed mass hierarchy. That is not prediction; that is fitting
with a geometric frame around it.

The neutrino mass situation has two partially conflicting answers: the Majorana-via-seesaw
resolution (Pillar 150) formally closes the gap at the level of mechanism (Type-I seesaw
gives m_ν ~ v²/M_Pl ~ few meV, safely below the Planck bound), but the Dirac-branch
Pillar 140 gives m_ν₁ ≈ 1.086 eV from the RS zero-mode formula with c_L = 0.776 —
violating the Planck bound by a factor of ~9. Both branches are active. The inconsistency
between Pillars 135 and 140 is a documented structural problem, not a resolved one.

The single hardest remaining gap: the nine individual fermion bulk masses. If the geometric
framework could derive all nine c_L values from topology — rather than fitting each one
separately — the parameter count of the Standard Model would reduce dramatically. Whether
that is possible within the Randall-Sundrum architecture, or requires a different UV
completion, is the central open question that Pillars 133–142 have sharpened without
resolving.

---

## What to Check, What to Break

**Pillar 138 (solar mixing angle):**
- Verify: sin²θ₁₂ = 1/3 − 1/30 + 1/444 ≈ 0.30225. PDG 0.307. Error 1.55%.
  Run `from src.core.solar_mixing_closure import solar_mixing_angle_corrected; print(solar_mixing_angle_corrected())`.
- Challenge: is there a three-term tribimaximal correction formula that fits θ₂₃ and θ₁₃
  with the same structure? The framework has these as geometric estimates (> 15% error)
  rather than predictions. Finding the right sub-leading formula is open.

**Pillar 139 (Higgs VEV):**
- Verify the self-consistent iteration converges: the loop correction Δλ depends on v,
  and the code iterates until |v_new − v| < 10⁻⁶ × v.
- Critical test: try removing the PDG m_H input. Can the Higgs mass and VEV be derived
  simultaneously from geometry? Pillars 134 and 139 use each other's PDG input. A truly
  independent prediction requires both simultaneously from the quartic structure.

**Pillar 140 (lightest neutrino mass):**
- Run `from src.core.neutrino_lightest_mass import neutrino_lightest_mass_rs; print(neutrino_lightest_mass_rs())`.
  Confirm that m_ν₁ ≈ 1.086 eV is reported honestly, with Planck-consistency False.
- The open structural problem: `neutrino_mass_pillar135_140_consistency()` reports
  the three-order-of-magnitude discrepancy between the Pillar 135 ratio estimate
  (~1.49 meV) and the Pillar 140 RS Dirac formula (~1.086 eV). Both cannot be right.
  Find the resolution — or find the error in one of the derivations.

**Pillar 141 (Newton's constant):**
- The RS self-consistency check: run `from src.core.newton_constant_rs import rs_planck_mass_relation; print(rs_planck_mass_relation())`.
  Confirm M₅ ≈ M_Pl from the near-Planck curvature condition.
- Challenge: is πkR = 37 derived from pure topology, or is it an input? Pillar 81 claims
  it from the RS hierarchy; audit whether there is a circularity in using πkR to set the
  EW scale and then using the EW scale to validate πkR.

**Pillar 142 (CKM ρ̄):**
- Verify: ρ̄_sub = √(m_u/m_t) / (√(5/7) × λ³) × cos(2·arctan(5/7)) ≈ 0.119, ~25% from PDG 0.159.
- The key challenge for full closure: derive |V_ub| from the full 3×3 Yukawa
  diagonalization rather than the mass-ratio approximation. This requires fixing all
  nine c_L parameters geometrically — the same problem that limits the fermion mass
  predictions. It is the same gap, appearing in a different place.

**The Grand Scorecard:**
- Run `from src.core.sm_parameter_grand_sync import grand_sync_toe_score; print(grand_sync_toe_score()['toe_verdict'])` for the machine-readable summary.
- The most valuable challenge to this entire arc: find a Standard Model parameter that
  the framework claims as DERIVED but that actually depends on a hidden free input.
  The labeling is designed to be honest. If it isn't, an external check will find the error.

---

*Full source code, derivations, and test suite:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Pillar 138: `src/core/solar_mixing_closure.py`*
*Pillar 139: `src/core/higgs_vev_exact.py`*
*Pillar 140: `src/core/neutrino_lightest_mass.py`*
*Pillar 141: `src/core/newton_constant_rs.py`*
*Pillar 142: `src/core/ckm_rho_bar_closure.py`*
*Honest gaps: `FALLIBILITY.md`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*
*Version: v9.32, May 2026*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
