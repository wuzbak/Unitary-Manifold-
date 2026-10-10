# AZ Polariton Vortex Analyzer — Product 29

**Folder:** `12-AZ-IP/29-az-polariton-vortex-analyzer/`
**Version:** 1.1.0
**TRL:** TRL-2 (analysis software; validated only against synthetic data)
**Status:** Active — Phase 0 of article-354's polariton-vortex roadmap, now a runnable web product

## What this is

A signal-processing pipeline (`extract_feature_velocity_curve`,
`compare_to_prediction`) that takes real femtosecond pump-probe frame data —
tracked feature position, timestamp, wavefront half-angle — and extracts the
measured feature velocity as a function of half-angle, in the same `v/c`
units `src/materials/polariton_vortex.py` already uses for its prediction
curve (critical half-angle θ_c ≈ 18.93°, from the braided sound speed
c_s = 12/37).

No information travels faster than light in this prediction — only a
geometric crossing point does, the way a pair of scissors can "close" faster
than light without moving matter that fast. This product does not run or
claim any lab measurement; it is built and unit-tested against synthetic
data constructed to exactly reproduce `vortex_speed_ratio()`, so that it is
ready the moment a real dataset (e.g. from Kaminer et al., Nature 2026, or a
follow-up hBN run) is available.

## Epistemic status

Phase 0 only (analysis pipeline). Phase 1 (correspondence with an existing
optics group to check angular resolution near θ_c) and Phase 2 (publication-
grade comparison) are external-dependent and not part of this product.

## Usage

```bash
python 12-AZ-IP/29-az-polariton-vortex-analyzer/run.py
```

```python
from az_polariton_vortex_analyzer import PumpProbeFrame, extract_feature_velocity_curve, compare_to_prediction

frames = [...]  # real pump-probe frames
curve = extract_feature_velocity_curve(frames)
result = compare_to_prediction(curve)
```

## Running as a web product

A stdlib-only JSON API plus a static dashboard sits over the same pipeline above
(`app/server.py` dispatches to `dispatch_api_request`, covered by `tests/test_api.py`):

```bash
python 12-AZ-IP/29-az-polariton-vortex-analyzer/run.py serve --port 8129
# then open http://127.0.0.1:8129/
```

Endpoints: `GET /api/status`, `GET /api/prediction?c_s=`, `GET /api/demo-comparison?c_s=`
(the latter uses synthetic frames built directly on the prediction curve — a
self-consistency check, not a real dataset comparison).

## Tests

```bash
python -m pytest 12-AZ-IP/29-az-polariton-vortex-analyzer/tests -q
```

## Sources

- `src/materials/polariton_vortex.py`
- Kaminer et al. — superluminal optical phase singularities in hexagonal boron nitride, Nature (2026)
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #2

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
