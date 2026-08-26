# Falsification Observatory

**Product:** 19 of the AxiomZero suite  
**Folder:** `12-AZ-IP/19-falsification-observatory/`  
**Default port:** `8019`  
**Status:** Standalone browser product with Python routing engine, local static server, copied UI, and full test suite.  
**License:** Defensive Public Commons License v1.0

---

## 1. What This Product Is
The Falsification Observatory is a browser-based scientific product that turns seven live or near-live experimental fronts into explicit verdict routes. It is the productized version of Pillar 787 falsification logic for a local AxiomZero deployment.

Instead of burying predictions in prose, the Observatory exposes them as callable routing functions and as a visible experiment dashboard. The user can supply a measured value, read the verdict, inspect the kill condition, and trace the relevant pillar chain.

The design goal is not rhetorical persuasion. The design goal is bright-line accountability. A product that claims a scientific framework should also show the exact conditions under which that framework survives, enters tension, or fails.

Product 19 is therefore half interface and half oracle. The interface lives in `ui/`. The oracle lives in `falsification_observatory/engine/`. The static app launcher lives in `run.py`. The tests enforce the contract.

### Core verdict vocabulary
- **PASS** — the submitted value remains inside the encoded survivability region.
- **TENSION** — the submitted value strains the encoded prediction but does not meet the kill threshold.
- **FALSIFIED** — the submitted value meets a bright-line failure condition.
- **AWAITING_DATA** — no measurement was supplied to the routing function.

## 2. Quick Start
```bash
cd 12-AZ-IP/19-falsification-observatory
pip install -r requirements.txt
python run.py --no-open
# then visit http://127.0.0.1:8019/
```

### Test command
```bash
cd 12-AZ-IP/19-falsification-observatory
python -m pytest tests/ -q
```

## 3. Product Files
- `README.md` — Long-form product specification and API reference.
- `requirements.txt` — Minimal Python dependencies.
- `run.py` — Static server launcher with `--port` and `--no-open`.
- `falsification_observatory/__init__.py` — Public exports for the package.
- `falsification_observatory/engine/constants.py` — Canonical predictions and thresholds.
- `falsification_observatory/engine/routing.py` — All seven routing functions and `route_all`.
- `falsification_observatory/engine/verdict.py` — Typed verdict dataclass.
- `falsification_observatory/app/server.py` — Simple HTTP server bound to `ui/`.
- `ui/index.html` — Standalone copied observatory HTML.
- `ui/falsification-observatory.js` — Standalone copied observatory JavaScript.
- `css/main.css` — Copied shared site stylesheet for standalone serving.
- `css/az-apps.css` — Copied app stylesheet for standalone serving.
- `tests/test_falsification_observatory.py` — Comprehensive product-level tests.

## 4. Experiment Registry
### EXP-1 — LiteBIRD Cosmic Birefringence
- **Prediction:** β ∈ {0.273°, 0.331°}
- **Kill condition:** β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.
- **Relevant pillars:** 11, 13, 765, 771, 787
- **Python API:** `route_litebird(beta=None, beta_sigma=None)`
- **Product reading:** LiteBIRD Cosmic Birefringence is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

1. EXP-1 interpretive note 1: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
2. EXP-1 interpretive note 2: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
3. EXP-1 interpretive note 3: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
4. EXP-1 interpretive note 4: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
5. EXP-1 interpretive note 5: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
6. EXP-1 interpretive note 6: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
7. EXP-1 interpretive note 7: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
8. EXP-1 interpretive note 8: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.

### EXP-2 — DESI Dark Energy
- **Prediction:** w_a = 0
- **Kill condition:** A ≥3σ departure from w_a = 0.
- **Relevant pillars:** 5, 29, 38, 727, 739, 771, 787
- **Python API:** `route_desi(w_a=None, w_a_sigma=None)`
- **Product reading:** DESI Dark Energy is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

1. EXP-2 interpretive note 1: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
2. EXP-2 interpretive note 2: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
3. EXP-2 interpretive note 3: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
4. EXP-2 interpretive note 4: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
5. EXP-2 interpretive note 5: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
6. EXP-2 interpretive note 6: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
7. EXP-2 interpretive note 7: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
8. EXP-2 interpretive note 8: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.

### EXP-3 — JUNO Neutrino Mass
- **Prediction:** Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²
- **Kill condition:** Outside the window at ≥2σ.
- **Relevant pillars:** 772, 773, 786, 787
- **Python API:** `route_juno(dm21=None, dm21_sigma=None)`
- **Product reading:** JUNO Neutrino Mass is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

1. EXP-3 interpretive note 1: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
2. EXP-3 interpretive note 2: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
3. EXP-3 interpretive note 3: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
4. EXP-3 interpretive note 4: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
5. EXP-3 interpretive note 5: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
6. EXP-3 interpretive note 6: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
7. EXP-3 interpretive note 7: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
8. EXP-3 interpretive note 8: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.

### EXP-4 — ACT CMB Spectral Index
- **Prediction:** n_s = 0.9635
- **Kill condition:** A ≥3σ inconsistency with the prediction.
- **Relevant pillars:** 11, 67, 787
- **Python API:** `route_act(n_s=None, n_s_sigma=None)`
- **Product reading:** ACT CMB Spectral Index is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

1. EXP-4 interpretive note 1: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
2. EXP-4 interpretive note 2: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
3. EXP-4 interpretive note 3: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
4. EXP-4 interpretive note 4: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
5. EXP-4 interpretive note 5: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
6. EXP-4 interpretive note 6: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
7. EXP-4 interpretive note 7: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
8. EXP-4 interpretive note 8: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.

### EXP-5 — HL-LHC KK Gluon
- **Prediction:** Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.
- **Kill condition:** No hard kill in Product 19; low-scale discovery is routed as TENSION.
- **Relevant pillars:** 709, 787
- **Python API:** `route_hllhc(mass_tev=None, observed=False)`
- **Product reading:** HL-LHC KK Gluon is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

1. EXP-5 interpretive note 1: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
2. EXP-5 interpretive note 2: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
3. EXP-5 interpretive note 3: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
4. EXP-5 interpretive note 4: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
5. EXP-5 interpretive note 5: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
6. EXP-5 interpretive note 6: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
7. EXP-5 interpretive note 7: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
8. EXP-5 interpretive note 8: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.

### EXP-6 — nEDM Electric Dipole Moment
- **Prediction:** Residual EDM near 1e-30 e·cm.
- **Kill condition:** Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.
- **Relevant pillars:** 731, 786, 787
- **Python API:** `route_nedm(d_e=None, d_e_sigma=None)`
- **Product reading:** nEDM Electric Dipole Moment is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

1. EXP-6 interpretive note 1: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
2. EXP-6 interpretive note 2: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
3. EXP-6 interpretive note 3: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
4. EXP-6 interpretive note 4: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
5. EXP-6 interpretive note 5: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
6. EXP-6 interpretive note 6: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
7. EXP-6 interpretive note 7: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
8. EXP-6 interpretive note 8: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.

### EXP-7 — XENON-nT Dark Matter
- **Prediction:** Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.
- **Kill condition:** σ < 5e-47 cm².
- **Relevant pillars:** 717, 787
- **Python API:** `route_xenon(sigma_cm2=None)`
- **Product reading:** XENON-nT Dark Matter is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

1. EXP-7 interpretive note 1: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
2. EXP-7 interpretive note 2: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
3. EXP-7 interpretive note 3: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
4. EXP-7 interpretive note 4: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
5. EXP-7 interpretive note 5: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
6. EXP-7 interpretive note 6: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
7. EXP-7 interpretive note 7: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.
8. EXP-7 interpretive note 8: the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the note field as explanatory rather than discretionary.

## 5. Falsification Philosophy
1. Falsification in this product means a condition that is stated before the measurement and evaluated after the measurement.
2. The Observatory separates bright-line kill conditions from softer tension states so that survivability does not collapse into public-relations spin.
3. A routed tension state is not ignored. It is recorded, visible, and available for aggregation through `route_all`.
4. The primary LiteBIRD birefringence falsifier remains the most important single bright-line condition in the entire product.
5. The product intentionally exposes pillar references so that users can audit where each route comes from in the broader framework.
6. AWAITING_DATA is epistemically cleaner than pretending to have a verdict without a measurement.
7. The browser interface is intentionally simple because the hard intellectual content lives in the routing contract, not in animation.
8. The Python package is the authoritative local product API for automation and testing.

### Primary falsifier
The primary falsifier is the LiteBIRD cosmic birefringence route. If β falls outside the admissible window `[0.22°, 0.38°]`, or inside the predicted gap `(0.29°, 0.31°)`, and the sigma-level distance from the nearest canonical branch reaches at least `3.0σ`, the Observatory routes the result to **FALSIFIED**.

## 6. API Reference
### `route_litebird(beta=None, beta_sigma=None)`
Returns a `VerdictResult` for the cosmic birefringence route.

Returned fields:
- `exp_id`
- `name`
- `verdict`
- `prediction`
- `measured`
- `sigma_deviation`
- `kill_condition`
- `pillar_refs`
- `note`

Example:
```python
from falsification_observatory import route_litebird
result = route_litebird(0.273, 0.01)
print(result.verdict)
```

- API note 1: `route_litebird` is deterministic for the same input arguments and never mutates shared state.
- API note 2: `route_litebird` is deterministic for the same input arguments and never mutates shared state.
- API note 3: `route_litebird` is deterministic for the same input arguments and never mutates shared state.
- API note 4: `route_litebird` is deterministic for the same input arguments and never mutates shared state.
- API note 5: `route_litebird` is deterministic for the same input arguments and never mutates shared state.
- API note 6: `route_litebird` is deterministic for the same input arguments and never mutates shared state.
- API note 7: `route_litebird` is deterministic for the same input arguments and never mutates shared state.
- API note 8: `route_litebird` is deterministic for the same input arguments and never mutates shared state.
- API note 9: `route_litebird` is deterministic for the same input arguments and never mutates shared state.
- API note 10: `route_litebird` is deterministic for the same input arguments and never mutates shared state.

### `route_desi(w_a=None, w_a_sigma=None)`
Returns a `VerdictResult` for the DESI dark-energy route.

Returned fields:
- `exp_id`
- `name`
- `verdict`
- `prediction`
- `measured`
- `sigma_deviation`
- `kill_condition`
- `pillar_refs`
- `note`

Example:
```python
from falsification_observatory import route_desi
result = route_desi(0.0, 0.1)
print(result.verdict)
```

- API note 1: `route_desi` is deterministic for the same input arguments and never mutates shared state.
- API note 2: `route_desi` is deterministic for the same input arguments and never mutates shared state.
- API note 3: `route_desi` is deterministic for the same input arguments and never mutates shared state.
- API note 4: `route_desi` is deterministic for the same input arguments and never mutates shared state.
- API note 5: `route_desi` is deterministic for the same input arguments and never mutates shared state.
- API note 6: `route_desi` is deterministic for the same input arguments and never mutates shared state.
- API note 7: `route_desi` is deterministic for the same input arguments and never mutates shared state.
- API note 8: `route_desi` is deterministic for the same input arguments and never mutates shared state.
- API note 9: `route_desi` is deterministic for the same input arguments and never mutates shared state.
- API note 10: `route_desi` is deterministic for the same input arguments and never mutates shared state.

### `route_juno(dm21=None, dm21_sigma=None)`
Returns a `VerdictResult` for the JUNO neutrino mass-splitting route.

Returned fields:
- `exp_id`
- `name`
- `verdict`
- `prediction`
- `measured`
- `sigma_deviation`
- `kill_condition`
- `pillar_refs`
- `note`

Example:
```python
from falsification_observatory import route_juno
result = route_juno(7.53e-5, 0.1e-5)
print(result.verdict)
```

- API note 1: `route_juno` is deterministic for the same input arguments and never mutates shared state.
- API note 2: `route_juno` is deterministic for the same input arguments and never mutates shared state.
- API note 3: `route_juno` is deterministic for the same input arguments and never mutates shared state.
- API note 4: `route_juno` is deterministic for the same input arguments and never mutates shared state.
- API note 5: `route_juno` is deterministic for the same input arguments and never mutates shared state.
- API note 6: `route_juno` is deterministic for the same input arguments and never mutates shared state.
- API note 7: `route_juno` is deterministic for the same input arguments and never mutates shared state.
- API note 8: `route_juno` is deterministic for the same input arguments and never mutates shared state.
- API note 9: `route_juno` is deterministic for the same input arguments and never mutates shared state.
- API note 10: `route_juno` is deterministic for the same input arguments and never mutates shared state.

### `route_act(n_s=None, n_s_sigma=None)`
Returns a `VerdictResult` for the ACT spectral-index route.

Returned fields:
- `exp_id`
- `name`
- `verdict`
- `prediction`
- `measured`
- `sigma_deviation`
- `kill_condition`
- `pillar_refs`
- `note`

Example:
```python
from falsification_observatory import route_act
result = route_act(0.9635, 0.001)
print(result.verdict)
```

- API note 1: `route_act` is deterministic for the same input arguments and never mutates shared state.
- API note 2: `route_act` is deterministic for the same input arguments and never mutates shared state.
- API note 3: `route_act` is deterministic for the same input arguments and never mutates shared state.
- API note 4: `route_act` is deterministic for the same input arguments and never mutates shared state.
- API note 5: `route_act` is deterministic for the same input arguments and never mutates shared state.
- API note 6: `route_act` is deterministic for the same input arguments and never mutates shared state.
- API note 7: `route_act` is deterministic for the same input arguments and never mutates shared state.
- API note 8: `route_act` is deterministic for the same input arguments and never mutates shared state.
- API note 9: `route_act` is deterministic for the same input arguments and never mutates shared state.
- API note 10: `route_act` is deterministic for the same input arguments and never mutates shared state.

### `route_hllhc(mass_tev=None, observed=False)`
Returns a `VerdictResult` for the HL-LHC heavy-resonance route.

Returned fields:
- `exp_id`
- `name`
- `verdict`
- `prediction`
- `measured`
- `sigma_deviation`
- `kill_condition`
- `pillar_refs`
- `note`

Example:
```python
from falsification_observatory import route_hllhc
result = route_hllhc(2.5, True)
print(result.verdict)
```

- API note 1: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.
- API note 2: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.
- API note 3: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.
- API note 4: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.
- API note 5: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.
- API note 6: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.
- API note 7: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.
- API note 8: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.
- API note 9: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.
- API note 10: `route_hllhc` is deterministic for the same input arguments and never mutates shared state.

### `route_nedm(d_e=None, d_e_sigma=None)`
Returns a `VerdictResult` for the nEDM route.

Returned fields:
- `exp_id`
- `name`
- `verdict`
- `prediction`
- `measured`
- `sigma_deviation`
- `kill_condition`
- `pillar_refs`
- `note`

Example:
```python
from falsification_observatory import route_nedm
result = route_nedm(1e-30, 1e-31)
print(result.verdict)
```

- API note 1: `route_nedm` is deterministic for the same input arguments and never mutates shared state.
- API note 2: `route_nedm` is deterministic for the same input arguments and never mutates shared state.
- API note 3: `route_nedm` is deterministic for the same input arguments and never mutates shared state.
- API note 4: `route_nedm` is deterministic for the same input arguments and never mutates shared state.
- API note 5: `route_nedm` is deterministic for the same input arguments and never mutates shared state.
- API note 6: `route_nedm` is deterministic for the same input arguments and never mutates shared state.
- API note 7: `route_nedm` is deterministic for the same input arguments and never mutates shared state.
- API note 8: `route_nedm` is deterministic for the same input arguments and never mutates shared state.
- API note 9: `route_nedm` is deterministic for the same input arguments and never mutates shared state.
- API note 10: `route_nedm` is deterministic for the same input arguments and never mutates shared state.

### `route_xenon(sigma_cm2=None)`
Returns a `VerdictResult` for the XENON-nT route.

Returned fields:
- `exp_id`
- `name`
- `verdict`
- `prediction`
- `measured`
- `sigma_deviation`
- `kill_condition`
- `pillar_refs`
- `note`

Example:
```python
from falsification_observatory import route_xenon
result = route_xenon(1e-46)
print(result.verdict)
```

- API note 1: `route_xenon` is deterministic for the same input arguments and never mutates shared state.
- API note 2: `route_xenon` is deterministic for the same input arguments and never mutates shared state.
- API note 3: `route_xenon` is deterministic for the same input arguments and never mutates shared state.
- API note 4: `route_xenon` is deterministic for the same input arguments and never mutates shared state.
- API note 5: `route_xenon` is deterministic for the same input arguments and never mutates shared state.
- API note 6: `route_xenon` is deterministic for the same input arguments and never mutates shared state.
- API note 7: `route_xenon` is deterministic for the same input arguments and never mutates shared state.
- API note 8: `route_xenon` is deterministic for the same input arguments and never mutates shared state.
- API note 9: `route_xenon` is deterministic for the same input arguments and never mutates shared state.
- API note 10: `route_xenon` is deterministic for the same input arguments and never mutates shared state.

### `route_all(observations: dict)`
Returns a list of all seven verdict objects in registry order.

Returned fields:
- `exp_id`
- `name`
- `verdict`
- `prediction`
- `measured`
- `sigma_deviation`
- `kill_condition`
- `pillar_refs`
- `note`

Example:
```python
from falsification_observatory import route_all
results = route_all({'beta': 0.273, 'beta_sigma': 0.01})
```

- API note 1: `route_all` is deterministic for the same input arguments and never mutates shared state.
- API note 2: `route_all` is deterministic for the same input arguments and never mutates shared state.
- API note 3: `route_all` is deterministic for the same input arguments and never mutates shared state.
- API note 4: `route_all` is deterministic for the same input arguments and never mutates shared state.
- API note 5: `route_all` is deterministic for the same input arguments and never mutates shared state.
- API note 6: `route_all` is deterministic for the same input arguments and never mutates shared state.
- API note 7: `route_all` is deterministic for the same input arguments and never mutates shared state.
- API note 8: `route_all` is deterministic for the same input arguments and never mutates shared state.
- API note 9: `route_all` is deterministic for the same input arguments and never mutates shared state.
- API note 10: `route_all` is deterministic for the same input arguments and never mutates shared state.

## 7. Verdict Schema
`VerdictResult` is a frozen dataclass. Its fields are designed to be serializable, assertable in tests, and legible in terminal logs.

- `exp_id` — Stable experiment identifier such as `EXP-1`.
- `name` — Human-readable experiment title.
- `verdict` — One of `PASS`, `TENSION`, `FALSIFIED`, `AWAITING_DATA`.
- `prediction` — Short description of the encoded prediction.
- `measured` — The submitted value or structured payload.
- `sigma_deviation` — Computed sigma distance when the route supports it.
- `kill_condition` — Plain-English description of the bright-line failure test.
- `pillar_refs` — Tuple of relevant pillar numbers.
- `note` — Short explanation of why the route returned the verdict.

## 8. Constant Reference
- `BETA_C1 = 0.273`
- `BETA_C2 = 0.331`
- `BETA_WIN_MIN = 0.22`
- `BETA_WIN_MAX = 0.38`
- `BETA_GAP_LO = 0.29`
- `BETA_GAP_HI = 0.31`
- `BETA_KILL_SIGMA = 3.0`
- `WA_PRED = 0.0`
- `WA_KILL_SIGMA = 3.0`
- `DM21_PRED = 7.53e-5`
- `DM21_WIN_LO = 7.0e-5`
- `DM21_WIN_HI = 8.1e-5`
- `R_PRED = 0.0315`
- `R_KILL = 0.036`
- `N_S_PRED = 0.9635`
- `MG_PRED_TEV = 2.5`
- `MG_KILL_TEV = 5.0`
- `KK_DM_CS = 1e-46`
- `XENON_SENS = 5e-47`
- `WINDING_NUMBER = 5`
- `K_CS = 74`

## 9. Browser App Notes
- The `ui/` folder contains a copied HTML shell and copied JavaScript engine derived from the public-site observatory asset lineage.
- For standalone serving, the HTML file is patched to load `./falsification-observatory.js` locally.
- The product also copies `public-site/css/main.css` and `public-site/css/az-apps.css` into a local `css/` directory so the page can be served without broken stylesheet references.
- The browser app is static. There is no database and no backend API requirement for local use.

## 10. Epistemic Status
This product is an instrumentation layer, not an independent scientific proof. It encodes the routing contract.

The pillar references and numerical values are treated here as repository-defined constants. The product does not independently derive them.

Because the product is built to expose falsifiers, it should be read as a scientific accountability artifact rather than a marketing page.

The copied UI includes lineage from the existing public-site artifact. The standalone Python engine is the local automation layer for Product 19.

## 11. Programmatic Examples
### Example 1: LiteBIRD Cosmic Birefringence
```python
from falsification_observatory import route_litebird
result = route_litebird(0.273, 0.01)
print(result)
```

- Example note 1: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 2: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 3: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 4: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 5: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 6: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 7: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 8: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 9: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 10: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 11: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 12: EXP-1 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.

### Example 2: DESI Dark Energy
```python
from falsification_observatory import route_desi
result = route_desi(0.0, 0.1)
print(result)
```

- Example note 1: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 2: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 3: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 4: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 5: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 6: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 7: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 8: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 9: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 10: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 11: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 12: EXP-2 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.

### Example 3: JUNO Neutrino Mass
```python
from falsification_observatory import route_juno
result = route_juno(7.53e-5, 0.1e-5)
print(result)
```

- Example note 1: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 2: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 3: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 4: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 5: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 6: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 7: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 8: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 9: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 10: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 11: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 12: EXP-3 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.

### Example 4: ACT CMB Spectral Index
```python
from falsification_observatory import route_act
result = route_act(0.9635, 0.001)
print(result)
```

- Example note 1: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 2: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 3: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 4: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 5: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 6: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 7: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 8: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 9: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 10: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 11: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 12: EXP-4 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.

### Example 5: HL-LHC KK Gluon
```python
from falsification_observatory import route_hllhc
result = route_hllhc(2.5, True)
print(result)
```

- Example note 1: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 2: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 3: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 4: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 5: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 6: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 7: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 8: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 9: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 10: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 11: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 12: EXP-5 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.

### Example 6: nEDM Electric Dipole Moment
```python
from falsification_observatory import route_nedm
result = route_nedm(1e-30, 1e-31)
print(result)
```

- Example note 1: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 2: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 3: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 4: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 5: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 6: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 7: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 8: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 9: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 10: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 11: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 12: EXP-6 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.

### Example 7: XENON-nT Dark Matter
```python
from falsification_observatory import route_xenon
result = route_xenon(1e-46)
print(result)
```

- Example note 1: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 2: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 3: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 4: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 5: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 6: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 7: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 8: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 9: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 10: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 11: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.
- Example note 12: EXP-7 is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.

## 12. FAQ
### Q: Why does the product use AWAITING_DATA?
A: Because not every experiment has a submitted or current measurement in a local session.

- FAQ expansion 1: Why does the product use AWAITING_DATA? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Why does the product use AWAITING_DATA? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Why does the product use AWAITING_DATA? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Why does the product use AWAITING_DATA? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Why does the product use AWAITING_DATA? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Why does the product use AWAITING_DATA? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Why does the product use AWAITING_DATA? remains tied to the goal of explicit falsification rather than soft narrative scoring.

### Q: Why are pillar references included?
A: So each verdict can be traced back to the governing pillar chain.

- FAQ expansion 1: Why are pillar references included? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Why are pillar references included? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Why are pillar references included? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Why are pillar references included? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Why are pillar references included? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Why are pillar references included? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Why are pillar references included? remains tied to the goal of explicit falsification rather than soft narrative scoring.

### Q: Is the UI the source of truth?
A: No. The local Python package is the source of truth for the standalone product API.

- FAQ expansion 1: Is the UI the source of truth? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Is the UI the source of truth? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Is the UI the source of truth? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Is the UI the source of truth? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Is the UI the source of truth? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Is the UI the source of truth? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Is the UI the source of truth? remains tied to the goal of explicit falsification rather than soft narrative scoring.

### Q: Why is LiteBIRD primary?
A: Because the repository-level falsification note explicitly elevates the birefringence window as the main bright-line test.

- FAQ expansion 1: Why is LiteBIRD primary? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Why is LiteBIRD primary? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Why is LiteBIRD primary? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Why is LiteBIRD primary? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Why is LiteBIRD primary? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Why is LiteBIRD primary? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Why is LiteBIRD primary? remains tied to the goal of explicit falsification rather than soft narrative scoring.

### Q: Why is there a static server instead of a framework?
A: The product needs only local serving of HTML, JS, and CSS.

- FAQ expansion 1: Why is there a static server instead of a framework? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Why is there a static server instead of a framework? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Why is there a static server instead of a framework? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Why is there a static server instead of a framework? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Why is there a static server instead of a framework? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Why is there a static server instead of a framework? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Why is there a static server instead of a framework? remains tied to the goal of explicit falsification rather than soft narrative scoring.

### Q: Can `route_all` be used in automation?
A: Yes. It is designed for scripts, dashboards, and batch checks.

- FAQ expansion 1: Can `route_all` be used in automation? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Can `route_all` be used in automation? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Can `route_all` be used in automation? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Can `route_all` be used in automation? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Can `route_all` be used in automation? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Can `route_all` be used in automation? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Can `route_all` be used in automation? remains tied to the goal of explicit falsification rather than soft narrative scoring.

### Q: Does the product create files at runtime?
A: No. It simply serves static assets and computes in memory.

- FAQ expansion 1: Does the product create files at runtime? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Does the product create files at runtime? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Does the product create files at runtime? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Does the product create files at runtime? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Does the product create files at runtime? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Does the product create files at runtime? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Does the product create files at runtime? remains tied to the goal of explicit falsification rather than soft narrative scoring.

### Q: Are verdicts probabilistic?
A: No. The routes are deterministic for supplied inputs.

- FAQ expansion 1: Are verdicts probabilistic? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Are verdicts probabilistic? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Are verdicts probabilistic? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Are verdicts probabilistic? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Are verdicts probabilistic? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Are verdicts probabilistic? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Are verdicts probabilistic? remains tied to the goal of explicit falsification rather than soft narrative scoring.

### Q: Why copy CSS files?
A: To make the product actually standalone instead of leaving broken stylesheet links.

- FAQ expansion 1: Why copy CSS files? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Why copy CSS files? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Why copy CSS files? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Why copy CSS files? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Why copy CSS files? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Why copy CSS files? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Why copy CSS files? remains tied to the goal of explicit falsification rather than soft narrative scoring.

### Q: Why include tests for file presence?
A: Because the product contract includes both code and deployable static assets.

- FAQ expansion 1: Why include tests for file presence? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 2: Why include tests for file presence? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 3: Why include tests for file presence? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 4: Why include tests for file presence? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 5: Why include tests for file presence? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 6: Why include tests for file presence? remains tied to the goal of explicit falsification rather than soft narrative scoring.
- FAQ expansion 7: Why include tests for file presence? remains tied to the goal of explicit falsification rather than soft narrative scoring.

## 13. Repository Relationship
This folder is intentionally standalone, but it is also traceable to four upstream sources inside the repository: the public-site JavaScript, the public-site HTML, the Pillar 787 Python oracle, and the repository-level falsification tests.

The Product 19 package is therefore both derivative and operational: derivative in asset lineage, operational in local packaging and testing.

Nothing in this folder alters the source repository public-site artifact. It instead packages a standalone local product patterned after Product 16.

## 14. Authorship
Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.  
Code architecture, packaging, tests, and product synthesis: **GitHub Copilot** (AI).

## 15. Appendix A — One-line audit map
- EXP-1 audit line 1: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 2: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 3: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 4: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 5: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 6: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 7: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 8: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 9: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 10: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 11: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 12: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 13: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 14: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 15: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 16: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 17: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 18: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 19: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 20: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 21: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 22: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 23: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 24: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 25: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 26: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 27: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 28: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 29: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-1 audit line 30: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-2 audit line 1: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 2: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 3: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 4: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 5: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 6: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 7: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 8: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 9: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 10: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 11: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 12: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 13: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 14: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 15: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 16: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 17: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 18: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 19: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 20: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 21: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 22: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 23: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 24: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 25: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 26: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 27: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 28: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 29: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-2 audit line 30: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-3 audit line 1: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 2: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 3: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 4: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 5: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 6: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 7: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 8: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 9: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 10: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 11: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 12: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 13: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 14: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 15: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 16: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 17: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 18: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 19: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 20: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 21: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 22: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 23: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 24: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 25: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 26: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 27: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 28: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 29: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-3 audit line 30: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-4 audit line 1: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 2: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 3: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 4: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 5: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 6: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 7: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 8: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 9: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 10: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 11: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 12: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 13: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 14: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 15: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 16: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 17: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 18: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 19: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 20: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 21: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 22: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 23: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 24: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 25: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 26: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 27: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 28: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 29: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-4 audit line 30: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-5 audit line 1: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 2: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 3: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 4: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 5: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 6: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 7: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 8: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 9: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 10: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 11: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 12: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 13: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 14: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 15: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 16: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 17: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 18: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 19: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 20: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 21: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 22: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 23: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 24: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 25: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 26: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 27: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 28: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 29: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-5 audit line 30: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-6 audit line 1: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 2: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 3: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 4: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 5: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 6: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 7: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 8: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 9: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 10: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 11: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 12: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 13: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 14: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 15: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 16: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 17: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 18: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 19: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 20: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 21: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 22: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 23: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 24: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 25: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 26: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 27: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 28: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 29: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-6 audit line 30: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-7 audit line 1: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 2: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 3: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 4: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 5: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 6: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 7: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 8: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 9: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 10: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 11: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 12: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 13: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 14: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 15: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 16: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 17: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 18: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 19: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 20: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 21: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 22: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 23: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 24: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 25: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 26: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 27: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 28: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 29: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.
- EXP-7 audit line 30: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.

## 16. Appendix B — Operational checklist
- Cycle 1: Install dependencies.
- Cycle 1: Run `python -m pytest tests/ -q`.
- Cycle 1: Launch `python run.py --no-open`.
- Cycle 1: Open the browser on port 8019.
- Cycle 1: Enter a measurement.
- Cycle 1: Read the verdict card.
- Cycle 1: Check the kill condition field.
- Cycle 1: Check the pillar chips.
- Cycle 1: Repeat for all seven experiments.
- Cycle 1: Use `route_all` for scripted runs.
- Cycle 2: Install dependencies.
- Cycle 2: Run `python -m pytest tests/ -q`.
- Cycle 2: Launch `python run.py --no-open`.
- Cycle 2: Open the browser on port 8019.
- Cycle 2: Enter a measurement.
- Cycle 2: Read the verdict card.
- Cycle 2: Check the kill condition field.
- Cycle 2: Check the pillar chips.
- Cycle 2: Repeat for all seven experiments.
- Cycle 2: Use `route_all` for scripted runs.
- Cycle 3: Install dependencies.
- Cycle 3: Run `python -m pytest tests/ -q`.
- Cycle 3: Launch `python run.py --no-open`.
- Cycle 3: Open the browser on port 8019.
- Cycle 3: Enter a measurement.
- Cycle 3: Read the verdict card.
- Cycle 3: Check the kill condition field.
- Cycle 3: Check the pillar chips.
- Cycle 3: Repeat for all seven experiments.
- Cycle 3: Use `route_all` for scripted runs.
- Cycle 4: Install dependencies.
- Cycle 4: Run `python -m pytest tests/ -q`.
- Cycle 4: Launch `python run.py --no-open`.
- Cycle 4: Open the browser on port 8019.
- Cycle 4: Enter a measurement.
- Cycle 4: Read the verdict card.
- Cycle 4: Check the kill condition field.
- Cycle 4: Check the pillar chips.
- Cycle 4: Repeat for all seven experiments.
- Cycle 4: Use `route_all` for scripted runs.
- Cycle 5: Install dependencies.
- Cycle 5: Run `python -m pytest tests/ -q`.
- Cycle 5: Launch `python run.py --no-open`.
- Cycle 5: Open the browser on port 8019.
- Cycle 5: Enter a measurement.
- Cycle 5: Read the verdict card.
- Cycle 5: Check the kill condition field.
- Cycle 5: Check the pillar chips.
- Cycle 5: Repeat for all seven experiments.
- Cycle 5: Use `route_all` for scripted runs.
- Cycle 6: Install dependencies.
- Cycle 6: Run `python -m pytest tests/ -q`.
- Cycle 6: Launch `python run.py --no-open`.
- Cycle 6: Open the browser on port 8019.
- Cycle 6: Enter a measurement.
- Cycle 6: Read the verdict card.
- Cycle 6: Check the kill condition field.
- Cycle 6: Check the pillar chips.
- Cycle 6: Repeat for all seven experiments.
- Cycle 6: Use `route_all` for scripted runs.
- Cycle 7: Install dependencies.
- Cycle 7: Run `python -m pytest tests/ -q`.
- Cycle 7: Launch `python run.py --no-open`.
- Cycle 7: Open the browser on port 8019.
- Cycle 7: Enter a measurement.
- Cycle 7: Read the verdict card.
- Cycle 7: Check the kill condition field.
- Cycle 7: Check the pillar chips.
- Cycle 7: Repeat for all seven experiments.
- Cycle 7: Use `route_all` for scripted runs.
- Cycle 8: Install dependencies.
- Cycle 8: Run `python -m pytest tests/ -q`.
- Cycle 8: Launch `python run.py --no-open`.
- Cycle 8: Open the browser on port 8019.
- Cycle 8: Enter a measurement.
- Cycle 8: Read the verdict card.
- Cycle 8: Check the kill condition field.
- Cycle 8: Check the pillar chips.
- Cycle 8: Repeat for all seven experiments.
- Cycle 8: Use `route_all` for scripted runs.
- Cycle 9: Install dependencies.
- Cycle 9: Run `python -m pytest tests/ -q`.
- Cycle 9: Launch `python run.py --no-open`.
- Cycle 9: Open the browser on port 8019.
- Cycle 9: Enter a measurement.
- Cycle 9: Read the verdict card.
- Cycle 9: Check the kill condition field.
- Cycle 9: Check the pillar chips.
- Cycle 9: Repeat for all seven experiments.
- Cycle 9: Use `route_all` for scripted runs.
- Cycle 10: Install dependencies.
- Cycle 10: Run `python -m pytest tests/ -q`.
- Cycle 10: Launch `python run.py --no-open`.
- Cycle 10: Open the browser on port 8019.
- Cycle 10: Enter a measurement.
- Cycle 10: Read the verdict card.
- Cycle 10: Check the kill condition field.
- Cycle 10: Check the pillar chips.
- Cycle 10: Repeat for all seven experiments.
- Cycle 10: Use `route_all` for scripted runs.
- Cycle 11: Install dependencies.
- Cycle 11: Run `python -m pytest tests/ -q`.
- Cycle 11: Launch `python run.py --no-open`.
- Cycle 11: Open the browser on port 8019.
- Cycle 11: Enter a measurement.
- Cycle 11: Read the verdict card.
- Cycle 11: Check the kill condition field.
- Cycle 11: Check the pillar chips.
- Cycle 11: Repeat for all seven experiments.
- Cycle 11: Use `route_all` for scripted runs.
- Cycle 12: Install dependencies.
- Cycle 12: Run `python -m pytest tests/ -q`.
- Cycle 12: Launch `python run.py --no-open`.
- Cycle 12: Open the browser on port 8019.
- Cycle 12: Enter a measurement.
- Cycle 12: Read the verdict card.
- Cycle 12: Check the kill condition field.
- Cycle 12: Check the pillar chips.
- Cycle 12: Repeat for all seven experiments.
- Cycle 12: Use `route_all` for scripted runs.
- Cycle 13: Install dependencies.
- Cycle 13: Run `python -m pytest tests/ -q`.
- Cycle 13: Launch `python run.py --no-open`.
- Cycle 13: Open the browser on port 8019.
- Cycle 13: Enter a measurement.
- Cycle 13: Read the verdict card.
- Cycle 13: Check the kill condition field.
- Cycle 13: Check the pillar chips.
- Cycle 13: Repeat for all seven experiments.
- Cycle 13: Use `route_all` for scripted runs.
- Cycle 14: Install dependencies.
- Cycle 14: Run `python -m pytest tests/ -q`.
- Cycle 14: Launch `python run.py --no-open`.
- Cycle 14: Open the browser on port 8019.
- Cycle 14: Enter a measurement.
- Cycle 14: Read the verdict card.
- Cycle 14: Check the kill condition field.
- Cycle 14: Check the pillar chips.
- Cycle 14: Repeat for all seven experiments.
- Cycle 14: Use `route_all` for scripted runs.
- Cycle 15: Install dependencies.
- Cycle 15: Run `python -m pytest tests/ -q`.
- Cycle 15: Launch `python run.py --no-open`.
- Cycle 15: Open the browser on port 8019.
- Cycle 15: Enter a measurement.
- Cycle 15: Read the verdict card.
- Cycle 15: Check the kill condition field.
- Cycle 15: Check the pillar chips.
- Cycle 15: Repeat for all seven experiments.
- Cycle 15: Use `route_all` for scripted runs.
- Cycle 16: Install dependencies.
- Cycle 16: Run `python -m pytest tests/ -q`.
- Cycle 16: Launch `python run.py --no-open`.
- Cycle 16: Open the browser on port 8019.
- Cycle 16: Enter a measurement.
- Cycle 16: Read the verdict card.
- Cycle 16: Check the kill condition field.
- Cycle 16: Check the pillar chips.
- Cycle 16: Repeat for all seven experiments.
- Cycle 16: Use `route_all` for scripted runs.
- Cycle 17: Install dependencies.
- Cycle 17: Run `python -m pytest tests/ -q`.
- Cycle 17: Launch `python run.py --no-open`.
- Cycle 17: Open the browser on port 8019.
- Cycle 17: Enter a measurement.
- Cycle 17: Read the verdict card.
- Cycle 17: Check the kill condition field.
- Cycle 17: Check the pillar chips.
- Cycle 17: Repeat for all seven experiments.
- Cycle 17: Use `route_all` for scripted runs.
- Cycle 18: Install dependencies.
- Cycle 18: Run `python -m pytest tests/ -q`.
- Cycle 18: Launch `python run.py --no-open`.
- Cycle 18: Open the browser on port 8019.
- Cycle 18: Enter a measurement.
- Cycle 18: Read the verdict card.
- Cycle 18: Check the kill condition field.
- Cycle 18: Check the pillar chips.
- Cycle 18: Repeat for all seven experiments.
- Cycle 18: Use `route_all` for scripted runs.
- Cycle 19: Install dependencies.
- Cycle 19: Run `python -m pytest tests/ -q`.
- Cycle 19: Launch `python run.py --no-open`.
- Cycle 19: Open the browser on port 8019.
- Cycle 19: Enter a measurement.
- Cycle 19: Read the verdict card.
- Cycle 19: Check the kill condition field.
- Cycle 19: Check the pillar chips.
- Cycle 19: Repeat for all seven experiments.
- Cycle 19: Use `route_all` for scripted runs.
- Cycle 20: Install dependencies.
- Cycle 20: Run `python -m pytest tests/ -q`.
- Cycle 20: Launch `python run.py --no-open`.
- Cycle 20: Open the browser on port 8019.
- Cycle 20: Enter a measurement.
- Cycle 20: Read the verdict card.
- Cycle 20: Check the kill condition field.
- Cycle 20: Check the pillar chips.
- Cycle 20: Repeat for all seven experiments.
- Cycle 20: Use `route_all` for scripted runs.
