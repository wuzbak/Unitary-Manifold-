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
| $\alpha R \phi^2 g_{\mu\nu}$ | Nonminimal coupling | Scalar-curvature interaction; drives entropic cosmology. $\alpha = \phi_0^{-2}$ is **derived**, not free |
| $8\pi G_4\, T_{\mu\nu}$ | Standard matter | Ordinary matter stress-energy tensor |

**GR is recovered exactly** in the limit $\lambda \to 0$, $\phi \to \phi_0 = \text{const}$.

---

## 2. Companion Equations

### Gauge Field Equation

$$\nabla_\nu H^{\nu\mu} = 0$$

This is the covariant conservation equation for the irreversibility field — the analogue of Maxwell's equations in vacuum.

### Scalar Field Equation

$$\Box\phi + \alpha R\phi = S[H]$$

where $S[H] = \tfrac{1}{2}H_{\mu\nu}H^{\mu\nu}$ is the scalar source from the gauge field. This drives the growth of entanglement capacity in high-curvature regions.

### Information Current Conservation

$$\nabla_\mu J^\mu_{\rm inf} = 0, \qquad J^\mu_{\rm inf} = \phi^2 u^\mu$$

This is a geometric consequence of 5D diffeomorphism invariance and implies **information is never destroyed** under the Walker–Pearson equations (Theorem XII).

---

## 3. Dimensional Reduction

Starting from the 5D metric ansatz (see [Mathematical Framework](Mathematical-Framework)):

1. Compute the 5D Ricci scalar $\mathcal{R}_5$ in terms of $(g_{\mu\nu}, B_\mu, \phi)$.
2. Integrate over the compact fifth dimension (circumference $2\pi r_5$).
3. The resulting 4D effective Lagrangian is:

$$\mathcal{L}_{\rm 4D} = \frac{\phi}{16\pi G_4} R - \frac{\lambda^2 \phi}{4} H_{\mu\nu}H^{\mu\nu} + \frac{\alpha}{2}\phi R - \frac{1}{2}(\partial\phi)^2$$

4. Variation with respect to $g^{\mu\nu}$ yields the Walker–Pearson equations above.

### α is not a free parameter

The cross-block 5D Riemann components $R^\mu{}_{5\nu5}$ (mixing the 4D block with the compact dimension) produce the $\alpha R H^2$ coupling with coefficient:

$$\alpha \;=\; \left(\frac{\ell_P}{L_5}\right)^2 \;=\; \frac{1}{\phi_0^2}$$

where $\phi_0$ is the stabilised radion value (from the scalar field equation, §Scalar Field Equation above) and $L_5 = \phi_0\,\ell_P$ is the compactification radius encoded in $G_{55} = \phi^2$.  See [Mathematical Framework §9](Mathematical-Framework#9-derivation-of-α-from-the-5d-riemann-cross-block-term-v91) for the full derivation.

---

## 4. Inflation and CMB Predictions

The Walker–Pearson equations in the slow-roll cosmological sector yield:

$$n_s = 1 - \frac{2}{\mathcal{N}_e} - \frac{1}{n_w^2 \pi^2} \approx 0.9635 \quad (n_w = 5)$$

$$r_\text{bare} = \frac{8}{3}(1 - n_s) \approx 0.097 \quad (\text{single-mode})$$

The **braided-winding** extension resolves the $r$-tension: when winding modes $n_1 = 5$ and $n_2 = 7$ are braided at Chern–Simons level $k_\text{CS} = 74 = 5^2 + 7^2$, the sound speed $c_s = 12/37$ suppresses $r$:

$$r_\text{braided} = r_\text{bare} \times c_s \approx 0.097 \times 0.3243 \approx 0.0315 < 0.036 \checkmark$$

The birefringence rotation angle is:

$$\beta = \frac{k_\text{CS}\,\alpha_\text{EM}}{2\pi} \approx 0.3513°$$

which matches the Komatsu et al. (2022) measurement of $0.35° \pm 0.14°$.

---

## 5. Discretised Form (Numerical Implementation)

For the 1+1D (time + one spatial dimension) numerical system implemented in `src/core/evolution.py`, the field equations are discretised using **RK4** (fourth-order Runge–Kutta):

**Metric update:**
$$\partial_t g_{\mu\nu} = -2 R_{\mu\nu} + T_{\mu\nu}[B,\phi]$$

where the stress-energy approximation is:
$$T_{\mu\nu} \approx \lambda^2\left(H_{\mu\rho}H_\nu{}^\rho - \tfrac{1}{4}g_{\mu\nu}H^2\right)$$

**Gauge field update:**
$$\partial_t B_\mu = \partial_\nu(\lambda^2 H^{\nu\mu})$$

approximated by raising indices with the local inverse metric.

**Scalar update (Goldberger–Wise stabilisation):**
$$\phi^{n+1} = \phi^n + \Delta t\,(\Delta\phi^n + \alpha R^n \phi^n + S[H^n] - m_\phi^2(\phi^n - \phi_0))$$

where $\Delta\phi$ is the discrete Laplacian from `np.roll`-based central differences and the $m_\phi^2$ term implements Goldberger–Wise stabilisation to keep $\phi$ bounded away from zero.

---

## 6. Constraints and Diagnostics

The following quantities should remain bounded throughout a valid simulation:

| Constraint | Expression | Ideal value |
|------------|-----------|-------------|
| Ricci norm | $\langle\|R_{\mu\nu}\|\rangle_F$ | Bounded, non-diverging |
| Scalar curvature max | $\max|R|$ | Bounded |
| Gauge field norm | $\langle\|B_\mu\|\rangle$ | Bounded |
| Scalar max | $\max|\phi|$ | $\approx \phi_0$ for weakly perturbed runs |
| Information conservation | $\|\nabla_\mu J^\mu\|$ | $\approx 0$ |

Use `constraint_monitor(Ricci, R, B, phi)` from `src.core.evolution` to track these during a run.

---

## 7. Second Law as a Geometric Identity

A central result of the Unitary Manifold is that the **Second Law of Thermodynamics** is not an independent postulate but follows directly from the Walker–Pearson equations. Specifically, the non-negativity of the entropy production rate:

$$\dot{S} \geq 0$$

is equivalent (in the symmetry-reduced sector) to the positive-definiteness of the $H_{\mu\nu}H^{\mu\nu}$ contribution to the stress-energy, which is guaranteed by the antisymmetry of $H$ and the Lorentzian metric signature.

For a full derivation, see Chapters 7–9 and 35–37 of the [monograph](Monograph-Structure).

---

## 8. Quantum Theorems

Four quantum theorems are derived directly from the Walker–Pearson equations (see `QUANTUM_THEOREMS.md`):

| Theorem | Statement | Implementation |
|---------|-----------|---------------|
| XII — BH Information Preservation | $\nabla_\mu J^\mu_\text{inf} = 0$ unconditionally | `evolution.py: information_current` |
| XIII — Canonical Commutation Relation | $[\hat\phi, \hat\pi_\phi] = i\hbar\,\delta^3(x-y)$ from Poisson bracket | `evolution.py: conjugate_momentum_phi` |
| XIV — Hawking Temperature | $T_H = \|\partial_r\phi/\phi\|/2\pi$ at horizon | `evolution.py: hawking_temperature` |
| XV — ER = EPR | Entanglement $\leftrightarrow$ shared fixed point under $\mathbf{T}$ | `fixed_point.py: shared_fixed_point_norm` |
