# Contributing

Thank you for your interest in contributing to the Unitary Manifold project. Contributions of all kinds are welcome — mathematical review, code improvements, documentation, and independent verification.

---

## Ways to Contribute

### Mathematical Verification

The most valuable contributions are rigorous checks of the theoretical framework:

- **Verify proofs:** Check the derivations in the Walker–Pearson field equations (Chapters 7–9).
- **Check dimensional reduction:** Confirm that the 5D Einstein–Hilbert action correctly reduces to the 4D effective action.
- **Braided winding:** Verify the $(5, 7)$ braided-winding resolution and the resonance identity $k_\text{CS} = 5^2 + 7^2 = 74$.
- **Conserved currents:** Verify that $\nabla_\mu J^\mu_{\rm inf} = 0$ follows from the field equations.
- **FTUM:** Provide a formal proof or counterexample for the fixed-point theorem.
- **Completeness theorem:** Verify that all 7 independent constraints converge to $k_\text{CS} = 74$ (see `src/core/completeness_theorem.py`).

See the [AI & Automated Review Invitation](../discussions/AI-Automated-Review-Invitation.md) for a structured checklist of verification tasks.

### Code Contributions

Improvements to the numerical implementation are welcome. Areas of particular interest:

- **CMB amplitude:** The power spectrum amplitude is suppressed ×4–7 at acoustic peaks (see `FALLIBILITY.md §IV.9`) — any progress on resolving this is valuable.
- **φ₀ self-consistency:** The full FTUM self-consistency loop (φ₀ → α → nₛ → back to φ₀) needs verification; see `src/core/phi0_closure.py`.
- **3D/full 4D spatial grid** support (current evolution code is 1D).
- **Staggered-grid discretisation** for the gauge field $B_\mu$.
- **Visualisation utilities** for field evolution and entropy diagnostics.
- **New falsifiable pillar extensions** following the existing pillar pattern.

### Documentation

- Expand the [Mathematical Framework](Mathematical-Framework) wiki page with more derivation detail.
- Add worked examples to the [Getting Started](Getting-Started) page.
- Improve docstrings in the source code.

---

## Development Workflow

1. **Fork** the repository on GitHub.
2. **Create a branch** for your change: `git checkout -b feature/my-improvement`
3. **Run the test suite before making changes** to establish a baseline:
   ```bash
   python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" omega/ -q
   # Expected: 18057 passed, 329 skipped, 11 deselected, 0 failed
   ```
4. **Make your changes** following the conventions below.
5. **Run the test suite again** after your changes; 0 failures is a hard requirement.
6. **Open a Pull Request** with a clear description of what you changed and why.

---

## Test Suite Reference

```bash
# Fast suite — core physics:
python -m pytest tests/ -q
# Expected: ~15926 passed, 76 skipped, 11 deselected, 0 failed

# Recycling / φ-debt entropy (Pillar 16):
python -m pytest recycling/ -q
# Expected: 316 passed, 0 failed

# Unitary Pentad governance (18 modules):
python3 -m pytest "5-GOVERNANCE/Unitary Pentad/" -q
# Expected: 1026 passed, 254 skipped, 0 failed

# Full repository (~130 s):
python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" omega/ -q
# Expected: 18057 passed, 329 skipped, 11 deselected, 0 failed

# Slow tests (Richardson extrapolation convergence):
python -m pytest tests/ -m slow
```

> **Skip note:** 330 tests use conditional `pytest.skip()` guards — 76 dual-use stubs (cold fusion / lattice dynamics) and 254 Pentad product stubs. See `DUAL_USE_NOTICE.md` and `PENTAD_PRODUCT_NOTICE.md`.
> **Slow note:** 11 tests in `test_richardson_multitime.py` are marked `@pytest.mark.slow` and deselected by default. Run explicitly with `-m slow`.

---

## Code Conventions

- **Python 3.12+**, NumPy/SciPy only (no deep learning frameworks in core).
- All physical quantities in **natural units** (Planck units unless otherwise noted).
- Public functions must have a NumPy-style docstring with `Parameters`, `Returns`, and a one-line summary.
- Array shapes must be documented in the docstring (e.g., `ndarray (N, 4, 4)`).
- Constants live at **module top level in `ALL_CAPS`**; derived quantities in `__init__`.
- Every new module must have a corresponding test file in `tests/`.
- Avoid introducing new dependencies unless strictly necessary; prefer NumPy/SciPy.
- Keep changes focused — one logical change per pull request.

---

## Citing This Work

If you use the Unitary Manifold framework in your research, please cite it using the metadata in [`CITATION.cff`](../CITATION.cff):

```bibtex
@article{walker-pearson2026unitary,
  author    = {Walker-Pearson, ThomasCory},
  title     = {The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility},
  year      = {2026},
  version   = {9.14},
  doi       = {10.5281/zenodo.19584531},
  url       = {https://github.com/wuzbak/Unitary-Manifold-},
}
```

---

## Review and Discussion

For mathematical peer review and automated verification, see the discussion thread:
[`discussions/AI-Automated-Review-Invitation.md`](../discussions/AI-Automated-Review-Invitation.md)

For technical questions or suggestions, open an [Issue](https://github.com/wuzbak/Unitary-Manifold-/issues) on GitHub.

---

## Authorship Standard

Every substantive document must end with:

> *Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
> *Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## License

All contributions are accepted under the **Defensive Public Commons License v1.0 (2026)**:

- Contributions become part of the public domain.
- No exclusive commercial patents may be filed on the core equations.
- Attribution is requested but not legally required.
