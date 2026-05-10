# JAX Backend

The JAX-accelerated backend provides JIT-compiled, differentiable versions of the core field-evolution kernels.

## Key functions

- `field_strength_jax(B, dx)` — H_μν = ∂_μ B_ν − ∂_ν B_μ, shape (N,4,4)
- `assemble_metric_jax(g, B, phi, lam)` — 5×5 KK metric, shape (N,5,5)
- `grad_spectral_index(phi0, n_w)` — (n_s, dn_s/dφ₀, dn_s/dn_w) via `jax.grad`
- `vmap_field_strength(B_batch, dx)` — batch over field configurations

## JAX version

```python
from src.core.jax_backend import JAX_VERSION
print(JAX_VERSION)  # e.g. 0.10.0
```
