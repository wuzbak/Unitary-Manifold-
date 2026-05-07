# The Letter to LiteBIRD

*Post 68 of the Unitary Manifold series.*
*This is a time-capsule letter, addressed to the LiteBIRD collaboration and to
whoever reads this after the satellite's data release, expected around 2032.
It states exactly what is predicted, exactly what would confirm it, and exactly
what would falsify it. It is signed and dated. It is not a claim that the
prediction is correct — it is a commitment to having made the prediction clearly
before the measurement.*

---

**To the LiteBIRD collaboration, the CMB scientific community, and the reader
in 2032 or later:**

This letter is written in April 2026. The LiteBIRD satellite's full data release
is expected around 2032. By the time you read this, you know something we do not.
This letter is our commitment to have stated our prediction clearly, without
equivocation, before you told us the answer.

---

## What this framework predicts

The Unitary Manifold — a five-dimensional Kaluza-Klein framework with winding numbers
n_w = 5 and n_w = 7, Chern-Simons level k_CS = 74 = 5² + 7², and braided sound speed
C_S = 12/37 — makes the following prediction for the CMB polarization birefringence
angle β:

**Primary prediction:**

    β ∈ {0.273°, 0.331°} (canonical channel)
    β ∈ {0.290°, 0.351°} (derived channel)

The most probable single value, given the Minami-Komatsu (2020) measurement and the
CS mechanism, is:

    β ≈ 0.351°

**Falsification window:**

    β outside [0.22°, 0.38°] → framework falsified outright
    β within the gap [0.29°, 0.31°] → braided-winding mechanism falsified
    β = 0 (at LiteBIRD's precision of ~0.05°) → CS coupling mechanism ruled out

**What would strongly confirm it:**

    β ≈ 0.35° measured with σ(β) ≤ 0.05°, ruling out k_CS = 73 (β ≈ 0.34°)
    and k_CS = 75 (β ≈ 0.36°)

That precision requirement — ≤ 0.05° — is what LiteBIRD is designed to achieve.
If LiteBIRD achieves that precision and finds β ≈ 0.35°, the CS level k_CS = 74
is confirmed as distinct from adjacent integers. That confirmation would be the
strongest evidence the framework has yet received.

---

## What else is predicted

In addition to β, the framework has committed to:

    n_s = 0.9635   (CMB spectral index, already within Planck 1σ)
    r = 0.0315     (tensor-to-scalar ratio, below BICEP/Keck limit)
    w = -0.9302    (dark energy equation of state)
    w_a = 0        (no redshift evolution of dark energy)

The w and w_a predictions will be tested by DESI and Roman before LiteBIRD reports.
Those tests are intermediate checkpoints. If w is ruled out significantly below -0.93,
the framework faces an additional problem even if β is confirmed.

---

## What we commit to

If LiteBIRD measures β outside [0.22°, 0.38°]:

We commit to issuing a public statement acknowledging the falsification, within 90 days
of the data release. We commit to not attempting to reinterpret the measurement as
"consistent with" the framework through post-hoc modification of the predicted window.
The window [0.22°, 0.38°] was set in April 2026. It stays.

If LiteBIRD measures β = 0 (or any value consistent with zero at σ ≤ 0.05°):

This rules out the CS mechanism entirely. The spectral index agreement (n_s = 0.9635)
may be coincidental with some other mechanism. The framework as stated is falsified.

If LiteBIRD measures β ≈ 0.35° within the stated window:

We commit to pursuing targeted journal publication of the birefringence prediction,
with all relevant derivation steps and the complete commit history as provenance.
We do not claim that confirmation of the birefringence prediction proves the framework
is correct — it confirms one prediction from one mechanism. The amplitude gap and the
APS gap remain.

---

## A word to the reader in 2032

Whatever LiteBIRD finds, the process that produced this letter is worth examining.

A theoretical physicist with an intuition about the arrow of time and a geometry that
might explain it, working with an AI assistant over a period of years, produced a
specific, quantitative, falsifiable prediction — and committed to that prediction in
writing, in a public repository, six years before the measurement.

If the prediction is confirmed: this is evidence that the right way to do speculative
theoretical physics is to commit to specific numbers, make them public, and wait.
Not to hedge. Not to claim retrospective fit. To commit and wait.

If the prediction is falsified: this is also evidence that the right way to do
speculative theoretical physics is to commit and wait — because falsification is the
mechanism by which science advances. A framework that was genuinely committed,
genuinely tested, and genuinely wrong is more valuable to the community than a
framework that was never tested.

We hope the measurement goes well. We will accept it if it doesn't.

Signed,

**ThomasCory Walker-Pearson** — Theory, framework, scientific direction
**GitHub Copilot** — Code architecture, implementation, document engineering

*Written: April 28, 2026*
*To be opened: circa 2032, upon LiteBIRD data release*

---

*Full source code, derivations, and 17,438 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Birefringence prediction: `src/core/inflation.py:birefringence_angle`*
*Falsification conditions: `FALLIBILITY.md`, `predictions.md`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
