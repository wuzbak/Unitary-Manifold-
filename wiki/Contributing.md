# Contributing

Thank you for your interest in contributing to the Unitary Manifold project. Contributions of all kinds are welcome — mathematical review, code improvements, documentation, and independent verification.

---

## Ways to Contribute

### Mathematical Verification

The most valuable contributions are rigorous checks of the theoretical framework:

- **Verify proofs:** Check the derivations in the Walker–Pearson field equations (Chapters 7–9).
- **Check dimensional reduction:** Confirm that the 5D Einstein–Hilbert action correctly reduces to the 4D effective action.
- **Conserved currents:** Verify that $\nabla_\mu J^\mu_{\rm inf} = 0$ follows from the field equations.
- **FTUM:** Provide a formal proof or counterexample for the fixed-point theorem.

See the [AI & Automated Review Invitation](../discussions/AI-Automated-Review-Invitation.md) for a structured checklist of verification tasks.

### Code Contributions

Improvements to the numerical implementation are welcome. Areas of particular interest:

- **Higher-order time integrators** (RK4, symplectic integrators) for `src/core/evolution.py`
- **Staggered-grid discretisation** for the gauge field $B_\mu$
- **3D/full 4D spatial grid** support (current code is 1D)
- **Visualisation utilities** for field evolution and entropy diagnostics
- **Test suite** with unit tests for all public API functions

### Documentation

- Expand the [Mathematical Framework](Mathematical-Framework) wiki page with more derivation detail.
- Add worked examples to the [Getting Started](Getting-Started) page.
- Improve docstrings in the source code.

---

## Development Workflow

1. **Fork** the repository on GitHub.
2. **Create a branch** for your change: `git checkout -b feature/my-improvement`
3. **Make your changes** following the conventions below.
4. **Run the existing tests** (if any) and verify that the quickstart examples still work.
5. **Open a Pull Request** with a clear description of what you changed and why.

---

## Code Conventions

- Python 3.9+, NumPy style throughout.
- Public functions must have a NumPy-style docstring with `Parameters`, `Returns`, and a one-line summary.
- Array shapes must be documented in the docstring (e.g., `ndarray (N, 4, 4)`).
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
  version   = {9.0},
  url       = {https://github.com/wuzbak/Unitary-Manifold-},
}
```

---

## Review and Discussion

For mathematical peer review and automated verification, see the discussion thread:
[`discussions/AI-Automated-Review-Invitation.md`](../discussions/AI-Automated-Review-Invitation.md)

For technical questions or suggestions, open an [Issue](https://github.com/wuzbak/Unitary-Manifold-/issues) on GitHub.

---

## License

All contributions are accepted under the **Defensive Public Commons License v1.0 (2026)**:

- Contributions become part of the public domain.
- No exclusive commercial patents may be filed on the core equations.
- Attribution is requested but not legally required.
