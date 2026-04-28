# Nine Ways to Break This Theory — A Guide for Adversarial Reviewers

*Post 36 of the Unitary Manifold series.*
*Claim: the Unitary Manifold's internal consistency can be tested mechanically.
This post gives a hostile reviewer nine specific handles — code mutations that
should break specific tests if the theory's structural claims are genuine.
If a mutation does not break any test, that is a problem with the test suite,
not a confirmation of the theory. If all nine mutations produce the predicted
failures, the structural claims are at minimum robustly encoded. Physical
correctness remains a separate question that only LiteBIRD, Roman, and the
APS computation can answer.*

---

Every scientific framework should invite attempts to break it. Not just
"peer review," which is too often a process of finding polite objections —
but adversarial, mechanical stress-testing: here is the claim, here is
the code that implements it, here is the specific change that should
invalidate it, here is the test that should fail.

The repository includes a document called `HOW_TO_BREAK_THIS.md` that
provides exactly this. This post works through nine of those handles in
detail, because the logic of each one explains something about what the
framework is actually claiming.

Clone the repository. Run the suite. Then try to break it.

```bash
git clone https://github.com/wuzbak/Unitary-Manifold-
cd Unitary-Manifold-
pip install -r requirements.txt
python -m pytest tests/ -q   # all green before you start
```

---

## Break 1: Change k_CS from 74 to anything else

**What the framework claims:** k_CS = 74 is not chosen. It is the unique
Chern-Simons level that simultaneously satisfies the sum-of-squares resonance
(5² + 7² = 74), the birefringence prediction, the braided sound speed fraction
C_S = 12/37, and the CMB spectral index n_s = 0.9635. Pillar 74's completeness
theorem gives seven independent constraints that all yield 74.

**The handle:** In `src/core/inflation.py`, change the constant
`CS_LEVEL_PLANCK_MATCH` from 74 to 73 (or 75, or any other integer).

**Expected failure:** `claims/integer_derivation/test_claim.py` fails at
`test_cs_level_is_unique_minimiser`. The test verifies that 74 minimises
a cost function that penalises failures of any one of the seven constraints.
At k = 73, at least one constraint fails.

**What this shows:** The claim that k_CS = 74 is derived — not a free
parameter adjusted to fit — is verifiable by mutation. If changing it to 73
broke no tests, the claim would be hollow.

---

## Break 2: Remove the KK Jacobian from the spectral index calculation

**What the framework claims:** The CMB spectral index n_s = 0.9635 is derived
from the 5D → 4D Jacobian of the KK dimensional reduction applied to the
inflationary effective potential. Without the Jacobian, n_s takes a very
different value — one inconsistent with Planck 2018.

**The handle:** In `src/core/inflation.py`, modify `effective_phi0_kk()` to
return `phi0_bare` instead of `n_winding × 2π × √(phi0_bare)` (i.e., bypass
the Jacobian).

**Expected failure:** `tests/test_inflation.py` fails at multiple spectral
index tests. With `phi0_bare` returned directly, `ns_from_phi0(phi0_bare=1.0)`
computes n_s ≈ 0.75 — more than 30σ outside the Planck 1σ window of
0.9649 ± 0.0042. Multiple tests that assert n_s is within the 1σ or 2σ
Planck range fail.

**What this shows:** n_s does not pass through the Planck window by coincidence
or parameter adjustment. It passes because the KK Jacobian — a specific,
geometrically motivated factor — transforms the field-space distance in a way
that produces the correct tilt. Removing it breaks the prediction.

---

## Break 3: Change the coupling formula for the axion-photon coupling

**What the framework claims:** The birefringence angle β ≈ 0.35° follows from
the Chern-Simons axion-photon coupling g_aγγ, which is derived from the anomaly
inflow on the compact S¹. The coupling formula involves a 1/(2π² r_c) volume
factor from the KK reduction of the 5D Chern-Simons term.

**The handle:** In the axion-photon coupling function, change the denominator
from `2 × π² × r_c` to `2 × π × r_c` (dropping one factor of π — a common
error in KK reductions that confuse the 5D volume element with the 4D one).

**Expected failure:** `claims/anomaly_inflow/test_claim.py` fails at
`test_coupling_formula_correct` and `test_beta_within_observational_window`.
With the wrong volume factor, g_aγγ increases by π, and β ≈ 1.1° — far
outside the observational 1σ window of ~0.34° ± 0.12°.

**What this shows:** The coupling formula is not a free parameter. The specific
combination of π factors in the KK dimensional reduction is locked to the
geometric structure of the compact S¹. Changing it by one factor of π produces
a prediction that conflicts with existing CMB birefringence measurements.

---

## Break 4: Make the primordial amplitude λ affect the spectral index

**What the framework claims:** The COBE/Planck normalisation of the primordial
power spectrum amplitude A_s does not introduce fine-tuning of the spectral
index n_s. The amplitude and tilt are independent in the framework: changing
A_s (via the coupling λ) does not shift n_s.

**The handle:** Add a small λ-dependent correction to `spectral_index()`:

```python
# Mutant — add this line:
return 1.0 - 6.0 * epsilon + 2.0 * eta + 1e-4 * lam
```

**Expected failure:** `claims/amplitude_normalization/test_claim.py` fails at
`test_ns_lambda_independent`. The test verifies that `n_s(λ=1) == n_s(λ_COBE)`
to numerical precision. With the mutant, n_s shifts by ~10⁻⁴ × (λ_COBE − 1),
which is small but detectable at the test's numerical tolerance.

**What this shows:** The independence of n_s from λ is a structural property
of the framework, not an approximation. The test enforces that the spectral
index cannot be fine-tuned by adjusting the amplitude coupling — the same
parameters that normalise A_s must not affect the shape n_s.

---

## Break 5: Disable entropy production (reverse the arrow of time)

**What the framework claims:** The arrow of time in the Unitary Manifold is
not a statistical tendency — it is a geometric identity. The holographic
boundary dynamics produce entropy that is monotonically non-decreasing by
construction. This is not Boltzmann's H-theorem applied to a large system;
it is an exact property of the field equations on the boundary.

**The handle:** In `src/holography/boundary.py`, negate the entropy production
term so entropy decreases over time.

**Expected failure:** `tests/test_arrow_of_time.py` fails at
`TestEntropyMonotonicity`. The test verifies that `S(t + dt) ≥ S(t)` for
all time steps in the numerical evolution. With the negated term, entropy
decreases at every step — the test catches this immediately.

**What this shows:** The arrow of time is encoded as a constraint in the
equations of motion, not as an emergent statistical behaviour. It is not
possible to reverse entropy while keeping the rest of the framework intact —
the constraint is hard-wired.

---

## Break 6: Break FTUM fixed-point convergence

**What the framework claims:** The Fundamental Theory of Universal Mechanics
(FTUM) operator U = I + H + T has a unique fixed point in the relevant function
space. This is the basis for the multiverse selection mechanism in Pillar 5.

**The handle:** In `src/multiverse/fixed_point.py`, increase the iteration
step size to force non-convergence (overshoot the fixed point on each step).

**Expected failure:** `tests/test_fixed_point.py` fails at convergence tests
that verify the iteration error ‖U^n(φ) − φ*‖ → 0 as n → ∞. With an overshoot
step, the iteration oscillates around the fixed point without converging.

**What this shows:** The fixed-point convergence is not trivially guaranteed.
The specific step size and operator structure are tuned to the contraction mapping
condition. The test suite enforces this convergence as a numerical fact, and
the mutation breaks it when the condition is violated.

---

## Break 7: Remove the φ-correction from atomic spectra

**What the framework claims:** The 5D radion leaves a signature in atomic
spectra: the φ-corrected energy levels of hydrogen-like atoms shift by a small
amount proportional to the φ-field mean value. This is Pillar 14.

**The handle:** In `src/core/atomic_structure.py`, modify `phi_corrected_energy()`
to return the bare Bohr energy unchanged (no φ correction).

**Expected failure:** `tests/test_atomic_structure.py` fails at tests that
verify the φ-shift produces a non-zero correction — specifically
`test_phi_correction_nonzero` and `test_hydrogen_1s_phi_shift`.

**What this shows:** The φ-correction is a genuine, non-trivial modification to
the atomic spectrum. The tests enforce that the corrected energy differs from the
bare energy by a specific amount. The correction is small (sub-fine-structure
level) but it is there.

---

## Break 8: Remove the φ-enhancement from cold fusion tunnelling

**What the framework claims:** The Unitary Manifold predicts enhanced tunnelling
rates in Palladium-Deuterium lattices due to the φ-field geometry. This is Pillar 15
— and it is one of the framework's most provocative claims. Post 17 covered it in
detail, noting that it is explicitly framed as a falsifiable prediction, not a
confirmation that LENR occurs.

**The handle:** In `src/core/cold_fusion.py`, set the φ-enhancement factor to 1.0
(no enhancement) in `phi_enhanced_tunneling_probability()`.

**Expected failure:** `tests/test_cold_fusion.py` fails at `test_enhancement_exceeds_bare`
and `test_excess_heat_positive`. The tests verify that the φ-enhanced tunnelling
probability exceeds the bare WKB baseline. With the enhancement factor set to 1.0,
the φ-enhanced probability equals the bare probability, and the excess heat
prediction drops to zero.

**What this shows:** The cold fusion prediction is structural, not cosmetic.
The φ-field geometry makes a quantitative difference to the tunnelling rate.
Whether that difference corresponds to real physics is what laboratory experiments
must determine.

---

## Break 9: Change the winding number from 5 to any other value

**What the framework claims:** n_w = 5 is selected by the intersection of the
APS orbifold constraint, the three-generation count ⌊n_w/2⌋ + 1 = 3, and the
anomaly cancellation argument (Post 23, Post 31). No other winding number
simultaneously satisfies all three.

**The handle:** In any module that uses the winding number as a parameter,
set N_W = 7 (the next candidate). The most direct test: run
`tests/test_three_generations.py` with n_w = 7.

**Expected failure:** The test `test_n7_gives_four_generations` passes (n_w = 7
predicts 4 generations, not 3). But `test_three_generations_from_n5` will still
pass for n_w = 5 — the test explicitly checks that n_w = 5 gives exactly 3 stable
generations. The suite includes tests that verify n_w = 7 is inconsistent with
the observed three-generation constraint.

**What this shows:** n_w = 5 is not arbitrary. The three-generation constraint
alone eliminates n_w = 7. The anomaly cancellation argument (Pillar 67) narrows
to {5, 7}, and the three-generation count eliminates 7. These are independent
constraints that intersect at n_w = 5.

---

## What a real break looks like

Not all test failures are equal.

A break that matters is one where:
1. The failing test corresponds to a physical claim (not a numerical coincidence).
2. The failure cannot be fixed by adjusting a free parameter.
3. The failure is reproducible from a clean clone.

If you find such a break, the right response is to open a GitHub issue titled
"Break report: [claim name]" with the test output. The repository is a public
scientific claim. A legitimate break deserves public documentation and a public
response.

If you run all nine mutations and they all produce the expected failures, that
is structural evidence — not proof of physical correctness, but evidence that
the theory has been correctly encoded and that its internal claims are mutually
reinforcing. A framework that falls apart under mutation without claiming to
be physically correct is worse than a framework that holds together under mutation
while being transparent about what empirical tests remain.

The physical test is LiteBIRD 2032. The structural tests are above.

---

*Full source code, derivations, and 12,950+ automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Adversarial test guide: `HOW_TO_BREAK_THIS.md`*
*Structural break handles: `claims/` directory*
*Run everything: `python -m pytest tests/ recycling/ "Unitary Pentad/" -q`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
