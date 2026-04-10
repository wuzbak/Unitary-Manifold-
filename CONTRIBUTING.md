# Contributing to the Unitary Manifold

Thank you for looking at this work.  All contributions — corrections, numerical
verifications, extensions, and discussions — are welcome.

---

## 1 · How to run the code locally

```bash
git clone https://github.com/wuzbak/Unitary-Manifold-
cd Unitary-Manifold-
pip install -r requirements.txt pytest
python -m pytest tests/ -v          # 98 tests; all should pass
```

The test suite covers:

| Module | Tests |
|--------|-------|
| `src/core/metric.py` | KK ansatz, field strength, Christoffel, Riemann, Ricci |
| `src/core/evolution.py` | RK4 integrator, Euler baseline, CFL estimate, physics bounds |
| `src/holography/boundary.py` | Entropy-area law, boundary evolution, conservation |
| `src/multiverse/fixed_point.py` | FTUM convergence, second law, holographic bound |

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
Attribution to *ThomasCory Walker-Pearson* is requested but not required.

---

*Questions? Open a GitHub Issue or Discussion.*
