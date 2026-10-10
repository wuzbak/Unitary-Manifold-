# AZ Formal Verification Library — Product 38

**Folder:** `12-AZ-IP/38-az-formal-verification-library/`
**Version:** 1.0.0
**TRL:** TRL-3 (generic library; worked example reproduces canonical results exactly)
**Status:** Active — Phase 1 of article-354's "Z3 checker -> formal-verification-as-a-service" roadmap

## What this is

`src/core/z3_pentad_checker.py` hard-codes four Pentad-specific Z3 checks.
This product factors out the shared shape — declare Z3 variables and
constraints, declare an expected sat/unsat outcome, run the solver,
interpret PASS/FAIL — into a reusable `SafetyProperty` /
`run_property()` / `run_suite()` API that any project can use to define
its own formally-checked safety properties without hand-rolling Z3
boilerplate.

`pentad_example.py` reproduces all four of the canonical Pentad checks
(`trust_stability`, `no_deadlock`, `cs_bound`, `xi_c_rational`) using only
the generic template, and the test suite verifies each one's PASS/FAIL
status matches `src/core/z3_pentad_checker.py`'s own output exactly.

## Epistemic status

This does not replace `src/core/z3_pentad_checker.py`, which remains the
canonical Pentad checker. This product is the generalized library plus a
faithfulness proof (the worked example matches the canonical checker's
results bit-for-bit). Turning this into an actual hosted
"formal-verification-as-a-service" endpoint (Phase 2) is out of scope.
z3-solver is an optional dependency; `Z3_AVAILABLE`/`require_z3()` let
callers detect its absence instead of crashing at import time.

## Usage

```bash
python 12-AZ-IP/38-az-formal-verification-library/run.py
```

## Tests

```bash
python -m pytest 12-AZ-IP/38-az-formal-verification-library/tests -q
```

## Sources

- `src/core/z3_pentad_checker.py` — the four canonical Pentad checks being generalized
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #11

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
