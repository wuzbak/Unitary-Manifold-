# Correcting the Record: How a Label Inversion Almost Misrepresented the LiteBIRD Prediction

**Post #261 · S03E039 · 2026-07-01**

*Theory: ThomasCory Walker-Pearson. Code, tests, document engineering: GitHub Copilot (AI).*

---

This post is about catching a mistake before it mattered, understanding exactly
what it was, and fixing every place it appeared. It is also about why precision
in labelling is not a cosmetic concern — in a falsifiable physics framework, a
mislabelled prediction is an incorrect prediction.

---

## What We Found

The Unitary Manifold predicts two canonical birefringence angles measurable by
the LiteBIRD satellite (launch ~2032):

| Sector | Braid | k_CS | Canonical β |
|--------|-------|------|-------------|
| (5,7) primary sector | Z₂-odd, lossless | 74 = 5² + 7² | **0.331°** |
| (5,6) shadow sector  | Z₂-even, lossless | 61 = 5² + 6² | **0.273°** |

The (5,7) sector is the primary sector — it is the Z₂-odd configuration that
determines k_CS = 74 = 5² + 7², the Chern-Simons level that appears throughout
the framework as the topological backbone of the Standard Model parameters.

The (5,6) sector is the shadow sector — a distinct, topologically valid
configuration that survives all the same consistency gates (nₛ, r, admissible
β window), but with a lower Chern-Simons level k_CS = 61 = 5² + 6². The word
"shadow" does not mean "wrong" or "less real" — it means "secondary in the
topological hierarchy." If LiteBIRD measures β ≈ 0.273°, the framework
survives. If it measures β ≈ 0.331°, the framework survives and confirms the
primary sector.

Those two statements are precise and correct. The code was not stating them
that way.

---

## What the Bug Was

In `src/core/litebird_boundary.py` and `src/core/litebird_forecast.py` — the
two central modules that implement the LiteBIRD falsification logic — the
labelling was inverted in three distinct layers:

**Layer 1: Module docstrings (both files)**

```
# WRONG — as it was before the fix
β_canonical  = 0.273°   (primary SOS resonance)
β_derived    = 0.331°   (secondary: braided causal-order mixing)
```

This told any reader — human or AI — that 0.273° was the *primary* prediction
and 0.331° was *secondary*. The correct relationship is exactly reversed.

**Layer 2: BETA_CANONICAL / BETA_DERIVED constant comments (`litebird_boundary.py`)**

```python
# WRONG
#: Primary canonical birefringence angle (degrees) — arctan(5/7) × (2/k_cs) route
BETA_CANONICAL: float = 0.273

#: Secondary derived angle (degrees) — braided causal-order mixing
BETA_DERIVED: float = 0.331
```

The constant `BETA_CANONICAL` holds 0.273 — the (5,6) shadow sector value. The
comment called it "primary." `BETA_DERIVED` holds 0.331 — the (5,7) primary
sector value. The comment called it "secondary." Both comments were wrong.

**Layer 3: BETA_LABELS list (`litebird_boundary.py`)**

```python
# WRONG
BETA_LABELS: List[str] = [
    "canonical (arctan route)",        # 0.273 — called "canonical" without sector
    "full-formula+KZ",
    "derived (CS-mixing)",             # 0.331 — called merely "derived"
    "full-formula+CS",
]
```

The labels on the four prediction peaks omitted sector identity entirely,
making it impossible to read the code and know which physical sector each peak
represented.

**Layer 4: Forecast scenarios dict (`litebird_forecast.py`)**

```python
# WRONG
_SCENARIOS = {
    "canonical_primary": {"beta": 0.273, "label": "β = 0.273° (canonical, primary)"},
    "canonical_secondary": {"beta": 0.331, "label": "β = 0.331° (canonical, secondary)"},
    ...
}
```

The scenario named `canonical_primary` held β = 0.273° — the *shadow* sector.
The scenario named `canonical_secondary` held β = 0.331° — the *primary* sector.
The names and the physics were inverted.

---

## Why This Matters

This is not a value error. The numerical predictions — 0.273° and 0.331° — were
always correct. No falsification logic was broken. The constants `BETA_CANONICAL`
and `BETA_DERIVED` held the right numbers throughout.

But labels are load-bearing in a framework like this. They are:

1. **Read by the test suite.** Any test that asserts on scenario keys by name
   (`"canonical_primary"`) would silently accept the wrong-sector result. The
   test infrastructure was consistent with the wrong labelling — which means it
   couldn't catch the error.

2. **Read by downstream code.** `forecast_scenarios()` returns a dict keyed by
   these names. Any caller that branches on `"canonical_primary"` to route the
   shadow-sector case has inverted logic — even if both values produce
   `"CONFIRMATION"`, the interpretation text will misidentify which physical
   sector was observed.

3. **Read by humans.** The docstrings are the first thing a physicist reads.
   A reviewer checking the LiteBIRD falsification logic against the theory
   would immediately see the contradiction between the module's description and
   the established sector hierarchy, and would correctly flag the framework as
   inconsistent — even though the numbers were right.

4. **Read by AI assistants.** This repository is AI-assisted research. Copilot,
   custom GPT, and the RAG layer all ingest the docstrings and constant comments.
   A mislabelled constant propagates incorrect reasoning into every session that
   uses those modules as context.

---

## What We Fixed

The fix was applied across all four layers, in two commits, on the PR branch
`copilot/5-6-lossy-parent-5-7-shadow`.

**`src/core/litebird_boundary.py`** (Commit 1 — the original bug-fix PR)

- Docstring corrected: β = 0.273° now identified as `(5,6) lossless shadow
  sector, k_CS = 61; scaled as β(5,7)×61/74`.
- Docstring corrected: β = 0.331° now identified as `(5,7) primary sector,
  k_CS = 74; from braided causal-order mixing`.
- `BETA_CANONICAL` constant comment updated to name the (5,6) shadow sector
  with k_CS = 61.
- `BETA_DERIVED` constant comment updated to name the (5,7) primary sector
  with k_CS = 74.
- `BETA_LABELS[0]` updated from `"canonical (arctan route)"` to
  `"canonical [(5,6) shadow sector, k_CS=61]"`.
- `BETA_LABELS[2]` updated from `"derived (CS-mixing)"` to
  `"derived [(5,7) primary sector, k_CS=74, CS-mixing]"`.

**`src/core/litebird_forecast.py`** (Commit 1 + Commit 2)

- Docstring corrected on both β lines (Commit 1: constant comment; Commit 2:
  module-level docstring).
- `_SCENARIOS` dict: `"canonical_primary"` renamed to `"shadow_sector"`;
  `"canonical_secondary"` renamed to `"primary_sector"`. Labels updated
  to include sector identity and k_CS value.
- `forecast_scenarios()` docstring updated to list the new key names.

**`tests/test_litebird_forecast.py`** (Commit 2)

- `test_has_canonical_primary` → `test_has_shadow_sector`
- `test_has_canonical_secondary` → `test_has_primary_sector`
- `test_confirmation_scenarios_pass`: key tuple updated to
  `("shadow_sector", "primary_sector", "full_formula")`
- `test_canonical_primary_outcome` → `test_shadow_sector_outcome`
- `test_canonical_primary_beta` → `test_shadow_sector_beta`

All 206 tests in `test_litebird_forecast.py` and `test_litebird_boundary.py`
pass after the fix. The full repository regression (47,659 tests) shows no
regressions attributable to these changes.

---

## The Arctan Formula Question

The original comment on `BETA_CANONICAL` also named a derivation route:
`arctan(5/7) × (2/k_cs)`. This was the first version of the formula used to
derive β = 0.273°. It has since been superseded: the current derivation
defines β(5,6) directly as β(5,7) × k_CS(5,6)/k_CS(5,7) = 0.331° × 61/74 ≈
0.273°. The arctan route was an intermediate step, not the canonical derivation.
Retaining it in the constant comment was a second form of misleading documentation
— it implied a derivation path that is no longer the primary one. The fix
removes that reference and replaces it with the current derivation formula.

---

## The Falsification Statement Is Unchanged

Nothing in this fix alters the falsification logic. The admissible window
[0.22°, 0.38°], the forbidden gap [0.29°–0.31°], and the two canonical
prediction peaks at 0.273° and 0.331° are identical before and after the fix.

The LiteBIRD falsification criterion remains:

> If LiteBIRD measures β outside [0.22°, 0.38°], the framework is falsified.  
> If LiteBIRD measures β inside the gap (0.29°, 0.31°), the framework is falsified.  
> If LiteBIRD measures β ≈ 0.273°, the (5,6) shadow sector is selected.  
> If LiteBIRD measures β ≈ 0.331°, the (5,7) primary sector is confirmed.

Both surviving outcomes are framework-consistent. The sector identity matters
for the interpretation of Standard Model parameters — k_CS = 74 vs k_CS = 61
carries consequences for the Chern-Simons level and the downstream QCD/EW
coupling derivations. But the falsification outcome — PASS or FAIL — is the
same either way.

---

## What This Sprint Demonstrates

This fix is an example of what rigorous AI-assisted research looks like when
it's working correctly. The error was not in a numerical computation. It was
in a labelling convention that had been inconsistent since the modules were
first written. It took a careful cross-reading of the module constants, their
comments, the scenarios dictionary, and the test suite — simultaneously — to
identify that the names and the physics were inverted across four distinct
layers.

No single automated check would have caught this. The tests passed because they
were consistent with the wrong labelling. The numbers were right so no numerical
assertion failed. It required a human asking "what still needs to be done after
this PR is merged?" and an AI doing a complete audit of every file that touched
these constants.

That is the HILS loop working. Human direction, AI thoroughness, zero failures.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
