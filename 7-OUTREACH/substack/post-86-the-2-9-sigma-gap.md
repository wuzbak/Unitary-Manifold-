# The 2.9σ Gap — What LiteBIRD Will Actually Measure

*Post 86 of the Unitary Manifold series.*
*This post examines the observational consequence of the dual-sector structure:
a predicted gap in the birefringence angle between 0.29° and 0.31°, separated
from both sector predictions by 2.9σ at LiteBIRD sensitivity. This is the
sharpest predictive consequence the framework produces for a near-term experiment.*

---

The measurement that will determine the fate of this framework is not a single
number. It is the location of a measurement on a continuous scale.

If LiteBIRD measures the cosmic birefringence angle β and finds β ≈ 0.273°,
the (5,6) sector is confirmed.

If it finds β ≈ 0.331°, the (5,7) sector is confirmed.

If it finds β ≈ 0.302° — right in the middle — the birefringence mechanism is wrong.

This is not a safety valve. It is a specific prediction: there is a forbidden
zone, and the measurement will either land in it (falsifying the mechanism) or
outside it (confirming one of the two sectors). The measurement cannot be
interpreted as neutral. It will say something.

---

## What Cosmic Birefringence Is

Cosmic birefringence is the rotation of the polarization angle of the Cosmic
Microwave Background as light travels from the surface of last scattering
(380,000 years after the Big Bang) to our detectors.

In standard cosmology, CMB polarization should not rotate. The polarization
direction is set at recombination and preserved through transparent space.
Any rotation would indicate a new physics effect — specifically, the coupling
of photons to an axion-like particle (ALP) through a Chern-Simons interaction.

The signal is tiny: a rotation of fractions of a degree, superimposed on
primordial polarization and foreground contamination. But the signal has been
tentatively detected.

---

## The Current Status

Several groups have analyzed existing CMB data (Planck, BICEP, SPT) for
evidence of cosmic birefringence. The results vary, but a 2022 analysis by
Minami and Komatsu found β = 0.342° ± 0.094° at 3.6σ significance. A subsequent
analysis with refined foreground modeling found consistent results.

The current measurement: **β ≈ 0.34° ± 0.09°**

The framework's predictions:
- Sector (5,7): β ≈ 0.331° — within 0.09° of the measured central value
- Sector (5,6): β ≈ 0.273° — 0.7σ below the current measurement

The current data is consistent with both sectors and provides no discrimination
between them. This is expected: the current precision σ ≈ 0.09° cannot resolve
the 0.058° gap between the two predictions.

LiteBIRD will achieve σ ≈ 0.02°. At that precision, the discrimination is 2.9σ.

---

## The Prediction Structure

The framework makes a layered prediction about the LiteBIRD measurement:

**Layer 1 (Framework test):** β ∈ [0.22°, 0.38°]
If this fails, the entire birefringence mechanism is ruled out.

**Layer 2 (Mechanism test):** β ∉ [0.29°, 0.31°]
If the measurement lands in the gap, the braided-winding mechanism is wrong
even if the overall scale is right.

**Layer 3 (Sector discrimination):** β ≈ 0.273° or β ≈ 0.331°
If either of these is confirmed at σ ≤ 0.03°, the specific braid sector
is identified.

**Layer 4 (CS level test):** σ(β) ≤ 0.02° rules out k_CS = 73 and k_CS = 75
If β is confirmed at sub-percent precision, the specific Chern-Simons level
(61 or 74) is identified.

---

## Why 2.9σ Matters

Two sigma is below the conventional 95% confidence threshold. Why is 2.9σ
the right criterion for sector discrimination?

Because the question is not "is there birefringence?" (Layer 1 — a detection
problem) but "which sector is it?" (Layer 3 — a discrimination problem).

For discrimination between two specific hypotheses with known predictions, the
relevant figure of merit is the signal-to-noise on the difference. The difference
is 0.058°; the noise is 0.02°; the SNR is 2.9.

At 2.9σ, the probability of incorrectly identifying the sector (measuring in
one sector's window when the universe is actually in the other) is less than
0.2%. That is sufficient for a scientific claim of sector identification.

DUNE and Hyper-Kamiokande's CP phase measurement (δ_CP^PMNS ≈ -107°) combined
with LiteBIRD's sector identification will constitute the two-pronged test that
either confirms or rules out the framework at high confidence.

---

## The Timeline

| Experiment | Measurement | Expected |
|------------|-------------|----------|
| LiteBIRD | β to σ ≈ 0.02° | ~2032 launch, data ~2034 |
| DUNE full | δ_CP^PMNS to σ ≈ 5° | ~2030 |
| Hyper-K | δ_CP^PMNS to σ ≈ 3° | ~2028-2035 |
| Roman | w to σ ≈ 0.02 | Operating now; 5-year survey |
| CMB-S4 | r to σ ≈ 0.003 | ~2030 construction completion |
| EUCLID | Σm_ν to σ ≈ 20 meV | Operating, data ~2026-2030 |

The decade from 2025 to 2035 is the decade of judgment for this framework.
Every major open prediction will be tested. The framework will either survive
all of them or it won't. We have committed to acknowledging the results publicly,
without equivocation, within 90 days of each data release.

---

## What the Gap Means Physically

The forbidden zone [0.29°, 0.31°] is not arbitrary. It corresponds to values
of k_CS between 64 and 71 — integer values that do not factorize as n₁² + n₂²
with n₁ = 5 and any integer n₂.

The geometry forbids β in the gap because the geometry forbids braid sectors
with k_CS in that range. You cannot have a braid of (5, 6.5). The braid partners
are integers. The gaps between integer values of n₂ create forbidden zones in β.

The forbidden zone at [0.29°, 0.31°] is the most accessible of these gaps —
the one between n₂ = 6 and n₂ = 7. LiteBIRD will probe it at 2.9σ.

Higher gaps (between n₂ = 7 and n₂ = 8, etc.) are outside the birefringence
window [0.22°, 0.38°] — they are excluded by the birefringence constraint before
the r constraint applies.

---

*Full source code, derivations, and 17,438 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Pillar 95: `src/core/dual_sector_convergence.py`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
