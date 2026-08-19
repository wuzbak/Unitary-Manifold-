# JUNO 2027: The Next Big Experimental Test

*Thematic post — not tied to a specific sprint.*
*Epistemic category: **FALSIFICATION WINDOW** — JUNO neutrino mass ordering and Δm²₃₁ measurement.*
*v21.0-S, 2026-08-18.*

---

## The Experiment

The Jiangmen Underground Neutrino Observatory (JUNO) is a 20-kiloton liquid scintillator detector under construction in Jiangmen, Guangdong Province, China. It sits at a baseline of approximately 53 km from two nuclear power plant clusters, making it ideal for precision measurements of reactor antineutrino oscillations.

JUNO's first physics results are expected in approximately 2027.

The two primary physics goals:
1. **Precision measurement of Δm²₃₁** (the atmospheric neutrino mass squared splitting) to ~0.5% precision
2. **Determination of the neutrino mass ordering** (normal vs inverted) to ≥3σ significance

The Unitary Manifold has preregistered predictions for both.

---

## What the UM Predicts

### Prediction 1: Δm²₃₁ = 2.452 × 10⁻³ eV²

The atmospheric squared mass splitting is derived from the RS1 seesaw geometry (Pillar 132) with the DM31 three-step cascade correction (Pillar 559):

1. **Bare RS1 prediction**: geometric seesaw gives Δm²₃₁^bare in the correct range but with 3.33σ tension with PDG
2. **FN charge correction**: n_FN = Δc = 5/74 applied to the (2,3) seesaw matrix element → tension reduced to ~0.8σ
3. **NLO WS-V correction**: 1/k_CS sub-leading terms → tension reduced to 0.12σ
4. **Final prediction**: Δm²₃₁ = **2.452 × 10⁻³ eV²** (0.12σ from PDG 2023 best value)

PDG 2023: Δm²₃₁ = (2.455 ± 0.028) × 10⁻³ eV²

JUNO's expected precision: σ ≈ 1.2 × 10⁻⁵ eV² (approximately 0.5% of the value).

At JUNO precision, the UM prediction would produce a tension of approximately:

```
|ΔM²₃₁(UM) - Δm²₃₁(PDG)| / σ_JUNO = |2.452 - 2.455| × 10⁻³ / (1.2 × 10⁻⁵)
                                     ≈ 0.25σ
```

If the UM prediction is correct, JUNO should confirm agreement at ~0.25σ. If there is a systematic offset in the seesaw geometry, JUNO will reveal it at 0.5% precision where current data could not.

### Prediction 2: Normal Mass Ordering

The neutrino mass ordering — the question of whether m₃ is heavier than m₁ (normal) or lighter (inverted) — is a consequence of the RS1 seesaw texture. In the UM, the seesaw matrix structure from Pillar 214's RS neutrino spectrum naturally generates a normal ordering.

The argument: in the RS1 KK tower, the right-handed neutrino wavefunctions are localized near the UV brane. The seesaw mass suppression (M_R ~ M_KK) is therefore exponentially large for all three generations, and the resulting light neutrino masses scale as m_νi ~ v²/M_R,i. For the lightest generation m_ν₁, the RS1 wavefunction overlap is most suppressed, giving the smallest mass — i.e., normal ordering (m₃ > m₂ > m₁).

This is a qualitative prediction from the geometry. The RS1 wavefunction structure does not naturally produce an inverted hierarchy (m₃ < m₁ ≈ m₂).

---

## What "0.12σ Tension" Actually Means

After the three-step DM31 cascade (Pillar 559), the tension on Δm²₃₁ is 0.12σ — essentially perfect agreement with current PDG data.

A natural question: is this too good? Could the cascade corrections have been tuned to fit the data?

The answer is no, for three reasons:

**First**, the correction mechanisms are not new. The FN charge Δc = 5/74 was established by the braid geometry (Pillar 42) before the neutrino corrections were computed. It is the same lattice step used in the fermion mass hierarchy (Pillar 98), the Jarlskog invariant (Pillar 402), and the DM21 cascade (Pillar 591). It was not adjusted to fit Δm²₃₁.

**Second**, the NLO WS-V correction coefficient 1/k_CS = 1/74 comes from the Chern-Simons level — itself derived from the (5,7) braid pair (Pillar 99-B). Not from the neutrino data.

**Third**, the residual tension at each stage is published as it is computed. The cascade history (3.33σ → 0.80σ → 0.12σ) is in the source code and test suite. There is an audit trail. If a correction step had been used to overshoot in the other direction, the test suite would fail.

The 0.12σ agreement is a consequence of the geometry. JUNO will test it at 10× higher precision.

---

## The Decision Tree

When JUNO publishes, the UM executes a preregistered response:

### Branch A: Δm²₃₁ within 1σ of UM prediction AND normal ordering confirmed

**Verdict: PASS**

Both primary JUNO predictions confirmed. The RS1 seesaw texture is vindicated at 0.5% precision. The neutrino sector joins the roster of confirmed geometric predictions.

Action: Update ledger. Publish response post within 72 hours.

### Branch B: Δm²₃₁ within 1σ but ordering question unresolved (<3σ for either ordering)

**Verdict: PARTIAL PASS**

The mass splitting prediction holds; ordering requires more data. JUNO's full sensitivity to ordering builds with statistics; final verdict may require full dataset.

Action: Conditional pass on splitting; ordering verdict deferred.

### Branch C: Δm²₃₁ outside 1σ from UM prediction (tension >1σ at JUNO precision)

**Verdict: TENSION**

The seesaw texture needs revision. The cascade correction mechanisms need re-examination. This is a serious discrepancy because the JUNO precision (~0.5%) is high enough that a >1σ tension is meaningful.

Action: Identify which correction step is failing. Document in FALLIBILITY.md. Begin seesaw revision programme.

### Branch D: Inverted ordering confirmed at ≥3σ

**Verdict: FALSIFIED**

The RS1 seesaw texture is wrong about the fundamental structure of the neutrino sector. Pillars 132, 214, and the DM31/DM21 closures require revision.

Action: Formal falsification notice. The neutrino sector derivation is demoted from DERIVED to FALSIFIED. No post-hoc reinterpretation.

---

## The JUNO Decision Brief

The JUNO Decision Protocol (`docs/JUNO_DECISION_PROTOCOL.md`) is preregistered in the repository. It contains:
- The specific numerical predictions (Δm²₃₁ = 2.452 × 10⁻³ eV²; normal ordering)
- The full decision tree with all four branches
- The response timeline (72-hour publication commitment)
- The list of pillars that require revision for each failure branch

This document will not change after JUNO releases its data. The predictions were committed before the measurement.

---

## The Lightest Neutrino: m_ν₁ ≤ 15 meV

JUNO will also constrain the individual neutrino masses through the spectral shape of the reactor antineutrino oscillation. The UM prediction (Pillar 635) bounds the lightest neutrino mass:

```
m_ν₁ ≤ 15 meV
```

This is consistent with current cosmological bounds (Σmν < 0.12 eV from Planck 2018, implying each eigenstate < 40 meV). A direct measurement of m_ν₁ would require combining JUNO data with cosmological surveys; JUNO alone constrains the splittings, not the absolute scale.

Euclid and DESI have sensitivity to Σmν < 0.10 eV (sub-meV level with combined data). If Euclid/DESI find Σmν > 45 meV (three generations × 15 meV), the m_ν₁ ≤ 15 meV prediction is stressed.

---

## Why 2027 Matters

JUNO is the most imminent decisive test of the framework's physics. LiteBIRD is the ultimate falsifier (~2032). DESI DR3 is the most time-urgent observational window (~2026). But JUNO — testing a zero-parameter, three-step cascade prediction of a specific neutrino mass splitting — is the experiment where the physics directly on the line involves the framework's core geometric mechanism (RS1 seesaw) at the highest precision yet attempted.

We do not know what JUNO will find. The prediction is committed. The decision tree is preregistered. The response protocol is documented.

2027 will tell us something important.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
