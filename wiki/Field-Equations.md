# Walker–Pearson Field Equations

The Walker–Pearson (WP) equations are the 4D effective field equations that emerge from dimensionally reducing the 5D Einstein–Hilbert action of the Unitary Manifold. They unify gravitational, irreversibility, and scalar degrees of freedom.

---

## 1. Full Covariant Form

$$G_{\mu\nu} + \lambda^2 \left( H_{\mu\rho}H_\nu{}^\rho - \tfrac{1}{4}g_{\mu\nu}H^2 \right) + \alpha R \phi^2 g_{\mu\nu} = 8\pi G_4\, T_{\mu\nu}$$

### Term-by-term interpretation

| Term | Origin | Physical meaning |
|------|--------|-----------------|
| $G_{\mu\nu}$ | Einstein tensor | Standard gravitational curvature sourced by energy-momentum |
| $\lambda^2(H_{\mu\rho}H_\nu{}^\rho - \tfrac{1}{4}g_{\mu\nu}H^2)$ | Maxwell-like | Stress-energy of the irreversibility gauge field |
| $\alpha R \phi^2 g_{\mu\nu}$ | Nonminimal coupling | Scalar-curvature interaction; drives entropic cosmology |
| $8\pi G_4\, T_{\mu\nu}$ | Standard matter | Ordinary matter stress-energy tensor |

---

## 2. Companion Equations

### Gauge Field Equation

$$\nabla_\nu H^{\nu\mu} = 0$$

This is the covariant conservation equation for the irreversibility field — the analogue of Maxwell's equations in vacuum.

### Scalar Field Equation

$$\Box\phi + \alpha R\phi = S[H]$$

where $S[H] = \tfrac{1}{2}H_{\mu\nu}H^{\mu\nu}$ is the scalar source from the gauge field. This drives the growth of entanglement capacity in high-curvature regions.

---

## 3. Dimensional Reduction

Starting from the 5D metric ansatz (see [Mathematical Framework](Mathematical-Framework)):

1. Compute the 5D Ricci scalar $\mathcal{R}_5$ in terms of $(g_{\mu\nu}, B_\mu, \phi)$.
2. Integrate over the compact fifth dimension (circumference $2\pi r_5$).
3. The resulting 4D effective Lagrangian is:

$$\mathcal{L}_{\rm 4D} = \frac{\phi}{16\pi G_4} R - \frac{\lambda^2 \phi}{4} H_{\mu\nu}H^{\mu\nu} + \frac{\alpha}{2}\phi R - \frac{1}{2}(\partial\phi)^2$$

4. Variation with respect to $g^{\mu\nu}$ yields the Walker–Pearson equations above.

---

## 4. Discretised Form (Numerical Implementation)

For the 1+1D (time + one spatial dimension) numerical system implemented in `src/core/evolution.py`, the field equations are discretised as:

**Metric update:**
$$\partial_t g_{\mu\nu} = -2 R_{\mu\nu} + T_{\mu\nu}[B,\phi]$$

where the stress-energy approximation is:
$$T_{\mu\nu} \approx \lambda^2\left(H_{\mu\rho}H_\nu{}^\rho - \tfrac{1}{4}g_{\mu\nu}H^2\right)$$

**Gauge field update:**
$$\partial_t B_\mu = \partial_\nu(\lambda^2 H^{\nu\mu})$$

approximated by raising indices with the local inverse metric.

**Scalar update (semi-implicit):**
$$\phi^{n+1} = \phi^n + \Delta t\,(\Delta\phi^n + \alpha R^n \phi^n + S[H^n])$$

where $\Delta\phi$ is the discrete Laplacian from `np.roll`-based central differences.

---

## 5. Constraints and Diagnostics

The following quantities should remain bounded throughout a valid simulation:

| Constraint | Expression | Ideal value |
|------------|-----------|-------------|
| Ricci norm | $\langle\|R_{\mu\nu}\|\rangle_F$ | Bounded, non-diverging |
| Scalar curvature max | $\max|R|$ | Bounded |
| Gauge field norm | $\langle\|B_\mu\|\rangle$ | Bounded |
| Scalar max | $\max|\phi|$ | $\approx 1$ for weakly perturbed runs |

Use `constraint_monitor(Ricci, R, B, phi)` from `src.core.evolution` to track these during a run.

---

## 6. Second Law as a Geometric Identity

A central result of the Unitary Manifold is that the **Second Law of Thermodynamics** is not an independent postulate but follows directly from the Walker–Pearson equations. Specifically, the non-negativity of the entropy production rate:

$$\dot{S} \geq 0$$

is equivalent (in the symmetry-reduced sector) to the positive-definiteness of the $H_{\mu\nu}H^{\mu\nu}$ contribution to the stress-energy, which is guaranteed by the antisymmetry of $H$ and the Lorentzian metric signature.

For a full derivation, see Chapters 7–9 of the [monograph](Monograph-Structure).
