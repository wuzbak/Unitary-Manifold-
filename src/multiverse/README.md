# src/multiverse — FTUM Fixed Point (TIER 1)

**Epistemic status: Physics Core — verified mathematical physics**

Implements the Fixed-Point Theorem of the Unitary Manifold (FTUM, Pillar 5).
The operator U acts on the joint state Ψ_bulk ⊗ Ψ_boundary; convergence to
Ψ* is the attractor condition.

## Key module

`fixed_point.py` — UEUM operator, FTUM iteration, convergence diagnostics

## Tests

```bash
python -m pytest tests/test_fixed_point.py tests/test_convergence.py -v
```
