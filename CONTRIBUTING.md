# Contributing to the Unitary Manifold

Thank you for looking at this work.  All contributions — corrections, numerical
verifications, extensions, and discussions — are welcome.

---

## 1 · How to run the code locally

```bash
git clone https://github.com/wuzbak/Unitary-Manifold-
cd Unitary-Manifold-
pip install -r requirements.txt pytest
python -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" omega/ -q
# Expected: 15023 passed, 2 skipped, 11 deselected, 0 failed
python -m pytest tests/ -q           # tests/ only: ~13059 passed, 2 skipped, 11 deselected
python -m pytest tests/ -m slow     # 11 slow tests (Richardson convergence)
```

The test suite covers:

| Module | Tests |
|--------|-------|
| `src/core/metric.py` | KK ansatz, field strength, Christoffel, Riemann, Ricci (30 tests) |
| `src/core/evolution.py` | RK4 integrator, Euler baseline, CFL estimate, physics bounds (49 tests) |
| `src/holography/boundary.py` | Entropy-area law, boundary evolution, conservation (21 tests) |
| `src/multiverse/fixed_point.py` | FTUM convergence, second law, holographic bound (35 tests) |
| `src/core/inflation.py` / `transfer.py` | CMB power spectrum, birefringence, triple constraint (271 tests) |
| `src/core/fiber_bundle.py` | Principal bundle topology, characteristic classes, anomaly cancellation (96 tests) |
| `tests/test_completions.py` | Completion and endpoint tests (72 tests) |
| `src/core/uniqueness.py` | Uniqueness theorems, ΛCDM no-go comparison (61 tests) |
| `src/core/derivation.py` (module) | Stage 0–3 symbolic constraint derivation (59 tests) |
| `src/core/boltzmann.py` | Baryon-loaded CMB transfer, Boltzmann H-theorem, entropy monotonicity (49 tests) |
| `src/core/diagnostics.py` | CMB diagnostics, chi2, observables, convergence (30 tests) |
| `tests/test_cosmological_predictions.py` | Hubble tension, muon g-2, dark matter curves, GW echoes (28 tests) |
| Convergence | O(dx²) gradient, Laplacian, Christoffel (10 tests) |
| Closure batch 1 | α dual-path, nₛ KK=Casimir, β coupling, holographic emergence (25 tests) |
| Closure batch 2 | Numerical robustness, cross-module consistency (31 tests) |
| Fuzzing | Edge cases, random inputs, adversarial numerics (20 tests) |
| Dimensional reduction | KK reduction identities (14 tests) |
| Discretization invariance | Grid-independence checks (13 tests) |
| Arrow of time | Entropy growth, deficit, path independence, rates (23 tests) |
| CMB landscape | χ² landscape, TB/EB cross-checks (17 tests) |
| End-to-end pipeline | Chain closure, CS level uniqueness, α loop (26 tests) |
| Observational resolution | nₛ/β/χ² tolerances, LiteBIRD bounds (30 tests) |
| Parallel validation | 5 independent theory claims, dual-branch, transfer physics (38 tests) |
| Quantum unification | BH info conservation, CCR, Hawking temperature, ER=EPR (26 tests) |
| Richardson (slow) | Second-order convergence rate in time step (11 tests) |
| Derivation integers | Key-integer derivations: k_cs=74, n_w=5/7, k_rc=12, φ_min=18 — geometry-forced (59 tests) |
| **Total (current)** | **Grand total: 15191 collected · 15023 passed · 2 skipped · 11 slow-deselected · 0 failed** (see README.md for full per-file breakdown) |

> **Skip note:** 1 test in `test_arrow_of_time.py` uses a conditional `pytest.skip()` guard that fires when `fixed_point_iteration` converges in fewer than 2 steps (immediate convergence = correct behaviour). This is not a failure.
> **Slow note:** 11 tests in `test_richardson_multitime.py` are marked `@pytest.mark.slow` and deselected by default via `pytest.ini`. Run with `pytest tests/ -m slow`.

---

## 2 · Ways to contribute

### Numerical verification
Run the test suite on your own machine and report the result (OS, Python version,
numpy version, pass/fail count) as a GitHub Issue.  This is genuinely useful —
independent reproduction of numerical results is a key part of scientific validation.

### Physics / mathematics review
Open an Issue titled `[Review] <topic>` if you find:
- An equation that doesn't match the monograph
- A test that is under-specified or trivially passed
- A physical constraint (e.g. Bianchi identity, energy condition) that should be
  checked but isn't

### Code improvements
Open a Pull Request for:
- New tests that probe physical laws not yet covered
- Numerical accuracy improvements (higher-order stencils, adaptive step size)
- Performance improvements (vectorisation, batched operations)
- Docstring or inline-comment clarifications

Please keep PRs focused — one logical change per PR makes review easier.

### Extending the theory
If you want to add a new physical module (e.g. gravitational wave extraction,
cosmological perturbation theory), open an Issue first to discuss scope and
interface before writing code.

---

## 3 · Code style

- Python 3.12, numpy-idiomatic
- Type hints on all public functions
- Docstrings follow NumPy docstring convention (`Parameters / Returns` sections)
- No new dependencies beyond `numpy` and `scipy` without discussion

---

## 4 · Reporting errors

If you find a **physics error** (wrong sign, wrong index contraction, violated
identity), please open an Issue with:
1. The file and function name
2. The expected behaviour (with equation reference from the monograph if possible)
3. The observed behaviour

Corrections are treated as the most valuable contributions — affirmations of
correct results are also always welcome.

---

## 5 · Attribution

This repository is released under the
**Defensive Public Commons License v1.0 (2026)** — effectively public domain.
You are free to fork, reproduce, and build on this work without restriction.
Attribution to *ThomasCory Walker-Pearson / AxiomZero Technologies* is requested but not required.

All source code, documentation, and sub-products in this repository (including the Unitary Pentad
governance framework) are original works of ThomasCory Walker-Pearson, produced under the
**AxiomZero Technologies** trade name (DBA commenced March 26, 2026, United States).  Copyright is
retained by ThomasCory Walker-Pearson; the DPC v1.0 and AGPL-3.0 licenses grant you broad
freedoms to use and build upon this work — they do not transfer ownership.

### Authorship roles

| Role | Person / Agent |
|------|---------------|
| Theory, framework, and scientific direction | **ThomasCory Walker-Pearson** |
| Code architecture, test suites, document engineering, and synthesis | **GitHub Copilot (AI)** |

AI-generated contributions (code, documentation, and test suites produced by GitHub Copilot)
are acknowledged in every `.py` source file via the SPDX header
`# Copyright (C) 2026  ThomasCory Walker-Pearson` and the two-line credit at the bottom
of every substantive document.  **AI contributions do not constitute co-authorship under
academic norms** — they are acknowledged in the same way that significant software tools
and infrastructure contributions are acknowledged, not as an equal intellectual contribution
to the scientific theory.  Pull requests that include AI-generated code or text should note
this in the PR description; they will be attributed using the same two-line standard.

---

## 6 · Developer Certificate of Origin (DCO)

By submitting a pull request or patch to this repository, you certify the following
**Developer Certificate of Origin** (version 1.1, https://developercertificate.org):

> *"I hereby certify that:*
> *(a) The contribution was created in whole or in part by me and I have the right to submit it
> under the open source licenses indicated in the file; or*
> *(b) The contribution is based upon previous work that, to the best of my knowledge, is covered
> under an appropriate open source license and I have the right under that license to submit that
> work with modifications, whether created in whole or in part by me, under the same open source
> license (unless I am permitted to submit under a different license), as indicated in the file; or*
> *(c) The contribution was provided directly to me by some other person who certified (a), (b) or
> (c) and I have not modified it.*
> *I understand and agree that this project and the contribution are public and that a record of the
> contribution (including all personal information I submit with it, including my sign-off) is
> maintained indefinitely and may be redistributed consistent with this project or the open source
> license(s) involved."*

**How to sign off:** Add a `Signed-off-by` line to every commit message:

```
git commit -s -m "Your commit message"
# produces: Signed-off-by: Your Name <your@email.example>
```

Pull requests without a `Signed-off-by` trailer on every commit may be asked to
rebase and add the sign-off before merging.

### Additional grant to copyright holder

By submitting a contribution, you additionally grant **ThomasCory Walker-Pearson**
a perpetual, worldwide, royalty-free, non-exclusive licence to use, reproduce, modify,
distribute, sub-license (including under commercial terms as described in
[`COMMERCIAL_TERMS.md`](COMMERCIAL_TERMS.md) § 4-A), and otherwise exploit your
contribution, for the purpose of operating and commercialising the Unitary Manifold
project in accordance with its open-core business model.

This additional grant does **not** restrict your own rights in your contribution; you
retain whatever rights you held before submitting.  The public's rights under DPC v1.0
and AGPL-3.0 are never diminished by this grant.

---

*Questions? Open a GitHub Issue or Discussion.*
