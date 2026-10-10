# AZ Formal Verification Library — Product 38

**Folder:** `12-AZ-IP/38-az-formal-verification-library/`
**Version:** 1.1.0
**TRL:** TRL-4 (generic library, now a runnable HTTP endpoint; worked example reproduces canonical results exactly)
**Status:** Active — Phases 1-2 of article-354's "Z3 checker -> formal-verification-as-a-service" roadmap

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
results bit-for-bit), now reachable over HTTP as a minimal
"formal-verification-as-a-service" endpoint for the Pentad worked example
specifically (Phase 2). Defining *new* safety properties still requires
Python code — a Z3 solver callable cannot be safely built from untrusted
HTTP query parameters, so the live service only runs the one trusted
example this product ships. z3-solver is an optional dependency;
`Z3_AVAILABLE`/`require_z3()` let callers detect its absence instead of
crashing at import time; the web endpoints return HTTP 503 if z3-solver
is unavailable at serve time.

## Usage

```bash
python 12-AZ-IP/38-az-formal-verification-library/run.py
```

## Running as a web product

```bash
python 12-AZ-IP/38-az-formal-verification-library/run.py --serve --port 8138
```

Then visit `http://127.0.0.1:8138/` for the checker dashboard, or query
the JSON API directly:

- `GET /api/status` — product metadata, Z3 availability, property names
- `GET /api/pentad-properties` — list the four Pentad safety properties
- `GET /api/pentad-suite` — run all four and summarize pass/fail
- `GET /api/pentad-check?name=` — run one named property

## Tests

```bash
python -m pytest 12-AZ-IP/38-az-formal-verification-library/tests -q
```

## Sources

- `src/core/z3_pentad_checker.py` — the four canonical Pentad checks being generalized
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #11

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
