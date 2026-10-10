# AZ Materials Screening Engine — Product 30

**Folder:** `12-AZ-IP/30-az-materials-screening-engine/`
**Version:** 1.1.0
**TRL:** TRL-2 (formula consolidation + ranking tool; not validated against measured data yet)
**Status:** Active — Phase 0/1 of article-354's materials-screening roadmap, now a runnable web product

## What this is

Pulls the critical-angle, Froehlich-polaron, and metamaterial formulas out of
`src/materials/polariton_vortex.py`, `froehlich_polaron.py`, and
`metamaterials.py` into one shared, material-parameter-agnostic function
signature: `MaterialCandidate(alpha, omega_lo_mev, m_band_me, epsilon_r,
mu_r)` in, polaron binding energy, effective mass ratio, polaron radius,
metamaterial flags, and the framework's fixed critical half-angle out.

`rank_candidates()` ranks a list of candidates by how far their Froehlich
coupling `alpha` diverges from the UM-predicted canonical value
(`froehlich_alpha_um(5, 5, 7)`) — the candidates with the largest divergence
are the ones where a measurement would most cleanly separate this
framework's prediction from a generic continuum estimate, i.e. the best new
falsification targets.

## Epistemic status

This is Phase 0/1 only: formula consolidation and ranking logic. Phase 1's
validated-database step (checking the consolidated formula against 3-4
materials with already-published polaron/polariton measurements) and
Phase 2's inversion against a real candidate-material database (e.g. the
Materials Project) are **not** part of this product yet — `run.py` ships
three illustrative demo candidates with placeholder parameters, not measured
values.

## Usage

```bash
python 12-AZ-IP/30-az-materials-screening-engine/run.py
```

```python
from az_materials_screening_engine import MaterialCandidate, rank_candidates

candidates = [MaterialCandidate("my-material", alpha=0.4, omega_lo_mev=120.0, m_band_me=0.1, epsilon_r=3.5)]
ranked = rank_candidates(candidates)
```

## Running as a web product

A stdlib-only JSON API plus a static dashboard sits over the same formulas above
(`app/server.py` dispatches to `dispatch_api_request`, covered by `tests/test_api.py`):

```bash
python 12-AZ-IP/30-az-materials-screening-engine/run.py serve --port 8130
# then open http://127.0.0.1:8130/
```

Endpoints: `GET /api/status`, `GET /api/screen?name=&alpha=&omega_lo_mev=&m_band_me=&epsilon_r=`,
`GET /api/demo-rank` (the 3 built-in demo candidates).

## Tests

```bash
python -m pytest 12-AZ-IP/30-az-materials-screening-engine/tests -q
```

## Sources

- `src/materials/polariton_vortex.py`, `froehlich_polaron.py`, `metamaterials.py`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #3

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
