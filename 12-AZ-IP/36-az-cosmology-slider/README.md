# AZ Differentiable Cosmology Slider — Product 36

**Folder:** `12-AZ-IP/36-az-cosmology-slider/`
**Version:** 1.1.0
**TRL:** TRL-4 (working differentiable backend API, now a runnable web product)
**Status:** Active — Phases 1-2 of article-354's "Differentiable backend -> education slider" roadmap

## What this is

`src/core/jax_backend.py` already computes `n_s` and its exact gradients
`dn_s/dphi0`, `dn_s/dn_w` via `jax.grad`. This product wraps that function
into a slider-ready API: `slider_reading(phi0, n_w)` returns the predicted
`n_s`, both partial derivatives, the gap to the Planck 2018 measured value,
and a `closer_if_phi0_increases` flag a UI could use to show which
direction a slider should move to shrink that gap. `sweep_phi0()` evaluates
a sequence of positions for a continuous slider widget to render.

## Epistemic status

This is an educational gradient display over an already-tested
differentiable backend — Phases 1-2 of the article's roadmap are both
done now. JAX is an optional dependency; `JAX_AVAILABLE` and `require_jax()`
let callers detect and handle its absence instead of crashing at import
time, matching this repository's existing optional-dependency convention
(see `src/core/jax_backend.py`, `src/core/formal_proof_hardening.py`). The
`/api/slider` and `/api/sweep` endpoints return HTTP 503 with a clear error
if JAX is unavailable at serve time.

## Usage

```bash
python 12-AZ-IP/36-az-cosmology-slider/run.py --phi0 10.0 --n-w 5.0
python 12-AZ-IP/36-az-cosmology-slider/run.py --phi0 10.0 --sweep
```

## Running as a web product

```bash
python 12-AZ-IP/36-az-cosmology-slider/run.py --serve --port 8136
```

Then visit `http://127.0.0.1:8136/` for the slider dashboard, or query the
JSON API directly:

- `GET /api/status` — product metadata, JAX availability, Planck/UM `n_s`
- `GET /api/slider?phi0=&n_w=` — `slider_reading(phi0, n_w)` as JSON
- `GET /api/sweep?n_w=&phi0_min=&phi0_max=&n_points=` — a sequence of readings

## Tests

```bash
python -m pytest 12-AZ-IP/36-az-cosmology-slider/tests -q
```

## Sources

- `src/core/jax_backend.py` — `grad_spectral_index`
- `src/core/cmb_polarisation.py` — `N_S = 0.9649` (Planck 2018)
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #9

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
