# Mathematical Framework

The Unitary Manifold rests on five interlocking pillars. This page documents the core mathematical structures shared across all pillars.

---

## 1. The 5D Kaluza–Klein Metric Ansatz

The irreversibility field $B_\mu$ is embedded as the off-diagonal component of a 5×5 parent metric $G_{AB}$:

$$G_{AB} = \begin{pmatrix} g_{\mu\nu} + \lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & 1 \end{pmatrix}$$

so that $G_{\mu 5} = \lambda B_\mu$ and $G_{55} = 1$ (radion fixed to unity).

### Key Fields

| Symbol | Name | Role |
|--------|------|------|
| $g_{\mu\nu}$ | 4D metric | spacetime geometry (signature −+++) |
| $B_\mu$ | Irreversibility field | gauge field encoding the arrow of time |
| $\phi$ | Entanglement-capacity scalar | nonminimal coupling to curvature |
| $\lambda$ | Kaluza–Klein coupling | controls strength of $B$–gravity mixing |
| $\alpha$ | Nonminimal coupling | coefficient of $\alpha R \phi^2$ in the action |

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

where $u^\mu$ is the unit 4-velocity of a fiducial observer. This conservation law is a geometric consequence of the 5D diffeomorphism invariance projected to 4D.

In the numerical implementation, the information density is $\rho = \phi^2$ and the current is approximated as:

$$J^\mu \approx \frac{\phi^2}{\sqrt{|g_{00}|}} \left(1,\ \frac{\partial_x\phi}{|\nabla\phi|},\ 0,\ 0\right)$$

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

This fixed point represents the **attractor state** of the multiverse under joint irreversibility, holographic, and topological constraints.

---

## References

- Kaluza, T. (1921). *Zum Unitätsproblem in der Physik.* Sitzungsber. Preuss. Akad. Wiss.
- Klein, O. (1926). *Quantentheorie und fünfdimensionale Relativitätstheorie.* Z. Phys.
- Misner, C. W., Thorne, K. S., Wheeler, J. A. (1973). *Gravitation.* W. H. Freeman.
- Walker-Pearson, T. C. (2026). *The Unitary Manifold.* v9.0. [`THEBOOKV9a (1).pdf`](../THEBOOKV9a%20(1).pdf)
