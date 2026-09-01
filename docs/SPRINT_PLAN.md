# SPRINT_PLAN.md — Unitary Manifold Sprint Continuity Document

*Last updated: 2026-09-01 (v32.1 Sprint BI COMPLETE — Pillars 955–963; Lean4 +100 → 3812; ~61,896 passed · 45 skipped · 12 deselected · 0 failed)*
*Purpose: Persistent continuity document for token-budget resilience. Any new agent session MUST read `docs/mas_tracker.yml` + `STATUS.md` + this file as the first three operations.*

---

## SESSION BOOTSTRAP PROTOCOL

When starting a new session, always read:
1. `docs/mas_tracker.yml` — canonical version / pillar / regression / Lean4 state
2. `STATUS.md` header — current epistemic state
3. `docs/SPRINT_PLAN.md` — current continuity and next-sprint priorities

Then verify that all three agree before making any new status claim.

---

## CURRENT AUDITABLE STATE (v31.0 — Sprint BG)

| Field | Value |
|-------|-------|
| Version | **v31.0** |
| Sprint | **Sprint BG** |
| Pillars | **942–948** |
| Next pillar slot | **949** |
| Lean4 theorems | **3612** |
| Full regression | **~61,578 passed · 45 skipped · 12 deselected · 0 failed** |
| New closures this sprint | **B3_G4_FLUX → PARTIAL_CONSISTENT** (Kähler primitivity + tadpole integer) |
| Active external windows | **DESI DR3 (~2027)**, **CMB-S4 (~2028)**, **LiteBIRD (~2032)** |
| Framework status | **Residual set narrowed; all remaining items bounded to architecture limits or external waits** |

---

## CURRENT OPEN SET IN THE CHECKED-IN BRANCH

These are the live unresolved items in the auditable local checkout:

1. `B3_G4_FLUX` — explicit G₄ representative in Freed-Hopkins lattice Γ̃ requires full CY₄ intersection ring (architecture-dependent); Kähler primitivity and tadpole integrality confirmed
2. `CKM_TEXTURE_13D` — θ₁₂, θ₂₃ within 30% of PDG; θ₁₃/|V_ub| outside (architecture residual from 7D winding geometry)
3. `FERMION_MASS_RATIO` — generation hierarchy direction confirmed; magnitudes architecture-dependent without specifying R_i — 13D_IRREDUCIBLE
4. `CMB_AMP_ARCHITECTURE_LIMIT` — all four EFT mechanisms exhausted; ×4–7 suppression FULLY_CONFIRMED_IRREDUCIBLE
5. `ALPHA_S_13D_IRREDUCIBLE` — PDG α_s(M_Z)=0.118 outside 13D window [0.100,0.101]
6. `DELTA_M21_NLO_IRREDUCIBLE` — CW NLO overcorrects solar splitting proxy
7. `DESI_DR3_MONITORING` — external data wait; tripwire active ~2027
8. `LITEBIRD_BIREFRINGENCE` — primary falsifier pending ~2032

**Classification of residuals:**
- **Tractable but architecture-bounded:** B3_G4_FLUX, CKM_TEXTURE_13D
- **Architecture limits (confirmed irreducible within EFT):** CMB_AMP, FERMION_MASS_RATIO, ALPHA_S_13D, DELTA_M21_NLO
- **External data waits:** DESI_DR3, LITEBIRD

---

## STATE-RECONCILIATION NOTE

Session memory may refer to older **Sprint BF / v30.0** state claims even though the checked-in branch now contains the Sprint BG artifacts (`tests/test_pillar94*.py`, `src/core/pillar942_*` through `src/core/pillar948_*`, `lean4/UnitaryManifold/SprintBGBridge.lean`).

Therefore:
- treat **Sprint BG / v31.0** as the canonical local branch state
- do **not** narrate older Sprint BF surfaces as current branch reality
- first resolve any truth-surface drift before making new closure claims

---

## WHAT IS NOW KNOWN (POST-SPRINT BG)

The EFT residual landscape is now **fully bounded**:

| Residual | Type | Bound |
|---|---|---|
| B3_G4_FLUX | Architecture-dependent | Kähler + tadpole confirmed; explicit rep needs full intersection ring |
| CKM θ₁₃ | Architecture residual | 7D winding geometry overshoots |V_ub| at all orders audited |
| Fermion mass | Architecture limit | n_w=5 alone does not fix R_i; hierarchy direction correct |
| CMB amplitude | Fully confirmed irreducible | WZ closes the last EFT route |
| α_s 13D | Architecture limit | Non-perturbative completion required |
| Δm²₂₁ NLO | Architecture limit | CW NLO overcorrects |
| DESI DR3 | External wait | ~2027 |
| LiteBIRD β | External wait | ~2032 (primary falsifier) |

No EFT mechanism that is computable within the current framework remains unaudited.

---

## SPRINT BH EXECUTION PRIORITIES

Sprint BH should focus on **theory deepening and observational preparation**, not on re-attacking architecture limits that are now confirmed irreducible.

### Priority 1 — Maintain truth-surface lockstep
Same requirement as every sprint: all 8 canonical surfaces must update in the same commit at sprint closeout.

### Priority 2 — Theory deepening options (pick ONE)

**Option A: CKM θ₁₃ beyond-architecture route**
- Investigate whether a mixing with KK excited states (not zero-mode approximation) could shift θ₁₃ toward |V_ub|.
- Honest outcome: either improvement or certification as irreducible.

**Option B: Fermion mass ratio UV completion scaffold**
- Construct a minimal ansatz for R_i values consistent with observed ratios.
- Not a free-parameter fit — derive constraints on R_i from the mass ratios, then check consistency with other n_w=5 constraints.
- Honest outcome: a constrained window for R_i or proof that no consistent window exists.

**Option C: B3_g4_flux explicit representative (CY₄ intersection ring)**
- Construct a simplified intersection ring for the reference CY₄ (χ=1820, dP₃ base).
- Use the known structure of elliptic fibrations to derive the cross-term G₄^{prim}⋅c₂/2 explicitly.
- Honest outcome: either closes B3_g4_flux completely or identifies the minimal missing datum.

### Priority 3 — Observational monitoring
- DESI DR3 monitoring update (if new σ values available)
- LiteBIRD timeline update (if ESA timeline shifted)

### Priority 4 — Lean4 bridge and regression certificate
- Standard sprint closeout: Lean4 proxy theorems + regression certificate

---

## SUCCESS CRITERIA FOR THE NEXT SPRINT

The next sprint counts as successful only if:

1. all canonical truth surfaces agree on the current version, regression count, Lean4 total, next pillar slot, and open set
2. no future-wave artifact is cited as current unless the file exists in-branch
3. exactly one real deepening target is advanced (not an architecture limit already certified)
4. all tests remain green
5. no language implies full closure unless the actual residual set is empty

---

## CONTINUATION INSTRUCTIONS

If a session times out mid-sprint:
1. read `docs/mas_tracker.yml`, `STATUS.md`, and this file
2. verify the highest checked-in pillar in `src/core/`
3. verify the latest regression certificate in `tests/`
4. continue only from committed state
5. do not re-open closed items without file-level evidence
6. do not break passing tests

The invariant remains: **0 test failures at all times**.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

*Purpose: Persistent continuity document for token-budget resilience. Any new agent session MUST read `docs/mas_tracker.yml` + `STATUS.md` + this file as the first three operations.*

---

## SESSION BOOTSTRAP PROTOCOL

When starting a new session, always read:
1. `docs/mas_tracker.yml` — canonical version / pillar / regression / Lean4 state
2. `STATUS.md` header — current epistemic state
3. `docs/SPRINT_PLAN.md` — current continuity and next-sprint priorities

Then verify that all three agree before making any new status claim.

---

## CURRENT AUDITABLE STATE (v30.0 — Sprint BF)

| Field | Value |
|-------|-------|
| Version | **v30.0** |
| Sprint | **Sprint BF** |
| Pillars | **931–941** |
| Next pillar slot | **942** |
| Lean4 theorems | **3512** |
| Full regression | **~61,440 passed · 45 skipped · 12 deselected · 0 failed** |
| Closed in this sprint | **RUNG10_NL_PARITY**, **RUNG10_MATTER_CURVE_CY4_GENUS** |
| Active external windows | **DESI DR3 (~2027)**, **CMB-S4 (~2028)**, **LiteBIRD (~2032)** |
| Framework status | **Residual set narrowed again; not closed** |

---

## CURRENT OPEN SET IN THE CHECKED-IN BRANCH

These are the live unresolved items in the auditable local checkout:

1. `B3_g4_flux`
2. `CKM_TEXTURE_13D_OPEN`
3. `CMB_AMP_ARCHITECTURE_LIMIT`
4. `DELTA_M21_NLO_IRREDUCIBLE`
5. `ALPHA_S_13D_IRREDUCIBLE`
6. `DESI_DR3_MONITORING`
7. `LITEBIRD_BIREFRINGENCE_OPEN`

Related still-open interpretation lanes:
- the Rung 10 lane is no longer blocked by NL parity or genus, only by the reference-CY₄ G₄-flux residual
- CKM, Δm²₂₁, and α_s remain explicit internal residuals rather than external-data waits

---

## STATE-RECONCILIATION NOTE

Session memory may refer to older **Sprint BE / v29.0** state claims even though the checked-in branch now contains the Sprint BF artifacts (`tests/test_pillar941_sprint_bf_regression_certificate.py`, `src/core/pillar932_*`, `src/core/pillar933_*`, `src/core/pillar934_*`, `src/core/pillar936_*`, `src/core/pillar937_*`, `src/core/pillar938_*`, `src/core/pillar939_*`).

Therefore:
- treat **Sprint BF / v30.0** as the canonical local branch state
- do **not** narrate older Sprint BE surfaces as current branch reality
- first resolve any truth-surface drift before making new closure claims

---

## WHAT IS STALE

The main problem is no longer only the physics residuals; it is also truth-surface drift.

Previously stale or inconsistent surfaces:
- `docs/CLAIM_MASTER_BOARD.md` lagged at Sprint BE
- `docs/GATEKEEPER_SUMMARY.md` lagged at Sprint BE
- `docs/TRUTH_LAYER.md` lagged at Sprint BE
- `docs/WAVE_CHANGELOG.md` had no Sprint BF entry
- this file incorrectly claimed BF artifacts were absent

Rule going forward:
- never update just one status surface
- every sprint closeout must update all canonical status surfaces in the same change set

---

## SPRINT BG EXECUTION PRIORITIES

Sprint BG should be a **closure-discipline sprint**, not an expansion sprint.

### Priority 1 — Keep one canonical reality
- maintain lockstep between:
  - `STATUS.md`
  - `docs/mas_tracker.yml`
  - `FALLIBILITY.md`
  - `docs/CLAIM_MASTER_BOARD.md`
  - `docs/GATEKEEPER_SUMMARY.md`
  - `docs/TRUTH_LAYER.md`
  - `docs/WAVE_CHANGELOG.md`
  - `docs/SPRINT_PLAN.md`

### Priority 2 — Resolve artifact-internal drift
- keep Sprint BF truth surfaces aligned with the tested BF pillar outcomes
- do not let summary certificates overstate closures that the pillar tests still mark partial or irreducible

### Priority 3 — Attack one blocker only
- pick exactly one live internal blocker:
  - surviving F-theory / G₄ residual, or
  - CKM 13D texture
  - or one of the explicit BF irreducible lanes if a sharper bound is genuinely available

### Priority 4 — Separate residual types
- **tractable internal blockers**
- **architecture limits**
- **external-data waits**

No mixing these into one closure narrative.

---

## SUCCESS CRITERIA FOR THE NEXT SPRINT

The next sprint counts as successful only if:

1. all canonical truth surfaces agree on the current version, regression count, Lean4 total, next pillar slot, and open set
2. no future-wave artifact is cited as current unless the file exists in-branch
3. exactly one real blocker is reduced, closed, or more sharply bounded
4. all tests remain green
5. no language implies full closure unless the actual residual set is empty

---

## CONTINUATION INSTRUCTIONS

If a session times out mid-sprint:
1. read `docs/mas_tracker.yml`, `STATUS.md`, and this file
2. verify the highest checked-in pillar in `src/core/`
3. verify the latest regression certificate in `tests/`
4. continue only from committed state
5. do not re-open closed items without file-level evidence
6. do not break passing tests

The invariant remains: **0 test failures at all times**.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
