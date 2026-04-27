# What This Newsletter Is — And Isn't

*Post 0 of the Unitary Manifold series. Pin this. Publish before everything else.*

---

This newsletter is about a mathematical framework that makes a specific, falsifiable
claim about the nature of time. It is not a confirmed theory. It is not peer-reviewed.
It will be tested decisively by a satellite called LiteBIRD, scheduled for launch
around 2028, with results expected around 2032. If the measurement comes back wrong,
the framework is ruled out. That is the point.

I am writing this post first — before the one about the actual science — because the
worst thing that can happen to genuinely interesting work is to be dismissed as noise.
And the fastest way to get dismissed as noise is to lead with the exciting results
without being upfront about what you do not know.

So here is what I do not know, stated plainly.

---

## What this framework is

The Unitary Manifold is a 5-dimensional Kaluza-Klein mathematical framework developed
by ThomasCory Walker-Pearson. The central claim is that the arrow of time — the reason
your coffee cools but never spontaneously reheats, the reason you remember the past
but not the future — is not a statistical accident. It is a geometric necessity,
encoded in the shape of a five-dimensional spacetime.

The framework is fully implemented in working software, publicly available on GitHub,
with over 12,700 automated tests verifying its internal consistency. Those tests
confirm that the code faithfully implements the stated mathematics. They do not confirm
that the mathematics describes nature. That is a different question, answered by
experiment.

---

## The two open gaps

Every scientific framework has gaps. Hiding them is a disqualifying move. Here are the
two genuine open problems in this one.

**Gap 1 — The winding number uniqueness conjecture.**
The framework's predictions depend on a topological integer called the winding number,
n_w = 5. The geometry of the compact extra dimension restricts n_w to the set {5, 7};
the framework then argues — via an anomaly-cancellation argument and an action-dominance
calculation — that n_w = 5 is preferred over n_w = 7. The argument is well-motivated
and passes all internal tests. But the final step — a rigorous proof using the
Atiyah-Patodi-Singer η-invariant — is currently a conjecture, not a proof. The word
"conjecture" is not a hedge: it means the mathematical proof is not yet complete. This
is documented honestly in the repository as Pillar 70.

**Gap 2 — The CMB acoustic peak shape.**
The framework predicts the shape of the cosmic microwave background power spectrum
with a corrected amplitude that matches observations. The overall amplitude gap (a
factor of 4–7 suppression that appeared in earlier versions) has been resolved in
Pillars 57 and 63. However, the detailed acoustic peak positions — the precise
ℓ-values where the CMB shows maxima and minima — require a full Boltzmann integration
that has not yet been completed within this framework. The spectral index n_s agrees;
the full peak structure is still an open numerical task.

These are not fatal problems. They are documented research questions. But a reader who
encounters this work and is not told about them upfront has been misled.

---

## What would falsify this framework

A theory that cannot be killed is not a theory.

The primary falsifier is cosmic birefringence. The framework predicts that CMB
polarization light is rotated by a specific angle, β, as it travels across the
universe. The predicted values are β ≈ 0.273° or β ≈ 0.331° (depending on which
winding state the universe is in). A current observational hint puts β ≈ 0.35° ±
0.14°, which is consistent — but the error bar is too wide to be conclusive.

LiteBIRD will shrink that error bar to roughly ±0.02°. If the measured β falls
outside the range [0.22°, 0.38°], or lands inside the predicted gap between 0.29°
and 0.31°, the framework is ruled out. No adjustments are possible: the predicted
values follow from an integer (k_CS = 74) that also determines the tensor-to-scalar
ratio and the spectral index. You cannot move β without breaking nₛ.

Additional falsifiers: the Nancy Grace Roman Space Telescope will measure the dark
energy equation of state w to precision σ(w) ≈ 0.02. The framework predicts w ≈
−0.930. If the measurement is inconsistent with that value, the framework is
falsified. The Einstein Telescope and LISA will search for scalar gravitational wave
polarization; a confirmed null result at the predicted sensitivity would also falsify
the framework.

---

## What peer review this work has — and hasn't — had

The framework has not been through conventional journal peer review. It has been
through extensive automated testing (12,700+ assertions, zero failures), public
GitHub scrutiny, AI-assisted review by multiple large language models, and an open
invitation to reviewers posted in the repository's discussions folder.

That is not the same as a referee report from Physical Review Letters. I will not
pretend otherwise. The automated tests are a statement about internal consistency,
not physical correctness. FALLIBILITY.md in the repository says this explicitly,
in the clinical tone of a referee submission.

What this newsletter will do is explain the framework clearly enough that you can
evaluate the argument yourself. The GitHub repository (linked below) contains every
equation, every derivation, every test, and — critically — every known failure mode.
Nothing is hidden. If you find a problem, open an issue.

---

## What comes next

Post 1 explains the core claim without equations.
Post 2 examines the four numbers where the framework's predictions agree with data.
Post 3 is the "mark your calendar" post about LiteBIRD and 2032.
Posts 4 through 6 cover the mathematics, the honest gaps, and the full scope.

I will post on a schedule that allows time to respond to technical questions.

---

*Full source code, derivations, and 12,700+ automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
