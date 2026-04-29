# The Full Falsification Map: What We Are Waiting For

*Post 32 of the Unitary Manifold series.*
*This post maps every active falsification condition in the Unitary Manifold
framework against the experiments and observations that will resolve them,
ordered by tier and timeline. No new physics is introduced. This is the ledger:
here is what the framework predicts, here is what would break it, here is when
we will know. The series has now covered all 74 pillars. What remains is to wait,
watch, and update.*

---

Post 3 of this series introduced one date: 2032. That is when LiteBIRD launches
and the framework's primary falsification test occurs.

Post 5 introduced the honesty principle: every open problem would be stated
plainly. The series has spent 31 posts trying to live up to that.

This final post is the accounting. Not a conclusion — the theory is not
concluded; it is open. But a complete map: everything the framework predicts,
everything that would falsify it, every experiment watching for it.

---

## Tier 1: Core physics predictions — these are precise and testable

These are predictions that follow directly from the 5D geometry with no domain
analogy involved. They are the theory's hardest commitments.

### 1.1 — Cosmic birefringence β (Primary falsifier)

**Prediction:** β ∈ {≈0.273°, ≈0.331°} (canonical) or {≈0.290°, ≈0.351°} (derived)
The admissible window is [0.22°, 0.38°]. The predicted gap is [0.29°–0.31°].

**Current status:** Minami & Komatsu (2020) and Diego-Palazuelos et al. (2023)
measure β ≈ 0.34° ± 0.12°. Consistent with the prediction. Not yet precise
enough to test the sub-structure.

**Falsification:** β outside [0.22°, 0.38°], OR β measured within the predicted
gap [0.29°–0.31°]. Either falsifies the braided winding mechanism.

**Resolution:** LiteBIRD satellite. Launch ~2032. Precision: ±0.01°. This
measurement has a definite date and a definite answer.

---

### 1.2 — CMB spectral index n_s and tensor-to-scalar ratio r

**Prediction:** n_s = 0.9635, r = 0.0315 (derived from (5,7) braid, C_S = 12/37)

**Current status:**
- Planck 2018: n_s = 0.9649 ± 0.0042. Framework: 0.33σ from central value. ✅
- BICEP/Keck 2021: r < 0.036 at 95% CL. Framework: r = 0.0315 is below the
  upper bound. ✅

**Falsification:** n_s measured more than 5σ from 0.9635, or r > 0.036 with
statistical confidence, or r measured and found inconsistent with 0.0315.

**Resolution:** CMB-S4, Simons Observatory, LiteBIRD polarisation sensitivity.
The r prediction (r = 0.0315) is within reach of next-generation B-mode surveys.
A measurement of r at any value inconsistent with 0.0315 at >3σ would be
challenging for the framework.

---

### 1.3 — Dark energy equation of state w_KK

**Prediction:** w_KK = −1 + (2/3) C_S² ≈ −0.930, w_a = 0 (no time evolution
at first order)

**Current status:** DESI 2024 early data reports mild tension with w = −1 at
~2–3σ, with best-fit w ≈ −0.9. This is consistent with the prediction w_KK ≈ −0.930
but is not a confirmation — the error bars are too large.

**Falsification:** w measured at better than 5σ tension with −0.930, or w_a
significantly different from zero at high confidence.

**Resolution:** Nancy Grace Roman Space Telescope (launch ~2027). The Roman weak
lensing survey (Pillar 66) forecasts σ(w) ≈ 0.02, which would test w = −0.930
against w = −1.0 at roughly 3.5σ. A Roman measurement of w = −1.00 ± 0.02 would
significantly challenge the framework's dark energy prediction.

---

### 1.4 — KK-modified S₈ tension

**Prediction:** the KK radion sector modifies the growth of structure, predicting
S₈ ≈ 0.80 (slightly below the Planck value of 0.83, consistent with the S₈
tension seen in weak lensing surveys).

**Current status:** Multiple weak lensing surveys (KiDS, DES, HSC) find
S₈ ≈ 0.76–0.80. The framework's prediction of S₈ ≈ 0.80 is within the
observational range but not uniquely testable at current precision.

**Falsification:** S₈ measured above 0.83 consistently across multiple surveys,
restoring agreement with Planck and removing the tension the framework predicts.

**Resolution:** Roman Space Telescope, Euclid, LSST Rubin Observatory. All
survey programmes with projected precision σ(S₈) < 0.01.

---

### 1.5 — Winding number uniqueness (APS conjecture)

**Prediction:** n_w = 5 is mathematically required by the APS η-invariant
condition on the orbifold S¹/Z₂. η̄(5) = 0.5 (chirality-compatible);
η̄(7) = 0 (chirality-incompatible).

**Current status:** The conjecture is not proved. Pillar 70 documents it as
a mathematical open problem. Pillar 70-B (`src/core/aps_spin_structure.py`)
implements the Hurwitz ζ function representation but uses the physical chirality
argument for the specific values.

**Falsification:** A direct analytical computation of η̄(n_w) for n_w ∈ {5, 7}
from APS boundary data that gives a result inconsistent with η̄(5) = 0.5.

**Resolution:** Mathematical. Not experimental. Requires a spectral geometer to
complete the APS computation for the relevant orbifold. This is the one open
problem in the framework that no satellite or accelerator can close.

---

## Tier 2: Extended predictions — derived from the physics core with additional assumptions

### 2.1 — KK radion contribution to photon-epoch observables

**Prediction:** The radion sector contributes Δρ/ρ ≈ 1.42 × 10⁻³ to radiation
domination, modifying the Hubble rate by ΔH/H ≈ 7 × 10⁻⁴.

**Falsification:** Any precision measurement of N_eff (the effective number of
relativistic species at recombination) that is inconsistent with the standard
value plus 1.42 × 10⁻³ extra radiation.

**Resolution:** CMB-S4 will measure N_eff to ±0.02. The KK radion correction
to N_eff is approximately 0.004. This is below CMB-S4's precision — the correction
will not be detectable.

---

### 2.2 — Fröhlich polaron KK correction in polar semiconductors

**Prediction:** The phonon frequency in polar semiconductors (GaAs, GaN, InP)
is corrected by a factor 1 + C_S²/k_CS ≈ 1 + 1.4 × 10⁻³.

**Falsification:** High-precision optical spectroscopy of LO phonon frequencies
in GaAs showing no correction at this level (precision would need to be < 10⁻³).

**Resolution:** Fourier-transform infrared spectroscopy or Raman spectroscopy
at millikelvin temperatures with frequency stability <0.01%. Currently borderline
accessible with state-of-the-art equipment.

---

### 2.3 — CMB power spectrum amplitude (open problem)

**Status:** The framework does not correctly reproduce the CMB power spectrum
amplitude at acoustic peaks. The predicted amplitude is suppressed by 4–7×
relative to the Planck observation. Pillars 57 and 63 attempt to address this
via back-reaction corrections; the gap persists.

**What would fix it:** A mechanism for normalising the primordial power spectrum
amplitude A_s from first principles within the braided winding framework. Currently
A_s is a free parameter.

**What would close it as unfixable:** If a future derivation shows that the
braided winding mechanism is fundamentally incompatible with the observed A_s
for any value of the compactification radius r_c. This would require restructuring
the inflationary sector.

---

### 2.4 — Three-generation derivation (conditional on APS)

**Status:** The derivation that n_w = 5 gives exactly three stable KK generations
is algebraically correct. It is conditional on: (a) n_w = 5 being correct, and
(b) the Z₂ orbifold stability argument being rigorous. Part (b) is connected to
the APS conjecture.

**Falsification:** Discovery of a fourth generation of quarks or leptons at collider
experiments. This would contradict the prediction ⌊n_w/2⌋ + 1 = 3.

**Resolution:** The LEP constraint on the number of light neutrino species is
already 3 at >5σ. A fourth generation with a heavy neutrino is still possible but
severely constrained. Future collider experiments (FCC-ee, CEPC) will push the
constraint further.

---

## Tier 3: Domain applications — formal language claims

These are not falsification conditions in the same sense as Tier 1 and 2. They
are claims that the φ-field language is *consistent* with domain-expert findings,
not that it makes novel predictions those experts cannot make themselves.

The falsification condition for all Tier 3 claims is the same: **if domain
experts find that the φ-field model makes predictions inconsistent with
established findings in their domain, the claim fails.**

| Domain | Module | Primary domain connection |
|--------|--------|--------------------------|
| Medicine | `src/medicine/` | Fixed-point displacement = disease |
| Justice | `src/justice/` | Recidivism as wrong-attractor trapping |
| Ecology | `src/ecology/` | Collapse as bifurcation |
| Governance | `src/governance/` | Democracy as distributed fixed-point stability |
| Neuroscience | `src/neuroscience/` | Grid-cell spacing ratio 7/5 |
| Climate | `src/climate/` | Tipping points as bifurcations |
| Psychology | `src/psychology/` | Habit strength, RPE, polarisation |
| Genetics | `src/genetics/` | Hardy-Weinberg as φ fixed point |
| Materials | `src/materials/` | Polaron KK correction (Tier 2 element) |
| Astronomy | `src/astronomy/` | Stars as FTUM fixed points |
| Dark matter | `src/core/dark_matter_geometry.py` | B_μ isothermal profile (Tier 1 element) |

---

## The experiments to watch

**2026–2027:**
- BICEP3 / Keck Array full analysis: tighter r constraint approaching 0.01
- DESI Year 3 results: better w and w_a measurement
- LHC Run 3 final datasets: muon g−2 theory updates

**2027:**
- Roman Space Telescope first light (if schedule holds): begins w, S₈ programme

**2028–2030:**
- Euclid weak lensing: first competitive w_KK test
- LSST Rubin first year: S₈ from photometric lensing
- CMB-S4 early data: N_eff, r, n_s improvements

**2031:**
- LiteBIRD integration and testing phase complete

**2032:**
- **LiteBIRD launch.** The primary falsification test.
- Expected result: β measured to ±0.01° precision.
- If β ∈ [0.22°, 0.38°] and outside the gap [0.29°–0.31°]: consistent, strong
  support for the braided winding mechanism.
- If β outside [0.22°, 0.38°]: the primary prediction is falsified. The framework
  would require restructuring of its birefringence sector.
- If β within the gap [0.29°–0.31°]: the prediction is falsified for the canonical
  mode structure. This would be the most interesting result — the theory predicts
  a gap, and finding a measurement in the gap would be a specific failure of the
  braided winding model.

**Mathematical (no fixed date):**
- APS η-invariant proof or disproof for the S¹/Z₂ orbifold with Chern-Simons inflow.
  This is the one falsification condition that no telescope can resolve.

---

## What the 14,183 tests are for

The automated test suite — 14,183 tests covering 74 pillars and the Unitary Pentad
governance framework — is not evidence that the physics is correct. It is a
structural guarantee: if any of the internal relationships the framework asserts
were broken by a code change, a test would fail. The suite ensures that the theory
is internally consistent as implemented.

Internal consistency is a necessary condition for a theory to be taken seriously.
It is not sufficient. The sufficient condition is what LiteBIRD, Roman, CMB-S4,
and the APS computation will provide.

The CI pipeline runs on every push. The badge is green. That means the framework
is self-consistent as of this writing. It does not mean it is right.

---

## Why the series ends here (for now)

Thirty-two posts. One claim: the arrow of time is a geometric identity, not a
statistical accident.

The claim rests on:
- One winding number (n_w = 5)
- One braid vector ((5, 7))
- One Chern-Simons level (k_CS = 74)
- One braided sound speed (C_S = 12/37)
- One coupling angle (β ≈ 0.35°)
- One falsification date (2032)

Everything else — the 74 pillars, the 14,183 tests, the domain applications from
cold fusion to governance — is the work of tracing the implications of those five
numbers through every corner of physics and human inquiry we could reach.

The series does not conclude. It pauses. The next substantive event is the first
precise measurement of β by a CMB polarisation survey with precision better than
the predicted gap width of 0.02°. When that measurement arrives, the series will
resume.

The prediction is specific. The timeline is known. The test is coming.

---

## A note on what the series tried to do

Post 0 set the terms: this series would apply a specific standard at every step.
- State claims precisely enough to be falsified.
- Be explicit about the tier (Tier 1 is physics; Tier 3 is analogy).
- Never claim a fit is a derivation.
- Document open problems without minimising them.
- Invite engagement rather than demanding deference.

Looking back across 32 posts, the series has tried to honour that standard. The
amplitude problem (×4–7 suppression) has been stated plainly at every relevant
point. The APS conjecture has been called a conjecture. The muon g−2 null result
(10⁻⁴¹ vs 10⁻⁹) has been published explicitly. The QGP coincidence has been
described as a dimensional coincidence, not a prediction.

If the series has done its job, readers come away knowing exactly what the framework
claims, exactly what it does not claim, and exactly how to check both.

The code is at the link below. The VERIFY.py script runs the consistency check.
FALLIBILITY.md has the full honest accounting. The rest is waiting for the sky.

---

*Full source code, derivations, and 14,183 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Completeness theorem: `src/core/completeness_theorem.py` — 170 tests*
*Primary falsifier: birefringence β — LiteBIRD 2032*
*Open problem: APS η-invariant conjecture — `src/core/aps_spin_structure.py`*
*Honest gaps: `FALLIBILITY.md`*
*Run the proof: `python VERIFY.py`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
