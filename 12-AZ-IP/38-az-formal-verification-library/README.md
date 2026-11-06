# AZ Formal Verification Library — Product 38

**Folder:** `12-AZ-IP/38-az-formal-verification-library/`
**Version:** 1.2.0
**TRL:** TRL-4 (generic library, now a runnable HTTP endpoint; worked example reproduces canonical results exactly)
**Status:** Active — trusted library examples and bounded declarative JSON service

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
"formal-verification-as-a-service" endpoint. Custom Python solver callables
remain a trusted library interface, not an HTTP input. New user-authored
properties can instead use bounded declarative JSON through
`POST /api/property-check` or `run.py --property-json FILE`. The format
supports finite bounded integer/real variables, arithmetic expressions and
logical constraints, not executable Python. Requests are capped at 64 KiB;
the checker limits variables (16), constraints (32), expression nodes (128),
depth (16), and solver time (2 seconds). Unknown solver outcomes are failures,
not proofs. z3-solver is an optional dependency;
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
- `POST /api/property-check` — check a bounded JSON property (no query parameters)

A minimal custom property is:

```json
{
  "name": "bounded-example",
  "description": "Find a bounded value at least five.",
  "variables": {"x": {"sort": "real", "min": 0, "max": 10}},
  "constraints": [{"op": "ge", "left": {"var": "x"}, "right": {"const": 5}}],
  "expected": "sat"
}
```

`PASS` means only that the declared constraints returned the expected solver
outcome; it does not validate their correspondence to an external system.
Recovered HTTP coverage is reconstructed in `tests/test_server.py`, rather
than claimed as a byte-for-byte recovery of the missing original file.

## Tests

```bash
python -m pytest 12-AZ-IP/38-az-formal-verification-library/tests -q
```

## Sources

- `src/core/z3_pentad_checker.py` — the four canonical Pentad checks being generalized
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #11

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
