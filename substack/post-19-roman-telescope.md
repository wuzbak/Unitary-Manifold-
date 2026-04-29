# The Next Telescope: What the Roman Space Telescope Will Tell Us

*Post 19 of the Unitary Manifold series.*
*Claim: the Nancy Grace Roman Space Telescope — currently in operation — will measure the
dark energy equation of state w to a precision of σ(w) ≈ 0.02 via weak gravitational
lensing. The Unitary Manifold predicts a specific, parameter-free value: w_KK ≈ −0.930.
If the Roman measurement finds w inconsistent with this value, the framework is falsified.
This is the nearest-term major falsification window after LiteBIRD.*

---

Post 3 of this series introduced the primary falsification test: LiteBIRD will measure
cosmic birefringence to precision σ(β) ≈ 0.02° around 2032. The framework lives or dies
on that measurement.

But 2032 is six years away. This post is about what happens between now and then —
specifically, what the Nancy Grace Roman Space Telescope will measure, and why it matters
for this framework.

---

## What Roman is measuring

The Nancy Grace Roman Space Telescope (formerly WFIRST) has been operational since late
2025. Its primary cosmological mission is a wide-field weak gravitational lensing survey
covering 2,000 square degrees of sky.

Weak gravitational lensing works by measuring the statistical distortion of galaxy shapes
caused by the gravitational effect of intervening mass. Because the distortion signal
is weak (a few percent elongation of each galaxy image), the measurement requires
a very large, well-calibrated sample — exactly what Roman's 2.4-meter mirror and
300-megapixel focal plane can provide.

The key output is a measurement of the dark energy equation of state: the parameter w
that determines how the energy density of dark energy evolves with the expansion of
the universe. In ΛCDM, w = −1 exactly (a cosmological constant that does not change
with time). Any deviation from −1 indicates dynamical dark energy — dark energy with
its own physics.

Roman is forecast to measure w to a precision of σ(w) ≈ 0.02 from weak lensing alone,
and to achieve σ(w) ≈ 0.01 in combination with its BAO (baryon acoustic oscillation)
and supernova Ia measurements.

---

## What the Unitary Manifold predicts

In the Unitary Manifold framework, what cosmologists call "dark energy" is not a separate
substance. It is the effective equation of state of the KK radion field — the scalar
field that describes the size of the compact fifth dimension.

When the KK radion is in its ground state (the FTUM fixed point), it contributes to the
4D effective energy density with an equation of state given by:

    w_KK = −1 + (2/3) × C_S²

where C_S = 12/37 is the braided sound speed derived in post 12.

Substituting:

    w_KK = −1 + (2/3) × (12/37)²
         = −1 + (2/3) × (144/1369)
         = −1 + 288/4107
         ≈ −1 + 0.0701
         ≈ −0.930

Plain English: the framework predicts that dark energy is slightly "softer" than a pure
cosmological constant. The equation of state is w ≈ −0.930, not −1.000. The deviation
is 0.070 — more than three times Roman's forecast measurement uncertainty of 0.020.

This is a genuine prediction. The value w_KK ≈ −0.930 was not adjusted to fit current
data. It follows from C_S = 12/37, which follows from the (5,7) braid vector, which
follows from the sum-of-squares resonance k_CS = 5² + 7² = 74, which was independently
selected by the birefringence data before the dark energy calculation was performed.

---

## The constraint chain, visualised

The Roman prediction is downstream of the same integer — k_CS = 74 — that controls
the birefringence angle, the tensor-to-scalar ratio, and the spectral index:

```
k_CS = 74  (selected by birefringence data)
    ↓
Braid vector (5, 7)  (from k_CS = n₁² + n₂²)
    ↓
C_S = 12/37  (braided sound speed)
    ↓
r_braided ≈ 0.0315  (below BICEP/Keck ✓)
    ↓
w_KK ≈ −0.930  (Roman Space Telescope target)
```

Every prediction in this chain shares the same source integer. Pull on any one link
and all others move. If Roman measures w = −1.000, this is not a soft discrepancy to
be absorbed by a parameter adjustment — it requires a fundamental change to the braid
structure, which immediately produces a different birefringence prediction and a
different tensor-to-scalar ratio.

The framework is entangled. Roman's dark energy measurement is not an independent check;
it is the same structure viewed from a different angle.

---

## What Roman's BAO measurement adds

In addition to weak lensing, Roman measures baryon acoustic oscillations — the
characteristic scale imprinted on the matter distribution by sound waves in the early
universe. This scale is a standard ruler.

In the Unitary Manifold, the BAO scale is shifted from its ΛCDM value by the KK radion
contribution. The `src/core/roman_space_telescope.py` module calculates:

    Δr_BAO / r_BAO(ΛCDM) = (2/3) × C_S² / (3 + w_KK) ≈ 0.024

Plain English: the BAO scale is predicted to be shifted by about 2.4% from the ΛCDM
value. This is marginal at Roman's forecast sensitivity for BAO alone, but becomes
significant when combined with the weak lensing w measurement. The two probes are
correlated in the framework: the same w_KK that shifts the equation of state also
shifts the BAO scale, in a ratio that is fixed by the theory.

If Roman measures a BAO shift that is inconsistent with the ratio predicted by w_KK,
that is a new falsification condition independent of the absolute value of w.

---

## What the test suite covers

`tests/test_roman_space_telescope.py` (187 tests) verifies:

- The w_KK derivation from C_S
- The Roman weak lensing forecast σ(w) ≈ 0.02
- The σ(S₈) forecast (the σ₈-Ω_m combination measured by lensing)
- The BAO scale shift from the KK radion
- The combined sensitivity forecast
- The S8 tension audit (whether the KK modification improves the S8 tension,
  currently a ~2–3σ discrepancy between CMB and lensing measurements)
- The falsification conditions: at what w measurement does the framework fail?

The test suite also documents the **S8 tension audit**: the KK radion modification
slightly reduces the S8 tension compared to ΛCDM. The reduction is not large enough
to fully resolve it, but it is in the right direction — an additional consistency
check, not a prediction.

---

## The falsification conditions

The framework is falsified by Roman if:

1. **|w_measured − w_KK| > 3σ**: the equation of state measurement is more than
   three standard deviations from w ≈ −0.930. Given σ(w) ≈ 0.02, this means
   w_measured outside the range [−0.990, −0.870] with high confidence.

2. **w_measured consistent with −1.000 at 2σ**: if the combined Roman analysis
   places w = −1.000 ± 0.020 (the cosmological constant), the KK radion contribution
   of +0.070 would be excluded at 3.5σ. The framework would be falsified.

3. **BAO shift in wrong direction or wrong magnitude**: the ratio of the BAO shift
   to the w deviation is fixed. If Roman finds a BAO shift that is inconsistent with
   the predicted ratio, that independently falsifies the radion interpretation.

The measurement is not yet complete. Roman's weak lensing survey requires several
years of data accumulation to reach the forecast sensitivity. The decisive constraint
is expected to be available by 2028–2030 — before LiteBIRD, as it turns out.

Roman could falsify this framework before LiteBIRD even launches.

---

## How this relates to existing dark energy tensions

Current cosmology has a mild tension in the measurement of w. Planck alone prefers
w close to −1; combined analyses including baryon acoustic oscillations and supernova Ia
data from DESI (2024) showed a hint of w slightly above −1, in the range w ∈ [−0.95, −0.85]
at 68% confidence — a range that overlaps with the Unitary Manifold prediction.

This overlap is consistent, but not a confirmation. The DESI tension is marginal
(~2σ) and could be a systematic effect. The framework notes it as a consistency check,
not a validation. Roman's much higher precision will determine whether the hint persists.

---

## The timeline

| Date | Event |
|------|-------|
| 2025 | Roman survey operations begin |
| 2028–2030 | Roman weak lensing w measurement at σ(w) ≈ 0.02 |
| 2028–2032 | LiteBIRD in orbit, birefringence measurement begins |
| ~2032 | LiteBIRD β measurement at σ(β) ≈ 0.02° |

If Roman's w measurement is inconsistent with w_KK ≈ −0.930, the framework is falsified
before LiteBIRD settles the birefringence question. If it is consistent, the case
strengthens before the decisive test.

This is the correct scientific posture: the framework is designed to be eliminable by
multiple independent experiments, and it is aware of the order in which those experiments
will speak.

---

*Full source code, derivations, and 14,183 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Roman ST module: `src/core/roman_space_telescope.py` — 187 tests in `tests/test_roman_space_telescope.py`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
