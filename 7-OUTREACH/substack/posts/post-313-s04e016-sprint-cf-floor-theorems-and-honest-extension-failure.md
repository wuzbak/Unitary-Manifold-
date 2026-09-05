# Sprint CF: Floor Theorems, Honest Extension Failure, and Pre-Registered External Falsifiers

## What changed
- Track A (Pillars 1062–1067): the five Type-B open-lane floors — CMB acoustic amplitude, α_s geometric floor, Higgs mass architecture ceiling, Jarlskog Layer-2 shadow floor, and 5D-EFT QG irreducibility — were upgraded into Lean4-backed lower/upper-bound theorems, aggregated under one Track A floor-theorems certificate (Lean4 delta +60).
- Track B (Pillars 1068–1073): a pre-registered, parameter-free 6D T²/Z₃ + F-theory extension attempt was executed as one honest one-shot. Three lane attempts published exact residuals (Pillar 1068 CW quartic: Δλ_geo achieved 6.5e-4 versus target 0.086; Pillar 1069 F-theory spectral cover m_H; Pillar 1070 6D A_s amplitude mechanism). Pillar 1071 verifies zero new free parameters introduced. Pillar 1072 verifies zero of the 208 hardgate anchors touched. Pillar 1073 publishes the verdict `EXTENSION_TIGHTENED_BUT_NO_CLOSURE_EARNED` — an honest published failure, not a closure claim.
- Track C (Pillars 1074–1076): the two pre-registered external falsifiers were sharpened into rigidity theorems keyed to K_CS=74. LiteBIRD β must lie in [0.22°, 0.38°] and avoid the excluded gap (0.29°, 0.31°) (Pillar 1074) or the braided-winding mechanism is falsified. DESI DR3 |wₐ| ≤ 1/K_CS ≈ 0.0135, strict-symmetry wₐ=0 (Pillar 1075) or the strict-symmetry KK prediction is falsified. Pillar 1076 registers both under `SPRINT_CF_v36.2_TRACK_C_PRE_REGISTERED_2026`; post-hoc softening is explicitly forbidden (Lean4 delta +20).
- Pillar 1077: Sprint CF regression certificate — `sprint_success=True` conditioned on meaningful progress + hardgate untouched + parameter free.

## What did not change
- Zero runtime label flips on any of the 208 hardgate physics pillars.
- Open-lane labels remain explicit and unchanged: `CMB_AMP_CONFIRMED_IRREDUCIBLE`, `ALPHA_S_TYPE_B_FLOOR`, `HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW`, `CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED`, `FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED`, `JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED`, `DESI_DR3_MONITORING`, `LITEBIRD_BIREFRINGENCE`, `NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT`.
- No hardgate physics claim labels were promoted. Track B did not softly claim closure of any Type-B floor.

## Falsification implications
- LiteBIRD β falsifier is sharper (Pillar 1074): a value outside [0.22°, 0.38°], or landing in the excluded gap (0.29°, 0.31°), falsifies the braided-winding mechanism.
- DESI DR3 wₐ falsifier is sharper (Pillar 1075): |wₐ| > 1/K_CS ≈ 0.0135 at ≥ 5σ, or exclusion of wₐ = 0 at ≥ 5σ, falsifies the strict-symmetry KK prediction.
- Sharpness is entirely topological — K_CS = 74 is the only input, no adjustable parameter.
- DESI, CMB-S4, and LiteBIRD windows remain active with the same boundary conditions.

## Residual unknowns
- CMB amplitude architecture floor remains open (Track B 6D CW quartic residual explicit; 6D A_s mechanism residual explicit).
- α_s Type-B geometric floor and Higgs architecture ceiling remain open (Track B F-theory spectral cover residual explicit).
- CKM shadow, fermion magnitude/radii, and Jarlskog Layer-2 architecture limits remain open.
- Non-perturbative QG residual lane remains open (Pillar 1066 negative irreducibility theorem within 5D EFT domain only).

## Sprint CF totals
- 16 pillars (1062–1077); Lean4 total → 4080 (+80); next slot 1078.
- Regression: 63,787 passed · 23 skipped · 12 deselected · 0 failed. Focused Sprint CF suite: 74 passed · 0 failed.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
