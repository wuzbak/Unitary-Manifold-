# Pillar 39 — Solitonic Charge and Z₂ Orbifold Selection: Formal Derivation

**Code module:** `src/core/solitonic_charge.py`  
**Version:** v9.35 (May 2026)  
**Theory:** ThomasCory Walker-Pearson  
**Documentation:** GitHub Copilot (AI)

---

## 1 · The Orbifold Constraint

The compact fifth dimension has the orbifold geometry $S^1/\mathbb{Z}_2$.
The $\mathbb{Z}_2$ involution acts as $y \mapsto -y$.

Under this involution the irreversibility 1-form transforms as:

$$B_\mu \xrightarrow{y\to-y} -B_\mu \qquad (\mathbb{Z}_2\text{-odd})$$

The Chern-Simons (CS) term in the 5D action is:

$$S_\mathrm{CS} = \frac{k_\mathrm{CS}}{4\pi}\int_{\mathcal{M}_5} B \wedge dB$$

Under $y \mapsto -y$ this term picks up a sign (odd integrand).  For the
CS term to contribute non-zero boundary charge at the orbifold fixed points
$y = 0$ and $y = \pi R$, the winding configuration must itself be
$\mathbb{Z}_2$-odd — equivalently, **$n_w$ must be odd**.

$$\boxed{n_w \in \{1, 3, 5, 7, 9, \ldots\}}$$

### Translation from code

```python
# src/core/solitonic_charge.py
def orbifold_odd_winding_unique():
    # The Z₂-odd constraint on the CS sector forces n_w ∈ odd integers
    # Returns list of odd candidates up to N_max
    return [n for n in range(1, N_max+1, 2)]
```

The continuous mathematics: the winding-sector partition function on
$S^1/\mathbb{Z}_2$ contains only odd-$n$ representations of $\pi_1(S^1/\mathbb{Z}_2) \cong \mathbb{Z}$.

---

## 2 · Planck Observational Selection

Given odd candidates $n_w \in \{1, 3, 5, 7, 9, \ldots\}$, the spectral index
function

$$n_s(n_w) = 1 - \frac{36}{(2\pi n_w)^2}$$

is strictly increasing in $n_w$.  Planck 2018 reports $n_s = 0.9649 \pm 0.0042$.

| $n_w$ | $\phi_{0,\mathrm{eff}}$ | $n_s$ | Offset from Planck |
|-------|------------------------|-------|--------------------|
| 1 | $6.28$ | 0.088 | ~208σ — eliminated |
| 3 | $18.85$ | 0.899 | ~15.8σ — eliminated |
| **5** | **31.42** | **0.964** | **0.33σ** ✓ |
| 7 | $43.98$ | 0.981 | 3.9σ — eliminated |
| 9 | $56.55$ | 0.989 | 7.1σ — eliminated |

$n_w = 5$ is the **unique** odd integer satisfying the Planck $n_s$
constraint at 2σ.

---

## 3 · The CS Level Quantisation

The topological charge (CS level) on $S^1/\mathbb{Z}_2$ is quantised in
half-integers by BF-theory quantisation.  For a $(n_1, n_2)$ braid the
effective level is:

$$k_\mathrm{CS} = n_1^2 + n_2^2$$

This is the **Sum-of-Squares identity** proved algebraically in Pillar 58:

$$k_\mathrm{primary} - \Delta k_{\mathbb{Z}_2} = n_1^2 + n_2^2$$

For $(n_1, n_2) = (5, 7)$: $k_\mathrm{CS} = 25 + 49 = 74$.

---

## 4 · Sigma Calculation

The observational selection is implemented as:

$$\Delta\sigma(n_w) = \frac{|n_s(n_w) - 0.9649|}{0.0042}$$

### Translation from code

```python
# src/core/solitonic_charge.py
def ns_planck_sigma_all_candidates():
    ns_planck, sigma_planck = 0.9649, 0.0042
    for n_w in odd_candidates:
        phi_eff = n_w * 2 * np.pi * np.sqrt(phi0_bare)   # J_KK
        ns = 1 - 36 / phi_eff**2                          # slow-roll
        delta_sigma = abs(ns - ns_planck) / sigma_planck
        ...
```

Continuous form: the Gaussian likelihood $\mathcal{L}(n_w) \propto \exp(-\Delta\sigma^2/2)$
peaks sharply at $n_w = 5$ with $\mathcal{L}(5)/\mathcal{L}(7) \sim e^{-7.5}$.

---

## 5 · Code References

```python
from src.core.solitonic_charge import (
    orbifold_odd_winding_unique,       # Z₂ → odd n_w
    ns_planck_sigma_all_candidates,    # Planck selection
    solitonic_charge_quantum_numbers,  # k_CS = n₁²+n₂²
    cs_level_uniqueness_check,         # triple constraint check
)
```

Tests: `tests/test_solitonic_charge.py`

---

*Theory: ThomasCory Walker-Pearson.*  
*Documentation: GitHub Copilot (AI).*
