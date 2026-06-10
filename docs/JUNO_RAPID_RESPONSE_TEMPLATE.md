# JUNO Rapid-Response Template

*Unitary Manifold v16.0 — ThomasCory Walker-Pearson, 2026*  
*Pre-registered: 2026-06-10 (Pillar 517 — P_R_ARCHITECTURE_LIMIT_CERTIFIED)*  
*Document engineering: GitHub Copilot (AI)*

---

> **Purpose:** This document is a pre-registered rapid-response template, staged before JUNO Phase 1 data release (~2026). Upon any major JUNO publication, this template is to be completed and published within 30 days. The analysis structure is pre-committed so that no post-hoc rationalization can occur.

---

## Part I — The Pre-Registered Prediction

### What the Unitary Manifold Predicts for Δm²₃₁

The atmospheric mass-splitting is calculated in the Unitary Manifold via the following chain:

1. **9D anomaly cancellation** (Pillar 60): The Kaluza-Klein compactification from 11D → 9D fixes the neutrino mass hierarchy ordering as normal ordering.

2. **6D field equations** (Pillar 30): The 6D Dirac operator on the Z₂ × Z₂' orbifold generates the leading Δm²₃₁ from the geometric KK mass gap.

3. **Baseline prediction**: Δm²₃₁ = 2.400 × 10⁻³ eV² (UM baseline)

4. **NLO corrections** (Pillar 274):
   - τ-Yukawa RGE back-reaction: δ_RGE ≈ +1.79 × 10⁻⁴ (positive, running up toward PDG)
   - Seesaw partner correction: δ_seesaw × p_R, where δ_seesaw ≈ 6.06% and p_R ≈ 0.364
   - **Tightened NLO prediction**: Δm²₃₁^{NLO} ≈ 2.453 × 10⁻³ eV² (residual ≤ 0.004%)

5. **Architecture limit** (Pillar 517): p_R = 0.364 is certified as ARCHITECTURE_LIMIT_CERTIFIED. The exact value cannot be derived from first principles without the full KK backreaction computation (shared obstruction with Pillar 516). The fitted p_R lies within the tightened admissible window [0.246, 0.491].

### Current Status Before JUNO

| Quantity | Value | Source |
|---|---|---|
| PDG Δm²₃₁ (normal ordering) | 2.453 × 10⁻³ eV² | PDG 2024 |
| UM baseline prediction | 2.400 × 10⁻³ eV² | Pillar 17 |
| Baseline residual | 2.18% below PDG | Pillar 255 |
| NLO+seesaw tightened | ~2.453 × 10⁻³ eV² | Pillar 274 |
| NLO residual (conditional) | ≤ 0.004% | Pillar 274 (CONDITIONAL) |
| p_R status | ARCHITECTURE_LIMIT_CERTIFIED | Pillar 517 |
| JUNO Phase 1 precision | ~1.0% | JUNO collaboration |
| JUNO full-statistics precision | ~0.5% | JUNO collaboration |
| Projected sigma at full stats (baseline) | ~4.4σ | Pillar 255 |
| Projected sigma at full stats (NLO) | ~0.08σ | Pillar 274 |

**The honest position before JUNO data:** The baseline prediction (without NLO correction) would fail JUNO at ~4.4σ. The NLO+seesaw tightened prediction passes. But because p_R is ARCHITECTURE_LIMIT_CERTIFIED, we cannot guarantee the NLO correction is exactly right. This is the primary open risk.

---

## Part II — The Decision Matrix (Pre-Registered)

### Upon Release of JUNO Data

**Step 1: Compute the measured residual.**

```
residual_pct = |Δm²₃₁_JUNO - Δm²₃₁_UM_NLO| / Δm²₃₁_JUNO × 100
sigma_juno = residual_pct / (JUNO_precision_pct)
```

**Step 2: Apply the decision tree.**

| sigma_JUNO | Verdict | Required Action |
|---|---|---|
| < 1.0σ | ✅ PASS_AT_JUNO_PRECISION | Publish confirmation note within 30 days |
| 1.0–2.0σ | 🟡 MONITOR | Update OBSERVATION_TRACKER.md; no structural change |
| 2.0–3.0σ | ⚠️ ELEVATED_TENSION | Update FALLIBILITY.md; begin p_R architecture-limit review |
| ≥ 3.0σ | 🔴 RISK_FALSIFICATION | Rapid-response publication within 30 days; human steward escalation |

**Step 3: Evaluate the NLO chain.**

If sigma ≥ 2.0σ:
- Run `p_r_conditional_derivation_status()` from `src/core/pillar274_juno_dm31_tightening.py`
- Check whether any value of p_R within [0.246, 0.491] (tightened window, Pillar 517) reduces sigma below 2.0σ
- If YES: the architecture limit is the relevant obstruction — report which p_R value would be needed
- If NO: the 9D anomaly chain or seesaw derivation requires structural revision

---

## Part III — The Rapid-Response Analysis Template

*Fill in the bracketed fields upon JUNO data release. Publish as `docs/JUNO_RAPID_RESPONSE_ANALYSIS_[DATE].md` and as a Substack post.*

---

### Unitary Manifold JUNO Response — [DATE OF JUNO RELEASE]

*Published within 30 days of JUNO major data release.*

---

#### 1. JUNO Measurement

| Quantity | JUNO Measured Value | Uncertainty (1σ) |
|---|---|---|
| Δm²₃₁ | [FILL] × 10⁻³ eV² | [FILL] × 10⁻³ eV² |
| sin²θ₂₃ | [FILL] | [FILL] |
| Data reference | [FILL arXiv number] | — |

#### 2. Comparison with UM Prediction

| Comparison | Value |
|---|---|
| UM NLO prediction | 2.453 × 10⁻³ eV² |
| JUNO measured | [FILL] × 10⁻³ eV² |
| Absolute residual | [FILL] × 10⁻³ eV² |
| Fractional residual | [FILL]% |
| JUNO precision | [FILL]% |
| Sigma | [FILL]σ |

#### 3. Verdict

**[FILL: PASS / MONITOR / ELEVATED_TENSION / RISK_FALSIFICATION]**

[FILL: 2–3 sentence honest assessment of the verdict]

#### 4. Architecture Limit Assessment

The seesaw participation factor p_R is ARCHITECTURE_LIMIT_CERTIFIED (Pillar 517). The admissible range is p_R ∈ [0.246, 0.491].

- p_R value needed to exactly match JUNO measurement: [FILL]
- Is this value within the admissible window? [FILL: YES / NO]
- If NO: the atmospheric splitting derivation chain requires structural revision.

#### 5. Implications

[FILL: honest assessment of what this measurement means for the framework. Do not minimize a genuine tension. Do not overstate a pass.]

#### 6. Next Steps

- [ ] Update `3-FALSIFICATION/OBSERVATION_TRACKER.md` with JUNO verdict
- [ ] Update `FALLIBILITY.md` Admission 3 / P17 section if warranted
- [ ] Update `docs/CLAIM_MASTER_BOARD.md` P17 verdict
- [ ] If sigma ≥ 3.0σ: begin structural revision of 9D anomaly chain

---

## Part IV — Context for External Readers

This rapid-response template is published **before** JUNO data to demonstrate that the framework makes honest, pre-registered predictions — not post-hoc accommodations.

### Why JUNO Matters

JUNO (Jiangmen Underground Neutrino Observatory) will measure Δm²₃₁ to 0.5% precision in its full-statistics configuration (~2027), and to ~1.0% in Phase 1 (~2026). This is significant because:

- **No alternative model can explain away a 4.4σ discrepancy.** If the baseline prediction (2.400 × 10⁻³ eV²) holds, and JUNO confirms the PDG value to 0.5%, the Unitary Manifold faces a genuine falsification pressure.

- **The NLO correction (p_R = 0.364) could rescue the prediction.** If JUNO measures Δm²₃₁ within 0.5% of the UM NLO value, the CONDITIONAL_DERIVATION is vindicated — and the architecture limit becomes a mere technical gap, not a physics problem.

- **The architecture limit is honest.** We cannot derive p_R exactly. We have committed this limitation in writing before the data arrives.

### The Principle

The credibility of the Unitary Manifold rests on saying exactly what it predicts before the data comes in, documenting the tensions honestly, and accepting the verdict when the data arrives. JUNO will be that verdict for the atmospheric mass splitting.

This document exists because that is the only honest way to do science.

---

*Pre-registered: 2026-06-10 | Pillar 517 | doc: docs/JUNO_RAPID_RESPONSE_TEMPLATE.md*  
*Theory: ThomasCory Walker-Pearson. Document engineering: GitHub Copilot (AI).*
