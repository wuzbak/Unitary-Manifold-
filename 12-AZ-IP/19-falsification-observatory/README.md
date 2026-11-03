# Falsification Observatory

**Product:** 19 of the AxiomZero suite  
**Folder:** `12-AZ-IP/19-falsification-observatory/`  
**Default port:** `8019`  
**Status:** Standalone browser product with a deterministic threshold router and an optional public arXiv literature feed. Experimental measurements are entered by users; the application does not ingest measured results.
**License:** Defensive Public Commons License v1.0

---

## 1. What This Product Is
The Falsification Observatory is a browser-based scientific product that applies seven documented prediction thresholds to measurements entered by a user. Its optional arXiv integration discovers recent literature for those experimental fronts; it does not fetch experimental measurements, extract values from papers, or change verdicts automatically. The application productizes Pillar 787's routing logic for local AxiomZero use.

Instead of burying predictions in prose, the Observatory exposes them as callable routing functions and as a visible experiment dashboard. The user can supply a measured value, read the verdict, inspect the kill condition, and trace the relevant pillar chain.

The design goal is not rhetorical persuasion. The design goal is bright-line accountability. A product that claims a scientific framework should also show the exact conditions under which that framework survives, enters tension, or fails.

Product 19 consists of a browser interface in `ui/`, a deterministic local threshold router in `falsification_observatory/engine/`, and an optional literature-feed service. Its output is a rule-based classification of submitted values, not independent experimental verification.

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
- `falsification_observatory/engine/evidence_feed.py` — arXiv public evidence-feed ingestion, validation, provenance, and freshness tracking (see §4A).
- `falsification_observatory/app/server.py` — Simple HTTP server bound to `ui/`, plus the `/api/litebird`, `/api/desi`, and `/api/evidence` JSON endpoints.
- `ui/index.html` — Standalone copied observatory HTML.
- `ui/falsification-observatory.js` — Standalone copied observatory JavaScript.
- `css/main.css` — Copied shared site stylesheet for standalone serving.
- `css/az-apps.css` — Copied app stylesheet for standalone serving.
- `tests/test_falsification_observatory.py` — Comprehensive product-level tests.
- `tests/test_evidence_feed.py` — Deterministic evidence-feed tests (injected fetcher and clock; network sockets are blocked).
- `tests/fixtures/arxiv_*.xml` — Synthetic arXiv Atom fixtures (clearly marked FIXTURE RECORD; not real papers).

## 4. Experiment Registry
For every experiment below, the Observatory treats the prediction as pre-registered, the verdict as mechanical, and the `note` field as explanatory rather than discretionary.

### EXP-1 — LiteBIRD Cosmic Birefringence
- **Prediction:** β ∈ {0.273°, 0.331°}
- **Kill condition:** β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.
- **Relevant pillars:** 11, 13, 765, 771, 787
- **Python API:** `route_litebird(beta=None, beta_sigma=None)`
- **Product reading:** LiteBIRD Cosmic Birefringence is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

### EXP-2 — DESI Dark Energy
- **Prediction:** w_a = 0
- **Kill condition:** A ≥3σ departure from w_a = 0.
- **Relevant pillars:** 5, 29, 38, 727, 739, 771, 787
- **Python API:** `route_desi(w_a=None, w_a_sigma=None)`
- **Product reading:** DESI Dark Energy is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

### EXP-3 — JUNO Neutrino Mass
- **Prediction:** Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²
- **Kill condition:** Outside the window at ≥2σ.
- **Relevant pillars:** 772, 773, 786, 787
- **Python API:** `route_juno(dm21=None, dm21_sigma=None)`
- **Product reading:** JUNO Neutrino Mass is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

### EXP-4 — ACT CMB Spectral Index
- **Prediction:** n_s = 0.9635
- **Kill condition:** A ≥3σ inconsistency with the prediction.
- **Relevant pillars:** 11, 67, 787
- **Python API:** `route_act(n_s=None, n_s_sigma=None)`
- **Product reading:** ACT CMB Spectral Index is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

### EXP-5 — HL-LHC KK Gluon
- **Prediction:** Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.
- **Kill condition:** No hard kill in Product 19; low-scale discovery is routed as TENSION.
- **Relevant pillars:** 709, 787
- **Python API:** `route_hllhc(mass_tev=None, observed=False)`
- **Product reading:** HL-LHC KK Gluon is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

### EXP-6 — nEDM Electric Dipole Moment
- **Prediction:** Residual EDM near 1e-30 e·cm.
- **Kill condition:** Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.
- **Relevant pillars:** 731, 786, 787
- **Python API:** `route_nedm(d_e=None, d_e_sigma=None)`
- **Product reading:** nEDM Electric Dipole Moment is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

### EXP-7 — XENON-nT Dark Matter
- **Prediction:** Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.
- **Kill condition:** σ < 5e-47 cm².
- **Relevant pillars:** 717, 787
- **Python API:** `route_xenon(sigma_cm2=None)`
- **Product reading:** XENON-nT Dark Matter is routed both in the standalone Python engine and in the copied browser interface lineage from Pillar 787.

## 4A. Public Evidence Feed (arXiv)
The Observatory can ingest a real public evidence feed: the **arXiv API** (`https://export.arxiv.org/api/query`, Atom 1.0). Each of the seven experiment fronts has one fixed, pre-registered search query; the server never fetches a user-supplied URL.

| Experiment | Fixed arXiv query |
|---|---|
| EXP-1 | `abs:"cosmic birefringence"` |
| EXP-2 | `abs:DESI AND abs:"dark energy"` |
| EXP-3 | `abs:JUNO AND abs:neutrino` |
| EXP-4 | `abs:"Atacama Cosmology Telescope" AND abs:"spectral index"` |
| EXP-5 | `abs:"Kaluza-Klein gluon"` |
| EXP-6 | `abs:"neutron electric dipole moment"` |
| EXP-7 | `abs:XENONnT` |

Results are sorted by submission date (newest first, 10 per fetch).

### Workflow
1. Run `python run.py --no-open` and open `http://127.0.0.1:8019/`.
2. In the **Public Evidence Feed** panel, pick an experiment and press **⟳ Fetch from arXiv**.
3. The local server fetches the fixed query, validates the response, and shows the entries with a status badge and a provenance block.
4. Later refreshes mark preprints that were not seen before as **NEW**. The first successful fetch is the baseline, so nothing is marked new on that fetch.
5. Read any paper that looks relevant. If it reports a measurement, enter the value in the simulation panel by hand. **Feed entries never change a verdict automatically.**

### Safeguards
- **Bounded network use:** 10 s timeout and a 2 MiB response cap. The fetcher accepts only the `export.arxiv.org` host and rejects redirects to other hosts. Each experiment has a 60 s cooldown, and the server waits at least 3 s between outbound requests, following arXiv's API guidance.
- **Validation:** the server rejects DOCTYPE/ENTITY declarations, malformed XML, non-Atom roots, non-XML content types, and arXiv error feeds. It also checks each entry's arXiv ID, ISO timestamps, DOI syntax, and duplicate IDs. It rejects individual bad entries and keeps the reasons. If every entry fails validation, the whole fetch is an error.
- **Provenance per snapshot:** endpoint, exact request URL, query, `fetched_at` (UTC), HTTP status, content type, byte length, SHA-256 of the raw response, `totalResults`, returned and rejected counts with reasons, and parser version.
- **Explicit states:**
  - `never_fetched`: no fetch has been attempted yet.
  - `fresh`: the last fetch succeeded and is still within the freshness window, 24 h by default (`--evidence-max-age-hours`).
  - `stale`: the last fetch succeeded, but it is older than the freshness window.
  - `unavailable`: the last attempt hit a network failure, timeout, HTTP 429, or HTTP 5xx.
  - `error`: the last attempt received a response that failed validation, or the fetcher failed unexpectedly.

  If a later fetch fails, the last good snapshot remains visible and is flagged `served_from_cache`.
- **Persistence (optional):** `python run.py --evidence-state evidence.json` saves tracking state through an atomic replace, so NEW detection survives a restart. Without this flag, the feed is held in memory only and no files are written. If the state file is corrupt, the server reports `persistence_error` and starts fresh.

### HTTP API
- `GET /api/evidence` returns status for all seven feeds and never touches the network.
- `GET /api/evidence?exp=EXP-1` returns one feed with its entries and provenance.
- `POST /api/evidence/refresh?exp=EXP-1` fetches from arXiv. It returns `200` when a fetch was attempted, even if the fetch failed. In that case, read `refresh.outcome` and `feed.status`. It returns `429` while cooldown or rate limits apply, `400` for an unknown experiment, and `405` for the wrong HTTP method.

### Limitations
- This is a **literature feed, not a measurement feed**. Measured values such as β or w_a are not extracted from papers.
- Keyword queries are approximate. They can miss relevant papers or include irrelevant ones.
- Fetches happen only when a user presses refresh. There is no background scheduler.
- Fixtures are synthetic. The automated tests never contact arXiv. In the environment where this feature was built, outbound DNS to arXiv was blocked, so the live path was smoke-tested only for the `unavailable` state. The parser targets the documented arXiv Atom schema.
- Acknowledgement: *Thank you to arXiv for use of its open access interoperability.*

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
Every `route_*` function, including `route_all`, is deterministic for the same input arguments and never mutates shared state.

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
- The verdict dashboard is static and has no database. The **Public Evidence Feed** panel needs the bundled Python server (`run.py`) because the server performs the arXiv fetch. When the panel is opened without the server, it shows an `unavailable` state instead of failing silently.

## 10. Epistemic Status
This product is an instrumentation layer, not an independent scientific proof. It encodes the routing contract.

The pillar references and numerical values are treated here as repository-defined constants. The product does not independently derive them.

Because the product is built to expose falsifiers, it should be read as a scientific accountability artifact rather than a marketing page.

The copied UI includes lineage from the existing public-site artifact. The standalone Python engine is the local automation layer for Product 19.

## 11. Programmatic Examples
Each example is suitable for CLI scripting, notebook usage, or batch routing through `route_all`.

### Example 1: LiteBIRD Cosmic Birefringence
```python
from falsification_observatory import route_litebird
result = route_litebird(0.273, 0.01)
print(result)
```

### Example 2: DESI Dark Energy
```python
from falsification_observatory import route_desi
result = route_desi(0.0, 0.1)
print(result)
```

### Example 3: JUNO Neutrino Mass
```python
from falsification_observatory import route_juno
result = route_juno(7.53e-5, 0.1e-5)
print(result)
```

### Example 4: ACT CMB Spectral Index
```python
from falsification_observatory import route_act
result = route_act(0.9635, 0.001)
print(result)
```

### Example 5: HL-LHC KK Gluon
```python
from falsification_observatory import route_hllhc
result = route_hllhc(2.5, True)
print(result)
```

### Example 6: nEDM Electric Dipole Moment
```python
from falsification_observatory import route_nedm
result = route_nedm(1e-30, 1e-31)
print(result)
```

### Example 7: XENON-nT Dark Matter
```python
from falsification_observatory import route_xenon
result = route_xenon(1e-46)
print(result)
```

## 12. FAQ
### Q: Why does the product use AWAITING_DATA?
A: Because not every experiment has a submitted or current measurement in a local session.

### Q: Why are pillar references included?
A: So each verdict can be traced back to the governing pillar chain.

### Q: Is the UI the source of truth?
A: No. The local Python package is the source of truth for the standalone product API.

### Q: Why is LiteBIRD primary?
A: Because the repository-level falsification note explicitly elevates the birefringence window as the main bright-line test.

### Q: Why is there a static server instead of a framework?
A: The product needs only local serving of HTML, JS, and CSS.

### Q: Can `route_all` be used in automation?
A: Yes. It is designed for scripts, dashboards, and batch checks.

### Q: Does the product create files at runtime?
A: Not by default. It serves static assets and keeps evidence-feed state in memory. It writes a file only when you pass `--evidence-state PATH`, and that file is the evidence tracking state.

### Q: Are verdicts probabilistic?
A: No. The routes are deterministic for supplied inputs.

### Q: Why copy CSS files?
A: To make the product actually standalone instead of leaving broken stylesheet links.

### Q: Why include tests for file presence?
A: Because the product contract includes both code and deployable static assets.

## 13. Repository Relationship
This folder is intentionally standalone, but it is also traceable to four upstream sources inside the repository: the public-site JavaScript, the public-site HTML, the Pillar 787 Python oracle, and the repository-level falsification tests.

The Product 19 package is therefore both derivative and operational: derivative in asset lineage, operational in local packaging and testing.

Nothing in this folder alters the source repository public-site artifact. It instead packages a standalone local product patterned after Product 16.

## 14. Authorship
Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.  
Code architecture, packaging, tests, and product synthesis: **GitHub Copilot** (AI).

## 15. Appendix A — One-line audit map
- EXP-1: prediction=β ∈ {0.273°, 0.331°}; kill=β outside [0.22°, 0.38°], or in the (0.29°, 0.31°) gap, at ≥3σ.; pillars=11, 13, 765, 771, 787.
- EXP-2: prediction=w_a = 0; kill=A ≥3σ departure from w_a = 0.; pillars=5, 29, 38, 727, 739, 771, 787.
- EXP-3: prediction=Δm²₂₁ ∈ [7.0e-5, 8.1e-5] eV²; kill=Outside the window at ≥2σ.; pillars=772, 773, 786, 787.
- EXP-4: prediction=n_s = 0.9635; kill=A ≥3σ inconsistency with the prediction.; pillars=11, 67, 787.
- EXP-5: prediction=Heavy-scale survivability above 5 TeV; discovery near 2.5 TeV creates tension.; kill=No hard kill in Product 19; low-scale discovery is routed as TENSION.; pillars=709, 787.
- EXP-6: prediction=Residual EDM near 1e-30 e·cm.; kill=Measured EDM ≥1e-27 e·cm or strong sigma-level inconsistency.; pillars=731, 786, 787.
- EXP-7: prediction=Cross section near 1e-46 cm²; sub-5e-47 cm² results are fatal.; kill=σ < 5e-47 cm².; pillars=717, 787.

## 16. Appendix B — Operational checklist
- Install dependencies.
- Run `python -m pytest tests/ -q`.
- Launch `python run.py --no-open`.
- Open the browser on port 8019.
- Enter a measurement.
- Read the verdict card.
- Check the kill condition field.
- Check the pillar chips.
- Repeat for all seven experiments.
- Use `route_all` for scripted runs.
