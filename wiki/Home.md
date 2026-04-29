# Unitary Manifold — Wiki Home

> *"Collapse entropy early. Gate compute. Enforce structure. Reduce variance."*

Welcome to the **Unitary Manifold** project wiki. This wiki documents the theory, code, and usage of the Unitary Manifold (UM) framework — a five-dimensional gauge-geometric approach that geometrises thermodynamic irreversibility and information flow.

**Current version:** 9.23 · **92 pillars closed** · **14,183 tests passing · 0 failures**

---

## What Is the Unitary Manifold?

The Unitary Manifold is a 5-dimensional Kaluza–Klein framework in which:

- **Thermodynamic irreversibility** is encoded as a gauge field $B_\mu$ living in the extra fifth dimension.
- **Quantum information flow** is carried by a nonminimally coupled scalar $\phi$ (entanglement-capacity / radion).
- **4D effective physics** — including the Walker–Pearson field equations — emerges from dimensional reduction of a 5D Einstein–Hilbert action.

The core claim is that the **Second Law of Thermodynamics is a geometric identity**, not a statistical postulate.

---

## Key Predictions

| Observable | UM Prediction | Observation |
|-----------|--------------|-------------|
| CMB spectral index $n_s$ | 0.9635 | Planck 2018: 0.9649 ± 0.0042 ✅ |
| Tensor-to-scalar ratio $r$ | 0.0315 (braided) | BICEP/Keck: $r < 0.036$ ✅ |
| Cosmic birefringence $\beta$ | 0.3513° | Komatsu et al. 2022: ≈ 0.35° ± 0.14° ✅ |
| Nonminimal coupling $\alpha$ | $\phi_0^{-2}$ (derived, not fitted) | — |
| Chern–Simons level $k_\text{CS}$ | 74 = $5^2 + 7^2$ | selected by birefringence data |

The braided (5, 7) winding resolution — using $k_\text{CS} = 74$ — simultaneously satisfies all three CMB constraints without new free parameters. See [`src/core/braided_winding.py`](../src/core/braided_winding.py).

**Primary falsifier:** LiteBIRD birefringence measurement (~2032). Any $\beta$ inconsistent with 0.3513° would falsify the braided-winding mechanism.

---

## Wiki Contents

| Page | Description |
|------|-------------|
| [Getting Started](Getting-Started) | Install dependencies and run your first simulation |
| [Mathematical Framework](Mathematical-Framework) | 5D metric ansatz, key fields, core equations, and braided winding |
| [Field Equations](Field-Equations) | Walker–Pearson equations: derivation and structure |
| [Numerical Methods](Numerical-Methods) | Discretisation pipeline, stability, and recommended settings |
| [API Reference](API-Reference) | Public API for all Python source modules (92 pillars) |
| [Monograph Structure](Monograph-Structure) | Chapter map of the full 74-chapter monograph |
| [Contributing](Contributing) | How to contribute, review, and cite this work |

---

## Quick Links

- **Source code:** [`src/`](../src/)
- **Full monograph:** [`THEBOOKV9a (1).pdf`](../THEBOOKV9a%20(1).pdf)
- **Plain-language summary:** [`WHAT_THIS_MEANS.md`](../WHAT_THIS_MEANS.md)
- **Honest limitations:** [`FALLIBILITY.md`](../FALLIBILITY.md)
- **Unification proof:** [`UNIFICATION_PROOF.md`](../UNIFICATION_PROOF.md)
- **Quantum theorems:** [`QUANTUM_THEOREMS.md`](../QUANTUM_THEOREMS.md)
- **Citation:** [`CITATION.cff`](../CITATION.cff)

---

## Citation

```
Walker-Pearson, ThomasCory (2026).
"The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility."
Version 9.23. https://github.com/wuzbak/Unitary-Manifold-
DOI: 10.5281/zenodo.19584531
```

---

## Authorship

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## License

This work is irrevocably dedicated to the **public domain** under the Defensive Public Commons License v1.0 (2026). All persons have the perpetual, royalty-free right to study, reproduce, and modify this work. Exclusive commercial patenting of the core equations is strictly prohibited.
