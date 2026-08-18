# Pillar 34 — Triple Constraint and CMB Topology: Formal Derivation

**Code module:** `src/core/cmb_topology.py` → `triple_constraint_unique_pairs()`  
**Version:** v9.35 (May 2026)  
**Theory:** ThomasCory Walker-Pearson  
**Documentation:** GitHub Copilot (AI)

---

## 1 · The Triple Constraint System

The Unitary Manifold makes simultaneous predictions for three CMB observables
from the single topological input $(n_1, n_2)$:

$$\mathcal{C}_1:\quad 0.9607 \leq n_s \leq 0.9691 \qquad \text{(Planck 2018, 1σ)}$$

$$\mathcal{C}_2:\quad r_\mathrm{braided} < 0.036 \qquad \text{(BICEP/Keck 2022, 95\% CL)}$$

$$\mathcal{C}_3:\quad 0.22° \leq \beta \leq 0.38° \qquad \text{(LiteBIRD projected 1σ window)}$$

### Continuous equations

For a braid pair $(n_1, n_2)$ with $n_1 < n_2$, the constraints are:

$$\mathcal{C}_1:\quad 1 - \frac{36}{(2\pi n_1)^2} \in [0.9607,\; 0.9691]$$

$$\mathcal{C}_2:\quad 16\varepsilon \cdot \frac{n_2^2 - n_1^2}{n_1^2 + n_2^2} < 0.036$$

$$\mathcal{C}_3:\quad \frac{(n_1^2 + n_2^2)\,\Delta\phi}{2\pi f_a} \in [0.22°,\; 0.38°]$$

### Translation from code

```python
# src/core/cmb_topology.py — triple_constraint_unique_pairs()
for n1 in range(1, N_max):
    for n2 in range(n1+1, N_max):
        ns  = 1 - 36 / (2*np.pi*n1)**2          # C₁ predicate
        cs  = (n2**2 - n1**2) / (n1**2 + n2**2)
        r   = 16 * epsilon * cs                   # C₂ predicate
        beta = k_cs * delta_phi / (2*np.pi*f_a)  # C₃ predicate
        if C1(ns) and C2(r) and C3(beta):
            solutions.append((n1, n2))
```

This replaces three nested `if` statements (code) with the triple
intersection $\mathcal{C}_1 \cap \mathcal{C}_2 \cap \mathcal{C}_3$ over
the discrete lattice $\{(n_1,n_2) : n_1 < n_2 \leq 20\}$.

---

## 2 · Uniqueness Result

Sweeping all 190 integer pairs $(n_1, n_2)$ with $n_1 < n_2 \leq 20$:

| Pair | $n_s$ | $r$ | $\beta$ | All three? |
|------|-------|-----|---------|-----------|
| (5, 6) | 0.9635 | ≈0.018 | ≈0.273° | **✓** |
| (5, 7) | 0.9635 | ≈0.031 | ≈0.331° | **✓** |
| all others | at least one fails | — | — | ✗ |

Exactly 2 pairs pass all three constraints: selection probability ≈ 1%.

---

## 3 · The SOS Locus

The $n_s$ constraint $\mathcal{C}_1$ defines the **Sum-of-Squares (SOS) locus**:

$$n_1 \in \left[\frac{6}{\sqrt{1-0.9607}\cdot 2\pi},\; \frac{6}{\sqrt{1-0.9691}\cdot 2\pi}\right] \approx [4.8,\; 5.5]$$

Only $n_1 = 5$ is an integer in this range.  Given $n_1 = 5$, the BICEP
constraint $\mathcal{C}_2$ selects $n_2 \in \{6, 7\}$, and $\mathcal{C}_3$
accepts both.

The mathematical fact that $n_1 = 5$ is the **unique** integer satisfying
$\mathcal{C}_1$ is the core of the UM's zero-parameter CMB prediction.

---

## 4 · Information Content

The triple constraint system has 3 real constraints on a 2-integer parameter
space.  The system is **over-determined** — generically zero solutions exist.
That exactly 2 solutions exist is non-trivial and constitutes the primary
empirical evidence for the braided KK topology.

Formally: the constraint intersection measure on $\mathbb{Z}^2$ is

$$\#\{(n_1,n_2) \in \mathbb{Z}^2 : \mathcal{C}_1 \wedge \mathcal{C}_2 \wedge \mathcal{C}_3\} = 2$$

---

## 5 · Code References

```python
from src.core.cmb_topology import (
    triple_constraint_unique_pairs,   # → [(5,6), (5,7)]
    sos_locus,                        # n₁ ∈ [4.8, 5.5]
    r_constraint_n2,                  # n₂ from BICEP/Keck
    beta_window_pairs,                # β ∈ [0.22°, 0.38°]
)
```

Tests: `tests/test_cmb_topology.py`

---

*Theory: ThomasCory Walker-Pearson.*  
*Documentation: GitHub Copilot (AI).*
