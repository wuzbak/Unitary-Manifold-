# Monograph Structure

The full monograph *The Unitary Manifold* (v9.0, Academic Edition) is included in the repository as [`THEBOOKV9a (1).pdf`](../THEBOOKV9a%20(1).pdf). It spans **74 chapters** organised into **XXIII parts**.

---

## High-Level Part Structure

| Parts | Chapters | Theme |
|-------|----------|-------|
| I–II | 1–2 | Motivation & Mathematical Preliminaries |
| III–VI | 3–6 | 5D Metric Construction & Dimensional Reduction |
| VII–IX | 7–9 | Walker–Pearson Field Equations |
| X–XIV | 10–30 | Entropy Geometry, Information Currents & Holographic Screens |
| XV–XIX | 31–48 | Quantum Information, Transition Asymmetry & Entanglement Capacity |
| XX–XXI | 49–55 | Irreversible Friedmann Equations & Holographic Fate |
| XXII | 56–62 | Multiverse Topology & Inter-Manifold Information Flow |
| XXIII | 63–74 | Observers, Mind & Co-emergence of Classical Reality |

---

## Chapter Highlights

### Foundational (Chapters 1–9)

| Chapter | Title / Topic |
|---------|--------------|
| 1 | Motivation: dimensional misalignment in modern physics |
| 2 | Mathematical Preliminaries: tensors, differential geometry, manifolds |
| 3 | The 5D Metric Ansatz (Kaluza–Klein) |
| 4 | Assembling $G_{AB}$: off-diagonal embedding of $B_\mu$ |
| 5 | Dimensional Reduction of the 5D Einstein–Hilbert Action |
| 6 | The 4D Effective Action and Its Symmetries |
| 7 | Deriving the Walker–Pearson Field Equations |
| 8 | The Irreversibility Field Equation and $H_{\mu\nu}$ |
| 9 | The Scalar Equation and Nonminimal Coupling |

### Core Theory (Chapters 10–48)

| Chapters | Topic |
|----------|-------|
| 10–14 | Entropy geometry and the information metric |
| 15–20 | Conserved information current $J^\mu_{\rm inf}$ and its physical content |
| 21–25 | Holographic screens: entropy-area law and boundary projection |
| 26–30 | Gaussian curvature of entropy landscapes |
| 31–36 | Quantum transition asymmetry from $B_\mu$ |
| 37–42 | Entanglement capacity scalar $\phi$ and quantum information flow |
| 43–48 | Arrow of time as a gauge phenomenon |

### Cosmology (Chapters 49–55)

| Chapters | Topic |
|----------|-------|
| 49–51 | Irreversible Friedmann equations (modified Hubble expansion) |
| 52–53 | Holographic fate of the universe: entropy saturation |
| 54–55 | Dark energy as a geometric effect of $B_\mu$ |

### Multiverse (Chapters 56–62)

| Chapters | Topic |
|----------|-------|
| 56–58 | Multiverse topology: inter-manifold information channels |
| 59–60 | The UEUM geodesic equation |
| 61 | The Final Theorem of the Unitary Manifold (FTUM) |
| 62 | Numerical evidence for the fixed point |

### Observers and Mind (Chapters 63–74)

| Chapters | Topic |
|----------|-------|
| 63–65 | The observer as a boundary condition |
| 66–68 | Co-emergence of classical reality from holographic projection |
| 69–71 | Consciousness and the irreversibility field |
| 72–74 | Open questions and future directions |

---

## Related Source Files

The numerical implementations in `src/` correspond directly to key chapters:

| Source file | Monograph chapters |
|-------------|-------------------|
| `src/core/metric.py` | 3–6 |
| `src/core/evolution.py` | 7–9, Appendix D |
| `src/holography/boundary.py` | 21–25, 49–55 |
| `src/multiverse/fixed_point.py` | 56–62 |

---

## Manuscript Sources

The LaTeX source for the arXiv submission is in [`arxiv/main.tex`](../arxiv/main.tex) with bibliography in [`arxiv/references.bib`](../arxiv/references.bib).

Chapter 2 is also available as standalone Markdown in [`manuscript/ch02_mathematical_preliminaries.md`](../manuscript/ch02_mathematical_preliminaries.md).
