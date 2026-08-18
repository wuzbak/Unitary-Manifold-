# Pillar 5 — FTUM Fixed-Point Equation: Formal Derivation

**Code module:** `src/multiverse/fixed_point.py` → `fixed_point_iteration()`, `ueum_acceleration()`  
**Version:** v9.35 (May 2026)  
**Theory:** ThomasCory Walker-Pearson  
**Documentation:** GitHub Copilot (AI)

---

## 1 · Physical Motivation

The Final Theorem of the Unitary Manifold (FTUM) asserts that the universe
evolves toward a unique stable fixed point of the combined operator
$\hat{U} = \hat{I} + \hat{H} + \hat{T}$.  This fixed point corresponds to the
emergence of classical observers.  This pillar formalises the fixed-point
equation and its convergence proof.

---

## 2 · The UEUM Acceleration Equation

The generative law of the Unitary Multiverse is the **Unified Evolution
Equation of the Unitary Manifold (UEUM)**:

$$\boxed{\ddot{X}^a + \Gamma^a_{bc}\,\dot{X}^b\dot{X}^c
= \mathcal{G}_U^{ab}\,\nabla_b S_U
+ \frac{\delta}{\delta X^a}\!\left(\sum_i \frac{A_{\partial,i}}{4G} + Q_\mathrm{top}\right)}$$

### Translation from code

```python
# src/multiverse/fixed_point.py — ueum_acceleration()
acc = -np.einsum('abc,b,c->a', Gamma, dX, dX)     # −Γ^a_{bc} Ẋ^b Ẋ^c
acc += G_U @ grad_S                                  # G_U^{ab} ∇_b S_U
acc += delta_boundary_area / (4 * G_N)              # ΣA_∂/(4G) term
acc += delta_Q_top                                   # Q_top term
```

Continuous form:
- **Geodesic deviation:** $\Gamma^a_{bc}$ are the Christoffel symbols of the
  Unitary Multiverse metric $\mathcal{G}_{ab}$.
- **Entropic driving:** $\mathcal{G}_U^{ab}\nabla_b S_U$ is the gradient of
  the total entropy functional in the configuration space.
- **Holographic pressure:** $\sum_i A_{\partial,i}/(4G)$ is the Bekenstein
  boundary-area sum (Second Law pressure).
- **Topological charge:** $Q_\mathrm{top}$ is the Chern-Simons winding
  contribution.

---

## 3 · The FTUM Fixed-Point Operator

The combined operator is

$$\hat{U} = \hat{I} + \hat{H} + \hat{T}$$

where:

| Operator | Role | Generator |
|----------|------|-----------|
| $\hat{I}$ | Irreversible flow | $\nabla_\mu J^\mu_\mathrm{inf} = 0$ |
| $\hat{H}$ | Holographic constraint | $S_\mathrm{bulk} = A_\partial/(4G)$ |
| $\hat{T}$ | Topological invariant | $k_\mathrm{CS} = n_1^2 + n_2^2 = 74$ |

The fixed-point equation is:

$$\hat{U}\,\Psi^* = \Psi^*$$

### Translation from code

```python
# src/multiverse/fixed_point.py — fixed_point_iteration()
for step in range(max_iter):
    psi_new = apply_I(psi) + apply_H(psi) + apply_T(psi)   # Û Ψ
    if np.linalg.norm(psi_new - psi) < tol:
        break                                                 # Ψ* reached
    psi = psi_new
```

Continuous form: Banach contraction on the space of field configurations
$\Psi \in \mathcal{F}$ with the sup-norm $\|\cdot\|_\infty$.

---

## 4 · Convergence Theorem

**Theorem (Banach Fixed-Point):** Let $\mathcal{F}$ be the Banach space of
smooth field configurations on $\mathcal{M}_5$ with finite entropy.  If
$\hat{U}$ is a contraction mapping with Lipschitz constant $\kappa < 1$, then:

1. There exists a unique fixed point $\Psi^* \in \mathcal{F}$.
2. The iteration $\Psi_{n+1} = \hat{U}\,\Psi_n$ converges to $\Psi^*$ for
   any initial $\Psi_0$.
3. The convergence rate is geometric: $\|\Psi_n - \Psi^*\| \leq \kappa^n \|\Psi_0 - \Psi^*\|$.

The contraction constant is $\kappa \approx 0.7$ (verified numerically in
`tests/test_fixed_point.py`).

---

## 5 · Entropy Fixed Point and the φ₀ Bridge

The FTUM entropy fixed point:

$$S^* = \frac{A}{4G_5} = 0.25 \quad \text{(Planck units, } A = 1\text{)}$$

links to the radion initial condition via:

$$\phi_{0,\mathrm{bare}} = \frac{R}{\ell_\mathrm{Pl}} \xrightarrow{\text{Planck units}} 1$$

This bridge (Pillar 56-B, `src/core/phi0_ftum_bridge.py`) feeds into the
inflationary spectral index chain:

$$\phi_{0,\mathrm{eff}} = n_w \cdot 2\pi \cdot \sqrt{\phi_{0,\mathrm{bare}}}
= 5 \cdot 2\pi \cdot 1 \approx 31.42$$

$$n_s = 1 - \frac{36}{\phi_{0,\mathrm{eff}}^2} \approx 0.9635 \quad\checkmark$$

---

## 6 · Code References

```python
from src.multiverse.fixed_point import (
    fixed_point_iteration,   # Banach iteration → Ψ*
    ueum_acceleration,       # UEUM geodesic law
    derive_alpha_from_fixed_point,  # α from Ψ*
)
```

Tests: `tests/test_fixed_point.py`

---

*Theory: ThomasCory Walker-Pearson.*  
*Documentation: GitHub Copilot (AI).*
