# src/holography — Holographic Boundary (TIER 1)

**Epistemic status: Physics Core — verified mathematical physics**

Implements the holographic boundary dynamics of the Unitary Manifold (Pillar 4).
The entropy-area relation S = A/4G is a constraint on the 5D boundary; this
module numerically verifies that the evolution satisfies it.

## Key module

`boundary.py` — entropy production, boundary saturation, holographic screen dynamics

## Tests

```bash
python -m pytest tests/test_boundary.py -v
```
