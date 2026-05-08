# LiteBIRD Falsifier Brief — Unitary Manifold

*Document version: 1.0 — 2026*

---

## 1 · Primary Falsifier: CMB Birefringence β

The **primary falsification test** of the Unitary Manifold's braided-winding
mechanism is the CMB polarization birefringence angle β.

The 5D geometry (K_CS = 74 = 5² + 7², winding number n_w = 5) predicts **two
distinct modes** of birefringence rotation:

| Mode | Predicted β |
|------|------------|
| Canonical (braided winding) | **β ≈ 0.273°** |
| Derived (higher harmonic) | **β ≈ 0.331°** |

### Admissible window and predicted gap

- **Admissible window:** β ∈ **[0.22°, 0.38°]**
  — any measurement outside this range **falsifies** the braided-winding mechanism.
- **Predicted inter-mode gap:** β ∈ **[0.29°, 0.31°]**
  — a detection *within* this gap would falsify the two-mode structure even if β
  falls inside the outer window.

Both conditions must be satisfied simultaneously for the prediction to survive.

---

## 2 · LiteBIRD Timeline

| Milestone | Date |
|-----------|------|
| Expected launch | ~2032 |
| Expected first birefringence results | ~2033–2034 |
| Angular sensitivity goal | σ(β) ≈ 0.01° (sufficient to resolve both modes) |
| Decision expected | ~2034 |

The LiteBIRD sensitivity goal of σ(β) ≈ 0.01° is sufficient to:
1. Distinguish the two predicted modes (separated by ~0.058°).
2. Test whether β falls in the predicted gap [0.29°, 0.31°].
3. Confirm or falsify the outer admissible window [0.22°, 0.38°].

**This is a hard, unambiguous falsification test with a definite experimental timeline.**

---

## 3 · Secondary Predictions and Status

The birefringence measurement is the primary falsifier, but two secondary CMB
predictions are already being tested:

| Prediction | UM Value | Current Constraint | Status |
|-----------|----------|-------------------|--------|
| Scalar spectral index n_s | 0.9635 | Planck: 0.9649 ± 0.0042 | ✅ CONSISTENT (0.33σ) |
| Tensor-to-scalar ratio r | 0.0315 | BICEP/Keck: r < 0.036 | ✅ CONSISTENT (inside bound) |

**r falsification condition:** r < 0.010 (measured with high confidence by CMB-S4 ~2030)
would exclude the UM prediction and effectively pre-falsify a key component of
the birefringence mechanism before LiteBIRD launches.

---

## 4 · Machine-Readable Registry

All UM predictions (including those above) are registered in:

```
src/core/prediction_registry.py
```

Key API:

```python
from src.core.prediction_registry import litebird_window, falsifiable_predictions

# Get LiteBIRD window
window = litebird_window()
# {'admissible_window_deg': [0.22, 0.38], 'predicted_gap_deg': [0.29, 0.31], ...}

# All predictions with upcoming experiments
future = falsifiable_predictions()
```

The registry provides machine-readable falsification conditions for all 9 UM
predictions, enabling automated monitoring as experimental results become available.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
