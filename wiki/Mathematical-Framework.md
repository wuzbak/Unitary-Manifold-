# Mathematical Framework

The Unitary Manifold rests on five foundational pillars plus an extended hierarchy of 69 derived pillars (74 total, now closed). This page documents the core mathematical structures shared across all pillars.

---

## 1. The 5D Kaluza–Klein Metric Ansatz

The irreversibility field $B_\mu$ is embedded as the off-diagonal component of a 5×5 parent metric $G_{AB}$:

$$G_{AB} = \begin{pmatrix} g_{\mu\nu} + \lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & \phi^2 \end{pmatrix}$$

so that $G_{\mu 5} = \lambda\phi B_\mu$ and $G_{55} = \phi^2$ (radion **not** fixed to unity — $\phi$ is a dynamical scalar).

### Key Fields

| Symbol | Name | Role |
|--------|------|------|
| $g_{\mu\nu}$ | 4D metric | spacetime geometry (signature −+++) |
| $B_\mu$ | Irreversibility field | gauge field encoding the arrow of time |
| $\phi$ | Entanglement-capacity scalar / radion | $G_{55} = \phi^2$; encodes compactification radius $L_5 = \phi\,\ell_P$ |
| $\lambda$ | Kaluza–Klein coupling | controls strength of $B$–gravity mixing |
| $\alpha$ | Nonminimal coupling | **derived**: $\alpha = \phi_0^{-2}$ (see §9) |

---

## 2. Field Strength Tensor

The antisymmetric field strength of the irreversibility gauge field is:

$$H_{\mu\nu} = \partial_\mu B_\nu - \partial_\nu B_\mu$$

This plays the role of an "electromagnetic" field strength for the arrow-of-time gauge field. Its contraction $H^2 = H_{\mu\nu}H^{\mu\nu}$ acts as a source of dissipation in the field equations.

---

## 3. 5D Einstein–Hilbert Action

The parent theory is governed by the action:

$$S_{\rm 5D} = \frac{1}{16\pi G_5} \int d^5x \sqrt{-G}\, \mathcal{R}_5 + S_{\rm matter}$$

where $\mathcal{R}_5$ is the 5D Ricci scalar and $G$ is the determinant of $G_{AB}$.

After dimensional reduction (integrating out the fifth dimension), the 4D effective action is:

$$S_{\rm 4D} = \int d^4x \sqrt{-g} \left[ \frac{R}{16\pi G_4} - \frac{\lambda^2}{4} H_{\mu\nu}H^{\mu\nu} + \frac{\alpha}{2} R \phi^2 - \frac{1}{2}(\partial\phi)^2 \right]$$

---

## 4. Curvature Hierarchy

Starting from the metric $g_{\mu\nu}$, the curvature hierarchy is computed as:

| Object | Formula | Shape |
|--------|---------|-------|
| Christoffel symbols | $\Gamma^\sigma_{\mu\nu} = \tfrac{1}{2}g^{\sigma\rho}(\partial_\mu g_{\nu\rho} + \partial_\nu g_{\mu\rho} - \partial_\rho g_{\mu\nu})$ | $(N, 4, 4, 4)$ |
| Riemann tensor | $R^\rho{}_{\sigma\mu\nu} = \partial_\mu\Gamma^\rho_{\nu\sigma} - \partial_\nu\Gamma^\rho_{\mu\sigma} + \Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}$ | $(N, 4, 4, 4, 4)$ |
| Ricci tensor | $R_{\mu\nu} = R^\rho{}_{\mu\rho\nu}$ | $(N, 4, 4)$ |
| Ricci scalar | $R = g^{\mu\nu}R_{\mu\nu}$ | $(N,)$ |

---

## 5. Conserved Information Current

A key prediction of the Unitary Manifold is the existence of a **conserved information current**:

$$\nabla_\mu J^\mu_{\rm inf} = 0, \qquad J^\mu_{\rm inf} = \phi^2 u^\mu$$

where $u^\mu$ is the unit 4-velocity of a fiducial observer. This conservation law is a geometric consequence of the 5D diffeomorphism invariance projected to 4D. It implies **black hole information is never destroyed** (Theorem XII, `QUANTUM_THEOREMS.md`).

---

## 6. Holographic Entropy

The fourth pillar of the framework is the **holographic entropy-area relation**. For a 2D boundary surface $\partial\mathcal{M}$ with induced metric $h_{ab}$, the Bekenstein–Hawking entropy is:

$$S = \frac{A(\partial\mathcal{M})}{4G_4}$$

The Unitary Manifold extends this to include corrections from the irreversibility field $B_\mu$ and the scalar $\phi$.

---

## 7. Unified Equation of the Unitary Manifold (UEUM)

The full geodesic equation on the Unitary Manifold is:

$$\ddot{X}^a + \Gamma^a_{bc}\dot{X}^b\dot{X}^c = G_U^{ab}\nabla_b S_U + \frac{\delta}{\delta X^a}\!\left(\sum_i \frac{A_{\partial,i}}{4G} + Q_{\rm top}\right)$$

where:
- $G_U^{ab}$ is the metric on the space of manifold states
- $S_U$ is the universal entropy functional
- $A_{\partial,i}$ are the boundary areas of the $i$-th manifold
- $Q_{\rm top}$ is the topological charge

---

## 8. Final Theorem of the Unitary Manifold (FTUM)

**Theorem:** There exists a fixed point $\Psi^*$ of the combined operator

$$U = \mathbf{I} + \mathbf{H} + \mathbf{T}$$

where $\mathbf{I}$ = Irreversibility operator, $\mathbf{H}$ = Holography operator, $\mathbf{T}$ = Topology operator, such that

$$U\Psi^* = \Psi^*$$

This fixed point represents the **attractor state** of the multiverse under joint irreversibility, holographic, and topological constraints. Implemented in `src/multiverse/fixed_point.py`. A Banach fixed-point proof is provided in `fixed_point.analytic_banach_proof()`.

---

## 9. Derivation of α from the 5D Riemann Cross-Block Term (v9.1)

The nonminimal coupling $\alpha$ in the 4D effective action is **not** a free parameter — it is determined entirely by the compactification geometry.

### Derivation

The 5D Riemann tensor $\mathcal{R}^A{}_{BCD}$ computed from the KK metric $G_{AB}$ contains **cross-block components** that mix the 4D block indices $\mu,\nu \in \{0,1,2,3\}$ with the compact-dimension index $5$:

$$R^\mu{}_{5\nu5} \;=\; \text{Riem5}[:, :4, 4, :4, 4]$$

After integrating the 5D action over the compact dimension of radius $L_5 = \phi_0\,\ell_P$, these components contribute the term $\alpha\,\ell_P^2\,R\,H^2$ to the 4D effective Lagrangian with coefficient:

$$\boxed{\alpha \;=\; \left(\frac{\ell_P}{L_5}\right)^2 \;=\; \frac{1}{\phi_0^2}}$$

This follows directly from $G_{55} = \phi^2$, which identifies the radion $\phi_0$ with $L_5/\ell_P$ in Planck units.

### Self-consistency with φ-stabilisation

The stabilised value $\phi_0$ is already determined internally (Requirement 1) by the scalar field equation:

$$\beta\,\Box\phi \;=\; \tfrac{1}{2}\phi^{-1/2}R \;+\; \tfrac{1}{4}\phi^{-2}H_{\mu\nu}H^{\mu\nu}$$

Setting $\phi = \phi_0$ (the fixed point) and solving gives $\phi_0$ from the curvature and vorticity of the background. Substituting back: $\alpha = \phi_0^{-2}$.

The chain is therefore closed internally:

$$S_5 \;\xrightarrow{\text{KK reduction}}\; \phi_0 \;\xrightarrow{G_{55}=\phi^2}\; L_5 = \phi_0\,\ell_P \;\xrightarrow{}\; \alpha = \phi_0^{-2}$$

### Numerical implementation

```python
from src.core.metric import extract_alpha_from_curvature
from src.multiverse.fixed_point import derive_alpha_from_fixed_point

# Geometric extraction: α = ⟨1/φ²⟩
alpha, cross_block_riem = extract_alpha_from_curvature(g, B, phi, dx)

# From stabilised radion: α = 1/φ₀²
alpha_predicted, _, _ = derive_alpha_from_fixed_point(phi_stabilized=phi_0)
```

---

## 10. Braided Winding and the Sum-of-Squares Resonance (v9.x)

The single-winding-mode theory ($n_w = 5$) predicts $r = 0.097$, which exceeds the BICEP/Keck 2021 bound $r < 0.036$. The **braided-winding resolution** uses two winding modes simultaneously.

### Braid Setup

When modes $n_1 = 5$ and $n_2 = 7$ are **braided** around each other in the compact $S^1/\mathbb{Z}_2$ dimension, the Chern–Simons term at level $k_\text{CS}$ couples their kinetic sectors:

$$\rho = \frac{2 n_1 n_2}{k_\text{CS}}$$

Under the **sum-of-squares resonance condition** $k_\text{CS} = n_1^2 + n_2^2$:

$$k_\text{CS} = 5^2 + 7^2 = 74$$

The canonically-normalised braided sound speed becomes:

$$c_s = \frac{|n_2^2 - n_1^2|}{k_\text{CS}} = \frac{24}{74} = \frac{12}{37} \approx 0.3243$$

### Braided CMB Predictions

The braided tensor-to-scalar ratio is suppressed by $c_s$, while $n_s$ is unchanged at leading order:

$$r_\text{braided} = r_\text{bare} \times c_s \approx 0.097 \times 0.3243 \approx 0.0315$$
$$n_{s,\text{braided}} \approx 0.9635$$

| Quantity | Braided Prediction | Observation |
|---------|-------------------|-------------|
| $n_s$ | 0.9635 | Planck 2018: 0.9649 ± 0.0042 ✅ |
| $r$ | 0.0315 | BICEP/Keck: $r < 0.036$ ✅ |
| $\beta$ | 0.3513° | Komatsu 2022: ≈ 0.35° ± 0.14° ✅ |

The integer $k_\text{CS} = 74$ is selected by the birefringence measurement. The fact that $74 = 5^2 + 7^2$ is the **resonance identity** — the Chern–Simons level equals the Euclidean norm-squared of the braid vector. This resolves the $r$-tension without new free parameters.

Implemented in `src/core/braided_winding.py` (118 tests in `tests/test_braided_winding.py`).

### Braided φ₀ Closure (Pillar 56)

The FTUM fixed-point value $\phi_0$ also has a braided form:

$$\phi_0^{\rm FTUM} = n_w \cdot 2\pi \cdot \sqrt{1 + c_s^2} \approx 33.03$$

The braided spectral-index formula:

$$n_{s,\text{braided}}(\phi_0, c_s) = 1 - \frac{36(1 + c_s^2)}{\phi_0^2}$$

evaluated at $(\phi_0^{\rm FTUM}, c_s = 12/37)$ equals the canonical prediction $n_s(\phi_0^{\rm canonical})$ exactly — the closure is internally consistent.

---

## 11. k_CS = 74 Topological Completeness Theorem (Pillar 74)

Seven independent constraint paths all converge to 74:

| Constraint | Result |
|-----------|--------|
| C1 — Sum-of-squares resonance | $5^2 + 7^2 = 74$ |
| C2 — CS gap saturation ($n^2 \leq n_w$) | $k_\text{eff}(5) = 74$ |
| C3 — Birefringence $\beta = 0.3513°$ | minimiser at $k = 74$ |
| C4 — Braided sound speed $c_s = 12/37$ | $k = 74$ |
| C5 — Moduli-winding link | $k = 74$ |
| C6 — Pillar count | 74 pillars closed |
| C7 — Back-reaction eigenvalue = 1 | $k = 74$ |

The convergence of all 7 constraints to the same integer is the capstone of the Unitary Manifold. Implemented in `src/core/completeness_theorem.py` (170 tests).

---

## References

- Kaluza, T. (1921). *Zum Unitätsproblem in der Physik.* Sitzungsber. Preuss. Akad. Wiss.
- Klein, O. (1926). *Quantentheorie und fünfdimensionale Relativitätstheorie.* Z. Phys.
- Misner, C. W., Thorne, K. S., Wheeler, J. A. (1973). *Gravitation.* W. H. Freeman.
- Planck Collaboration (2018). *Planck 2018 results. X. Constraints on inflation.* A&A 641, A10.
- BICEP/Keck Collaboration (2021). *Improved Constraints on Primordial Gravitational Waves.* PRL 127, 151301.
- Komatsu, E. et al. (2022). *New physics from the polarised light of the cosmic microwave background.* Nature Reviews Physics 4, 452–469.
- Walker-Pearson, T. C. (2026). *The Unitary Manifold.* v9.19. [`THEBOOKV9a (1).pdf`](../THEBOOKV9a%20(1).pdf)
