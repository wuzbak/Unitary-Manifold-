# Pillar 1 — 5D Kaluza–Klein Metric: Formal Derivation

**Code module:** `src/core/metric.py` → `assemble_5d_metric()`  
**Symbolic module:** `src/core/symbolic_metric.py` → `symbolic_5d_metric()`  
**Version:** v9.35 (May 2026)  
**Theory:** ThomasCory Walker-Pearson  
**Documentation:** GitHub Copilot (AI)

---

## 1 · Physical Motivation

The Unitary Manifold (UM) promotes thermodynamic irreversibility from a
statistical postulate to a geometric fact.  The mechanism is a compact fifth
dimension whose off-diagonal metric components *are* the irreversibility field.
This is the 5D Kaluza–Klein (KK) ansatz (Kaluza 1921, Klein 1926) adapted to
entropy geometry.

---

## 2 · The 5D Metric Ansatz

The 5-dimensional parent metric $G_{AB}$ ($A,B \in \{0,1,2,3,5\}$) is
assembled from three 4D fields:

| Symbol | Name | Role |
|--------|------|------|
| $g_{\mu\nu}$ | 4D Lorentzian metric | spacetime geometry |
| $B_\mu$ | irreversibility 1-form | gauge field of $U(1)_\mathrm{irr}$ |
| $\phi$ | entropic dilaton / KK radion | size of the fifth dimension |

The **KK block form** is:

$$\boxed{G_{AB} = \begin{pmatrix} g_{\mu\nu} + \lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\[4pt] \lambda\phi B_\nu & \phi^2 \end{pmatrix}}$$

### Component-by-component translation from code

```python
# src/core/metric.py — assemble_5d_metric()
G5[:, :4, :4] = g + (lam*phi)**2 * np.einsum('ni,nj->nij', B, B)
#  ↓  continuous form:
#  G_μν = g_μν + λ²φ² B_μ B_ν

G5[:, :4, 4]  = lam * phi[:, None] * B
#  ↓  continuous form:
#  G_μ5 = G_5μ = λφ B_μ

G5[:, 4, 4]   = phi**2
#  ↓  continuous form:
#  G_55 = φ²
```

---

## 3 · Line Element

The corresponding **line element** is

$$ds^2 = g_{\mu\nu}\,dx^\mu dx^\nu + \phi^2\!\left(dy + \lambda B_\mu\,dx^\mu\right)^2$$

where $y \in [0, 2\pi R]$ is the compact coordinate.  Expanding:

$$ds^2 = \underbrace{g_{\mu\nu}\,dx^\mu dx^\nu}_{\text{4D gravity}}
       + \underbrace{\phi^2\,dy^2}_{\text{radion kinetic}}
       + \underbrace{2\lambda\phi^2 B_\mu\,dx^\mu dy}_{\text{KK cross-term}}
       + \underbrace{\lambda^2\phi^2 B_\mu B_\nu\,dx^\mu dx^\nu}_{\text{gauge contribution}}$$

The **cylinder condition** $\partial_5 G_{AB} = 0$ (no field depends on $y$)
reduces this to a consistent 4D effective theory after integration.

---

## 4 · Metric Determinant

A direct block-matrix computation gives

$$\sqrt{-G} = \phi\,\sqrt{-g}$$

(The $\phi^{1/2}$ power is convention-dependent; the UM uses $G_{55} = \phi^2$,
so the determinant picks up one power of $\phi$.)

This is verified numerically in `tests/test_metric.py: test_determinant`.

---

## 5 · Cylinder Condition and Dimensional Reduction

The cylinder condition

$$\partial_5 G_{AB} = 0$$

allows integration of the 5D action over the compact dimension.  With
circumference $2\pi r_5$ this yields the 4D effective action

$$S_\mathrm{eff} = \frac{1}{16\pi G}\int d^4x\,\sqrt{-g}
\left[R_4 - \tfrac{1}{4}H_{\mu\nu}H^{\mu\nu} + \beta(\nabla\phi)^2 + \cdots\right]$$

where $G = G_5 / (2\pi r_5)$ and $H_{\mu\nu} = \partial_\mu B_\nu - \partial_\nu B_\mu$.

---

## 6 · Numerical → Symbolic → LaTeX Pipeline

```python
# Generate the publication-ready LaTeX for G_{AB}:
from src.core.symbolic_metric import latex_5d_metric, derivation_chain

print(latex_5d_metric())
# → \begin{pmatrix} g_{00} + \lambda^{2} \phi^{2} B_{0}^{2} & \cdots \end{pmatrix}

for label, latex in derivation_chain():
    print(f"  {label}:")
    print(f"  $${latex}$$")
```

---

## 7 · Code References

```python
from src.core.metric import assemble_5d_metric, field_strength, compute_curvature
from src.core.symbolic_metric import symbolic_5d_metric, latex_5d_metric
```

Tests: `tests/test_metric.py`, `tests/test_symbolic_metric.py`

---

*Theory: ThomasCory Walker-Pearson.*  
*Documentation: GitHub Copilot (AI).*
