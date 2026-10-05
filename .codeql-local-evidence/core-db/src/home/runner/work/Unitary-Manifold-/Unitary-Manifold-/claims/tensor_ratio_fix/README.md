# Claim: r = 0.097 is the honest, code-verified prediction (active tension) — **RESOLVED via braided (5,7) state**

> **Status update (2026-04-13):** The r vs nₛ tension (Q18) has been resolved.  The
> braided (n_w=5, n_w=7) resonant state with k_cs = 74 = 5² + 7² gives
> r_braided ≈ 0.0315 < 0.036 (BICEP/Keck ✓) while leaving nₛ unchanged at 0.9635
> (Planck 1σ ✓).  See `src/core/braided_winding.py` and
> `tests/test_braided_winding.py` for the derivation and 70-test numerical
> verification.  The history and context below are preserved for reference.

---

## What is claimed

For the Unitary Manifold with winding number n_w = 5 (the value required to
place nₛ inside the Planck 2018 1-σ window), the tensor-to-scalar ratio is

```
r = 0.0973   (code-verified, n_w = 5, φ₀_eff = 5·2π ≈ 31.42)
```

This is **not** a post-hoc adjustment.  The value is **an active data tension**:
BICEP/Keck 2022 constrains r < 0.036 at 95 % CL, and r = 0.097 already exceeds
this bound.

The theory has no free knob to reduce r while preserving nₛ:

| n_w | φ₀_eff | nₛ     | σ from Planck | r      | vs BICEP/Keck |
|-----|--------|--------|---------------|--------|---------------|
| 4   | 25.13  | 0.955  | −2.3 σ        | 0.149  | ❌ excluded   |
| **5** | **31.42** | **0.964** | **+0.0 σ** | **0.097** | **⚠️ tension** |
| 6   | 37.70  | 0.970  | +1.3 σ        | 0.067  | ⚠️ tension    |
| 9   | 56.55  | 0.983  | +4.3 σ        | 0.030  | ✅ OK         |

No integer n_w simultaneously satisfies nₛ within 1 σ of Planck **and**
r < 0.036.  This is documented as Q18 in `BIG_QUESTIONS.md`.

## Why this claim matters

- The tension is **real and acknowledged** — it is not hidden.
- The claim is that **n_w = 5 is the unique winding number consistent with nₛ**.
- The r-tension is therefore a genuine falsifiable prediction:
  if B-mode experiments confirm r < 0.036 at high significance and future
  CMB-S4 finds no tensor signal at r ≈ 0.097, the standard n_w = 5 path
  of this theory is excluded.

## What would falsify this claim

1. **B-mode detection at r < 0.036**: Future CMB-S4 or LiteBIRD measurement of
   r < 0.036 at ≥ 3σ while simultaneously confirming nₛ ≈ 0.964 would rule out
   the n_w = 5 double-well potential without a new suppression mechanism.

2. **Finding an integer n_w that satisfies both constraints**: If a new topological
   argument fixes n_w ≥ 9, the r tension is resolved — but then nₛ must be
   re-derived independently.

## Minimal code path

```python
from src.core.inflation import ns_from_phi0, effective_phi0_kk

phi0_eff = effective_phi0_kk(1.0, n_winding=5)  # = 5 · 2π ≈ 31.42
ns, r, eps, eta = ns_from_phi0(phi0_eff)
print(f"ns = {ns:.4f},  r = {r:.4f}")           # ns=0.9635, r=0.0973
assert r > 0.036                                  # tension confirmed
```

## Delete-power test

Change `n_winding=5` to any value and observe:
- n_w < 5 → nₛ leaves the Planck window to the low side
- n_w > 6 → nₛ leaves the Planck window to the high side
- n_w = 9 → r finally drops below 0.036, but nₛ is excluded at >4σ

No integer resolves the tension.  Run `python test_claim.py` for the full scan.

## Source

- `src/core/inflation.py`: `ns_from_phi0()`, `effective_phi0_kk()`
- `BIG_QUESTIONS.md`: Q18 (tensor-to-scalar tension)
- BICEP/Keck 2022: arXiv:2110.00483
