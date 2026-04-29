# Building Science Without a Lab

*Post 61 of the Unitary Manifold series.*
*No falsifiable physics claim is made in this post. It is an epistemological
examination of the status of 13,000 automated assertions as evidence — what they
prove, what they don't prove, and how they fit into the broader evidential structure
that science requires.*

---

The repository has 14,183 automated tests that pass. Every time someone runs
`python -m pytest tests/ recycling/ "Unitary Pentad/" -q`, they get back:

    14183 passed, 2 skipped, 11 deselected, 0 failed

What does this mean?

The answer has two parts. The first part is what most people assume it means.
The second part is what it actually means. Both matter.

---

## What it doesn't mean

Passing 14,183 tests does not mean the theory is correct.

The tests verify that the code faithfully implements the stated mathematics. When
`tests/test_inflation.py` passes, it means that the Python function `spectral_index()`
returns a value within the claimed range. It means that when the winding number is
set to 5, the result is consistent with the stated derivation.

It does not mean that winding number 5 correctly describes the actual universe.
It does not mean that the actual CMB spectral index is 0.9635 rather than some
other value. It does not mean that the Chern-Simons mechanism for birefringence
is physically real.

A test suite is a specification verifier. It verifies that the code matches the spec.
It says nothing about whether the spec matches nature.

This distinction matters enormously, and we make it explicit every time we describe
the test suite. "14,183 tests" is not shorthand for "14,183 pieces of evidence that
the theory is right." It is shorthand for "14,183 verifications that the code
correctly implements what it claims to implement."

---

## What it does mean

**Internal consistency.** The most direct thing the tests establish is that the
framework is internally consistent — the various components don't contradict each other.
When `tests/test_completeness_theorem.py` passes, it means that the seven independent
constraints on k_CS = 74 are simultaneously satisfiable. When `tests/test_evolution.py`
passes, it means that the numerical evolution doesn't produce runaway divergences or
obvious numerical artifacts.

Internal consistency is necessary but not sufficient for physical correctness.
A framework can be perfectly self-consistent and describe nothing in nature.
But a framework that is *inconsistent* cannot be correct — so internal consistency
is a real filter, just not the final one.

**Reproducibility.** Any researcher with Python installed can clone the repository
and reproduce every calculation in under three minutes. The results are not
"our lab got these numbers" — they are "anyone who runs this code gets these numbers."
This is stronger reproducibility than most experimental physics provides, because the
computational steps are visible and the random elements are controlled.

**Mutation resistance.** The test suite provides handles for adversarial testing
(Post 36). When specific inputs are mutated — k_CS changed from 74 to 73, winding
number changed from 5 to 7, entropy production negated — specific tests fail. This
mutation resistance demonstrates that the framework's internal claims are robustly
encoded, not accidentally satisfied.

---

## The epistemological status

The framework occupies a specific position in the epistemological landscape of science:

It is more than **speculation** — the predictions are specific, quantified, and
derivable from the stated premises. Speculation is vague; this is precise.

It is less than **confirmed theory** — the predictions have not been independently
tested by experiments designed specifically to probe them. The birefringence
measurement that suggested β ≈ 0.35° was not designed to test this framework;
it was a CMB polarization measurement that the framework's prediction happens
to match.

It is in the category physicists call **motivated hypothesis**: a framework with
specific, falsifiable predictions, internal consistency, and preliminary agreement
with existing data, which has not yet been subjected to the decisive experiment
designed specifically to test it.

Most of the history of physics consists of motivated hypotheses at various stages of
evaluation. General relativity was a motivated hypothesis from 1915 to 1919, when
the solar eclipse measurement confirmed its light-bending prediction. The electroweak
unification was a motivated hypothesis from 1967 to 1983, when the W and Z bosons
were discovered. The Higgs boson was a motivated hypothesis from 1964 to 2012.

The decisive experiment for this framework is LiteBIRD's birefringence measurement
around 2032. Until then, "motivated hypothesis" is the correct description.

---

## What a lab would add

The obvious objection: "real physics requires experimental apparatus, not software."

True, and the absence of experimental apparatus is a genuine limitation.

What experiments could in principle test the framework's non-cosmological claims:

- **Grid cell frequency ratio measurement** — high-precision recording of entorhinal
  cortex module spacings in multiple species, at sufficient resolution to determine
  whether 7:5 is a preferred ratio.
- **Casimir force precision measurement** — at 0.1% precision, the φ-field correction
  to the Casimir effect (Pillar 7 extension) would become detectable.
- **Cold fusion calorimetry** — controlled excess heat measurement in Pd-D lattices
  at conditions specified by the `src/cold_fusion/` module.

None of these require a multibillion-dollar satellite. They require labs.

We don't have labs. The repository is public and the predictions are specific; we
invite experimentalists to engage with the predictions and design tests.

---

*Full source code, derivations, and 14,183 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Test suite: `python -m pytest tests/ recycling/ "Unitary Pentad/" -q`*
*Honest gaps: `FALLIBILITY.md`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
