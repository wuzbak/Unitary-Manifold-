# The Machinery of Honesty — AxiomZero Guard, MAS Waves, and How We Built a Self-Auditing Physics Framework

*Post 143 of the Unitary Manifold series.*  
*Epistemic category: **A** — methodology and code architecture. No new physics claims.*  
*v10.42, May 2026.*

---

There is a category of problem in theoretical physics that nobody talks about in papers: the circular derivation that neither the author nor the reviewers caught.

It happens quietly. A research codebase grows. A helper function that once computed something purely from geometry now, after a refactor, imports a constants file. That constants file was updated with measured PDG values. The derivation that was supposed to be forward-chain now silently reads the answer it was supposed to derive. The agreement is exact — not because the theory is right, but because the answer was put in.

The Unitary Manifold is a framework that claims to *derive* Standard Model parameters from geometry. That claim is only meaningful if circularity is provably absent. Prose cannot guarantee that. A test suite can.

This post explains the machinery we built to make circularity impossible — and the broader philosophy behind it.

---

## The AxiomZero Guard

`src/core/axiomzero_guard.py`

The AxiomZero Guard performs static analysis on every module in the derivation path. At **import time** — not at test time, not on demand — it scans a defined list of derivation-chain source files for any occurrence of forbidden Standard Model seed identifiers.

The forbidden list includes identifiers like `G_FERMI`, `SIN2_THETA_W_PDG`, `WEINBERG_ANGLE_PDG`, `G_F_MEASURED` — the measured values that the framework is supposed to *output*, not *input*. If any of these strings appear in a derivation file in a structural (non-comment, non-test, non-comparison) context, the guard raises an `ImportError`. The module will not load. The CI run will not pass. The merge will not happen.

This is not a linter warning. This is a hard block.

**Why make it an import-time error rather than a test?**

Because a test can be skipped. A test can be marked `xfail`. A test can be ignored when you are in a hurry. An `ImportError` at the top of the module cannot be skipped — if it fires, the entire codebase is non-functional and nothing runs until the violation is resolved. The guard is structurally self-enforcing.

**The allowlist system** handles cases where a measured value appears in a derivation file for legitimate reasons: as a comment, inside a comparison assertion, in a test block, or in a docstring. These are detected by scanning the line for allowlist markers (`#`, `comparison`, `assert`, `test`, `print(`, triple-quote strings). An allowlisted match does not block import, but it also triggers a reclassification — the output of any module using an allowlisted measured value cannot be labeled DERIVED, only CONSISTENCY_CHECK.

**v10.4 audit result: 0 violations across 19 derivation files.** This result required auditing hundreds of import statements across a codebase built over two years, and refactoring several modules where the guard found unannotated dependencies during development. The 0-violation status is not the starting condition; it is the condition after corrections.

**The fine structure constant edge case** is worth explaining explicitly, because it illustrates the precision required. The framework uses `ALPHA_EM_CANONICAL = 1/137.036` in several modules. This looks like an SM input — α is measured. But in the Unitary Manifold, α is a *derived* quantity (Pillar 56: α = φ₀⁻² from the FTUM fixed point). The canonical value is the framework's own prediction, not a seed. The guard tracks this explicitly: `ALPHA_EM_DERIVED = 1/137.036` is classified as AxiomZero-compliant, while `ALPHA_EM_PDG` would be flagged. The distinction is in the variable name, and the guard enforces it.

---

## The MAS Wave System

**MAS: Manifold Audit Synthesis.** (In earlier posts and documentation, this was sometimes also called Milestone Acceleration Sprint — the initialism survived as MAS became the proper name for the programme.)

The MAS programme was the answer to a planning problem: with 28 Standard Model parameters to close and an unknown number of geometric tools still to be built, how do you decide what to work on next?

The answer cannot be "whatever feels interesting" — that produces a research record that is difficult to audit and prone to motivated progress. It cannot be "whatever a journal reviewer would most notice" — that is a bias toward cosmetically appealing results at the expense of honest gaps.

The MAS system structures every cycle of work into a **wave**: a bounded, pre-declared unit with:

- A defined set of target parameters (P-numbers from the 28-parameter ledger)
- A defined promotion gate for each target (specific residual threshold required)
- A defined set of geometric tools allowed (which pillar dimensions, which correction levels)
- A defined test requirement (how many passing gate tests certify the closure)
- An explicit record of what the wave delivered and what it did not

The tracker lives at `docs/mas_tracker.yml`. It is version-controlled, 2,000+ entries long, and contains the full record of every wave from W0 to W14 — including the waves that delivered nothing, including the parameters that failed their gates, including the demotions.

**The demotion system** is important enough to name explicitly. P17 (atmospheric neutrino mass splitting Δm²₃₁) was promoted to an estimate in an early wave, then demoted when a computation error was found. The tracker records the demotion with the specific error identified and the wave number. This is not embarrassing — it is the system working as intended. A framework that only records promotions is not a scientific ledger; it is a marketing document.

**Waves that appeared to fail delivered infrastructure.** The braid c_L spectrum arc (around v10.6) closed zero parameters directly. But the c_L closure it produced was the blocking dependency for the Tier-4 Yukawa sprint (v10.28), which promoted five parameters simultaneously and produced the single largest score jump in the project's history (+1.7 points). The MAS tracker allows us to trace that lineage: wave X appears to fail → wave Y succeeds by using what wave X built.

**Wave structure forces honest accounting.** Because each wave pre-declares its targets and gates, it is not possible to silently swap targets after the fact. If a wave targeted P3 and P3 did not pass its gate, the record shows a miss — not a redefinition of success.

Fourteen waves. Several complete misses. Two error-triggered demotions. Total score trajectory: 42% → 99.3%. That is what honest accounting looks like in a living research record.

---

## The Five-Tier Execution Framework

`src/core/five_tier_execution_framework.py`

After the MAS programme completed (formally closed at v10.14), future work needed a different operating structure. The five-tier framework defines a priority ordering for all post-MAS dimensional-extension work:

- **Tier 1**: Parameters with architecture limits and known closing mechanisms
- **Tier 2**: Parameters with strong-but-unfinished evidence chains
- **Tier 3–5**: Progressively more speculative or longer-horizon work

The framework encodes the current operating model as machine-readable dictionaries: which parameters are being targeted, which geometric tools are in scope, and what the pass/fail gate for each tier looks like. The version string (`FRAMEWORK_VERSION = "v10.42"`) is updated with every wave and tested automatically.

This makes the framework's current state queryable. `framework_summary()` returns a structured dictionary of all active tier packages. A test fails if the summary format drifts from specification. The framework is not documentation — it is running code.

---

## The Hardgate Certification System

Every parameter promotion at GEOMETRIC_PREDICTION or above requires a corresponding `p{N}_*_derived_cert.py` file in `src/core/`. These certification modules are not documentation — they are executable gate reports that verify three conditions:

1. **Residual gate**: the computed value falls within 5% of the PDG measurement
2. **AxiomZero purity gate**: the derivation imports zero forbidden SM seeds (enforced by a call to the AxiomZero Guard)
3. **Uniqueness gate**: no undocumented free parameter was adjusted to reach the result

A test in `tests/` calls each certification module and asserts all three conditions pass. If someone edits the underlying derivation in a way that changes the residual above 5%, the certification test fails. The scorecard cannot be promoted silently.

This architecture means the ToE score is not just a number in a markdown file. It is a number that 27,000+ tests defend. Every point on the scoreboard is backed by code that will fail if the point is no longer warranted.

---

## The Archived Hypotheses Pattern

`docs/archived_hypotheses/`

Every hypothesis that was audited and rejected gets its own file. The DAM lattice hypothesis (Pillar 207) proposed that K_CS = 74 might arise from a 1/24 fractional substructure. The audit rejected it: K_CS = 74 is algebraically exact from the braid theorem. The rejection file records the original motivation, the specific algebraic check that refuted it, and a note that the hypothesis is closed and should not be reopened without new evidence.

This pattern exists for a specific reason: future researchers should not redo work that has already been done and documented. Future AI systems reading this repository should not re-propose the 1/24 hypothesis without first reading why it was rejected. The archived hypotheses directory is a scientific dead-letter office — properly labeled, available for inspection, and sealed.

---

## The Zero-Failure Baseline

The hard operational rule: **zero test failures before any merge, at any time.**

This sounds obvious. It is not, in practice, the standard in research codebases. The moment you accept "a few known failures," you lose the ability to distinguish regressions from pre-existing problems. The zero-failure baseline means every new failure is immediately visible and immediately the highest-priority issue.

The baseline has caused delays. It has also caught two genuine errors that would have silently corrupted published predictions. The cost of discipline paid off.

---

## What This Architecture Means

There are two ways to protect a "derived from first principles" claim.

The first way: write the claim in a paper, trust that reviewers will check the math, rely on the community to catch circular reasoning over years or decades.

The second way: encode the protection in the codebase, run it on every commit, make it structurally impossible to merge a violation.

The Unitary Manifold uses the second approach. Not because the first approach is wrong — it is how physics has worked for a century — but because the second approach provides a level of continuous, verifiable assurance that prose cannot match.

The AxiomZero Guard runs on every pull request. The hardgate certifications run on every commit. The MAS tracker records every promotion and demotion with full provenance. The archived hypotheses preserve the scientific dead ends for the benefit of whoever comes next.

This is what a self-auditing framework looks like. The AI enforces the rules automatically. The human decides which rules matter scientifically. The experiments decide who was right.

---

## What to Check, What to Break

- **Run the guard yourself**: clone the repository and import `axiomzero_guard`. It will report 0 violations. If it reports one, that is the most important bug in the repository — open a GitHub issue immediately.
- **Read the MAS tracker**: `docs/mas_tracker.yml` — find a wave that missed its gates, read the reason, verify the tracker's account is honest.
- **Check the hardgate certs**: `src/core/p{N}_*_derived_cert.py` — run one. Verify the residual and the AxiomZero check.
- **Archived hypotheses**: read `docs/archived_hypotheses/pillar207_dam_leech_rejected.md`. If you find a flaw in the rejection — a way to rescue the 1/24 hypothesis — open a GitHub issue.
- **Full test suite**: `python -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q` — ~27,076 passed, 0 failed.
- Repository: https://github.com/wuzbak/Unitary-Manifold-

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
