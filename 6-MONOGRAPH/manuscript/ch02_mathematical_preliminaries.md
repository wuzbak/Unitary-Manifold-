# Chapter 2: Mathematical Preliminaries

## Tensors

Tensors are mathematical objects that generalize scalars, vectors, and matrices. They are crucial in many fields such as physics and engineering, particularly in the context of continuum mechanics and general relativity. Below is a brief overview of some fundamental aspects of tensors:

### Definition
A tensor is defined as a multi-linear map that takes a set of vectors and covectors and produces a scalar. Tensors can be classified into different types based on their rank:

- **Scalar (Rank 0 Tensor):** A single number is a tensor of rank 0.
- **Vector (Rank 1 Tensor):** A one-dimensional array of numbers, which can represent points, directions, or velocities in a space.
- **Matrix (Rank 2 Tensor):** A two-dimensional array which can be used to represent linear transformations or relations between two vector spaces.

### Tensor Notation
Tensors can be represented using index notation.

- A tensor of rank 2 can be denoted as T^i_j, where i indexes the rows and j indexes the columns.
- The transformation property of tensors under a change of basis can be expressed as T'^i_j = A^i_k B^l_j T^k_l, where A and B are the transformation matrices.

## Differential Geometry

Differential geometry is the field that uses the techniques of calculus and linear algebra to study problems in geometry. It provides the mathematical framework of geometry for curves, surfaces, and more complex structures called manifolds.

### Manifolds
A manifold is a topological space that resembles Euclidean space near each point. Here are some key concepts:

- **Differentiable Manifolds:** A manifold that is also a smooth space, allowing differentiation of functions.
- **Tangent Space:** At each point on a manifold, there exists a tangent space, which is a vector space that consists of the tangent vectors at that point.

### Curvature
Curvature is a measure of how much a geometric object deviates from being flat. Two types of curvature often studied are:

- **Gaussian Curvature:** The product of the principal curvatures of a surface.
- **Riemannian Curvature:** Describes how a manifold is curved in relation to its tangent spaces.

## Summary

This chapter has provided an overview of key concepts in tensors and differential geometry, setting a foundation for further exploration into the applications of these mathematical structures in physics and engineering.

---

## Kaluza–Klein Reduction and the Derivation of α

### Setup

The Unitary Manifold embeds the irreversibility field $B_\mu$ in a 5-dimensional metric $G_{AB}$ via the ansatz:

$$G_{AB} = \begin{pmatrix} g_{\mu\nu} + \lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & \phi^2 \end{pmatrix}$$

where $\phi$ is the **radion** scalar encoding the compactification radius $L_5 = \phi\,\ell_P$.

### The cross-block Riemann term

The 5D Riemann tensor $\mathcal{R}^A{}_{BCD}$ decomposes into three classes under the $4+1$ split:

- **4D block**: $\mathcal{R}^\rho{}_{\sigma\mu\nu}$ for $\rho,\sigma,\mu,\nu \in \{0,1,2,3\}$ — standard 4D curvature
- **Cross-block**: $\mathcal{R}^\mu{}_{5\nu 5}$ for $\mu,\nu \in \{0,1,2,3\}$ — mixing between 4D and compact dimension
- **Compact block**: $\mathcal{R}^5{}_{55 5}$ — pure compact curvature (vanishes for $\partial_5 G_{AB} = 0$)

The cross-block terms are the key new element of the non-truncated KK reduction. After integrating over the fifth dimension:

$$\int_0^{2\pi L_5} dy\; \mathcal{R}^\mu{}_{5\nu 5}\, G^{55} \;\longrightarrow\; \alpha\,\ell_P^2\,R\,H_{\mu\nu}H^{\mu\nu}$$

with coefficient:

$$\alpha \;=\; \left(\frac{\ell_P}{L_5}\right)^2 \;=\; \frac{1}{\phi_0^2}$$

### Why α was previously treated as free

Earlier derivations truncated the KK expansion at the Maxwell-like $H^2$ term and did not evaluate the cross-block Riemann components at the stabilised background $\phi = \phi_0$. At this background $G_{55} = \phi_0^2$ is a constant, and the cross-block contribution is non-zero and computable.

### The closure chain

The three completion requirements of the theory form an internally closed system:

1. **φ stabilisation** (Requirement 1): the equation $\beta\,\Box\phi = \tfrac{1}{2}\phi^{-1/2}R + \tfrac{1}{4}\phi^{-2}H^2$ is solved by the FTUM fixed point, giving $\phi_0$.
2. **Bμ geometric link** (Requirement 2): $\text{Im}(S_\text{eff}) = \int B_\mu J^\mu_\text{inf}\,d^4x$ is a path-integral theorem.
3. **α = φ₀⁻²** (Requirement 3): the cross-block Riemann identity, closed by the $\phi_0$ from Requirement 1.

The theory is therefore **self-complete**: no external parameters are required for the geometric sector.

### Numerical verification

The function `extract_alpha_from_curvature(g, B, phi, dx, lam)` in `src/core/metric.py` computes this numerically by:
1. Assembling the 5D metric $G_{AB}$ from $(g_{\mu\nu}, B_\mu, \phi)$.
2. Computing Christoffel symbols and the full 5D Riemann tensor.
3. Extracting the cross-block slice `Riem5[:, :4, 4, :4, 4]`.
4. Returning `alpha_geometric = mean(1/phi²)` — the KK-derived coupling.

Verified by 11 unit tests in `tests/test_metric.py`.
---

## Repository Context

This chapter is the foundational mathematical primer for the Unitary Manifold framework. As of **v9.29** the framework has expanded to **101 pillars** covering cosmology, particle physics, geometry, consciousness, governance, and the HILS co-emergence framework. The material in this chapter underpins Pillars 1–5 (the core KK geometry, field evolution, holography, and the FTUM fixed-point theorem).

For the complete picture, see:
- [`README.md`](../README.md) — full project overview
- [`omega/README.md`](../omega/README.md) — Pillar Ω: all 101 pillars in a single calculator
- [`AGENTS.md`](../AGENTS.md) — preferred ingest order for AI agents

*Chapter 2 — v9.29 — May 2026*  
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
