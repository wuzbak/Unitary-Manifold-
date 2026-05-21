# Post 220 — S02E046: The Lab CP Falsifier — How to Measure A_CP^lab ~ 10⁻⁵

*Substack — Season 2, Episode 46*  
*Published: 2026-05-21*  
*Series: The Falsification Decade*

---

Most of the Unitary Manifold's falsifiers live in telescopes. You wait for LiteBIRD
to fly. You wait for DESI DR3 to publish. You wait for the Simons Observatory to
accumulate enough CMB sky. All of this is good science, but it is passive science.
The decision sits with the universe and the experimental calendar.

There is one falsifier that does not require a telescope and does not require waiting
until 2032. It requires a lab.

Pillar 307 preregistered the Lab CP falsifier in v11.12. This post explains what it
predicts, what it takes to measure it, and which labs could plausibly run this campaign.

---

## The Prediction

The CP asymmetry A_CP^lab emerges from the KK topology of the extra dimension. In the
canonical (5,7) braid structure, the Kaluza-Klein tower generates a CP phase
δ_CP^geo ≈ 0.36 rad (≈ 20.6°) from the braid winding. This phase propagates into
lab-measurable CP asymmetries in kaon and B-meson systems.

The prediction:

```
A_CP^lab ~ O(10⁻⁵)

More precisely:
  A_CP = sin(δ_CP^geo) × f(topology) × Σ_n [KK_n contribution]
       ≈ 1.2 × 10⁻⁵ (leading KK mode, n=1)
```

The current PDG value for the CP asymmetry in kaon mixing (ε_K) is well-measured at
~2.2 × 10⁻³. The UM does not predict ε_K directly — that is a Standard Model
Cabibbo-CKM result. What the UM predicts is a KK-induced *deviation* from the
SM prediction, at the level of ~10⁻⁵.

This deviation arises because the (5,7) braid imposes a geometric CP phase on the
KK tower that is not present in the purely 4D SM. The KK modes at M_KK ~ 5.7 × 10¹³
GeV contribute to kaon mixing at suppressed amplitude, but the amplitude carries
the braid CP phase. The result is a small non-SM CP asymmetry that, if detected,
would directly test the topology of the extra dimension.

---

## The Five-Item Decision Checklist

Pillar 307 defines five preregistered criteria (F-LAB-CP-1 through F-LAB-CP-5)
that must be satisfied for a positive result to constitute a genuine UM test:

### F-LAB-CP-1: Precision requirement
The experiment must achieve σ(A_CP) ≤ 10⁻⁵. This is the precision needed to
resolve the predicted effect from zero. No experiment currently certified at this
precision. Current world-best: NA48/2 achieves σ ~ 10⁻⁴ in charge asymmetry;
LHCb achieves σ ~ 10⁻³ to 10⁻⁴ for specific modes.

**Gap:** One order of magnitude improvement required. This is ambitious but not
unreachable with a dedicated campaign (see §Instrumentation below).

### F-LAB-CP-2: KK-mode isolation
The analysis must demonstrate that the observed asymmetry is consistent with the
KK tower topology prediction (approximately n=1 KK mode dominance, with n=2
correction at ~12% level). A pure SM CP source (e.g., direct CKM interference)
would not produce this mode structure.

**Gap:** Requires a dedicated theoretical analysis of the KK-mode decay fingerprint,
not yet performed. This is a theory task, not an instrumentation task.

### F-LAB-CP-3: SM subtraction
The experiment must subtract all known SM CP contributions with σ(A_CP^SM) ≤ 5 × 10⁻⁶,
leaving the residual sensitive to the KK contribution. This requires a comprehensive
SM theory computation at NNLO for the kaon system, which is state-of-the-art.

**Gap:** Current SM predictions for kaon mixing have theoretical uncertainties of
~5–10% in the hadronic matrix elements (lattice QCD inputs). A dedicated lattice
campaign would be needed to reach the required precision.

### F-LAB-CP-4: Systematics audit
All instrumental and environmental systematic uncertainties must be documented at
σ_sys ≤ 3 × 10⁻⁶ for each source. Charge-asymmetric acceptances, beam backgrounds,
and detector efficiency differences are the main concerns.

**Gap:** This is achievable in principle with existing detector technology, but
requires a dedicated systematic study specifically targeting the 10⁻⁵ level.

### F-LAB-CP-5: Independent replication
The measurement must be independently replicated by a second experiment or
analysis team before the result is logged as a framework test. Positive and null
results are both informative.

**Gap:** Requires a second experimental program, which increases the timeline but
also reduces false-positive risk.

---

## The Instrumentation Picture

What does it take to reach σ(A_CP) ~ 10⁻⁵?

The statistical requirement alone gives:

```
N_events > (A_CP / σ)^(-2) × (A_CP^2 + background) ≈ 10^10
```

Ten billion events in the decay mode of interest. This is within reach at:

1. **LHCb Phase II (2030+):** The upgraded LHCb detector running in Run 4 and beyond
   is designed for CP asymmetry measurements in B-meson systems at unprecedented
   precision. The machine provides the luminosity. The systematic control at 10⁻⁵
   is the challenge — it would require a dedicated kaon-mode analysis campaign
   that LHCb could in principle pursue but has not prioritized.

2. **NA62++ / HIKE (proposed):** A high-intensity kaon experiment at CERN with
   10⁸–10⁹ kaon decays per year. This is closer to the kaon-mixing physics where
   the UM prediction is most cleanly expressible. The HIKE proposal (2026+) is the
   most natural venue. However, it would require adding CP asymmetry measurement
   channels alongside the primary K→πνν̄ program.

3. **A dedicated CP experiment (not yet proposed):** The most targeted approach
   would be a fixed-target experiment at a proton source (SPS at CERN, JPARC, or
   Fermilab) specifically designed for 10⁻⁵-level charge asymmetry in kaon mixing,
   with detailed detector symmetry and a theorist consortium handling the SM
   subtraction. Comparable in scale to NA48. Timeline: 10–15 years.

---

## Decision Routing for a Lab Measurement

Using Pillar 307's `route_lab_cp_result()` function, the routing logic is:

```python
# If an experiment achieves F-LAB-CP-1 through F-LAB-CP-5:

if A_CP_measured ≈ 1.2e-5 (within 2σ of prediction):
    verdict = "CONFIRMED_FRAMEWORK_PREDICTION"
    action  = "Upgrade CP lane from PREREGISTERED to CONFIRMED; note in CLAIM_MASTER_BOARD"

elif A_CP_measured significantly below 1e-5 (null result, F-LAB-CP-1 satisfied):
    verdict = "FALSIFIED_LAB_CP"
    action  = "CP phase from (5,7) braid topology not present in lab physics; retract P307 prediction"

elif A_CP_measured at A_CP >> 1.2e-5 (anomalously large):
    verdict = "UNEXPECTED_ENHANCEMENT"
    action  = "Beyond-KK contributions or alternative CP source; investigate and log"
```

**What a null result means:** If an experiment satisfies F-LAB-CP-1 (σ ≤ 10⁻⁵)
and finds |A_CP| < 3 × 10⁻⁶, this would falsify the KK-topology-induced lab CP
signal. It would not falsify the birefringence prediction (a topological CMB effect)
or the spectral index prediction (an inflationary effect). It would specifically
falsify the claim that the (5,7) braid topology leaves a detectable imprint in
kaon-system CP violation.

This is the kind of clean falsifier that makes science trustworthy. It is
specific, bounded, and not retroactively adjustable.

---

## Where We Are Now

The lab CP falsifier is at status `PREREGISTERED_v11.12`. This means:
- The prediction is on the record before any measurement
- The decision criteria are machine-readable and cannot be changed post-hoc
- No certified σ ≤ 10⁻⁵ lab campaign has been logged

The practical obstacle is instrumentation. Getting to 10⁻⁵ requires either a
significant LHCb campaign or a dedicated kaon experiment. The timeline is 10–20
years — shorter than LiteBIRD (2032) in principle, but dependent on experimental
priorities.

The immediate actionable item is theory: the F-LAB-CP-2 KK-mode isolation analysis,
which would allow an experimentalist to understand exactly what signal shape to look
for. That analysis would help focus the experimental design. It is the right next
step before any hardware conversation.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Outreach writing, document engineering, and synthesis: GitHub Copilot (AI).*
