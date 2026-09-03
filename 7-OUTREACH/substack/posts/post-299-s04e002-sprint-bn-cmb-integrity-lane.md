# The CMB Integrity Line

**Unitary Manifold — S04E002 · v34.4 · Sprint BN**

---

The claim of this post is that the repository now distinguishes, in executable form, between a calibrated CMB scalar amplitude and a predicted one. This claim would fail if λ_COBE in the current code stopped depending on an external A_s target and produced the observed normalization from first principles alone. It does not.

That distinction sounds technical. It is actually ethical.

If a theory chooses a parameter so that the answer matches the sky, that is calibration. If the theory produces the answer before seeing the sky, that is prediction. The two are not interchangeable.

Sprint BN makes that boundary machine-checkable in **Pillar 999**.

---

## What Pillar 999 does

Pillar 999 asks a brutally simple question:

If you double the input target amplitude, what happens to the COBE-normalization parameter?

In the checked-in lane, λ_COBE scales with the supplied target. That means the pivot normalization is being fit to an observational input. It is not emerging independently from the geometry.

The pillar therefore labels the result exactly as it should be labeled:

`CALIBRATED_NOT_PREDICTED`

That single phrase removes a large amount of ambiguity.

---

## Why this was necessary

The CMB amplitude problem has been the hardest quantitative issue in the repository for a long time.

The framework gets the spectral index n_s right.
It keeps the braided tensor ratio viable.
It has a clean birefringence falsifier.

But the acoustic peak amplitude remains off by a factor of about 4–7 in the checked-in EFT architecture.

That gap should not be blurred by the fact that one can always choose a normalization parameter after the fact.

Pillar 999 prevents that blur.

---

## What the pillar links together

It does not just correct a label. It also connects the calibration boundary to the terminal evidence chain:

- KK tower correction,
- brane backreaction,
- rolling-radion route,
- Wess-Zumino cross-check,
- residual-budget accounting.

All four EFT routes remain exhausted.

So the sprint does not say, "maybe the answer is hiding in one more small correction."

It says:

inside the current architecture, the answer is not there.

---

## What would change the status

Not a new sentence.

A new mechanism.

The CMB amplitude lane can only be upgraded if the repository derives the normalization and transfer response without an observational A_s target or an equivalent fitted substitute.

In other words, a future UV/global completion has to do real work:

- produce the amplitude,
- propagate it through the acoustic transfer chain,
- survive comparison with the observed multipoles,
- do all of that without borrowing the answer from the data.

Until then, the honest status remains:

`CMB_AMP_CONFIRMED_IRREDUCIBLE`

---

## Why this is not a retreat

Because removing a false positive is not retreat.

A framework becomes more credible, not less, when it refuses to count calibration as prediction.

That is especially true in cosmology, where normalization tricks are easy to hide in prose and much harder to hide in executable code.

Pillar 999 moves the repository in the right direction:

- less ambiguity,
- less accidental overclaim,
- more explicit dependency on external inputs,
- more pressure on any future UV completion to earn the label "prediction."

---

## The larger Sprint BN picture

Sprint BN had two jobs:

1. run the strongest shared-state UV/flavor completion attempt now;
2. keep the hardest cosmology gap honest in its own dedicated lane.

That second job is what this pillar does.

The theory does not get credit for the number it was handed.
It only gets credit for the number it derives.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
