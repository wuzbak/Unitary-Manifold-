# AZ Materials Screening Engine — Product 30

**Folder:** `12-AZ-IP/30-az-materials-screening-engine/`
**Version:** 1.2.0
**TRL:** TRL-2 (formula consolidation + ranking tool; not validated against measured data yet)
**Status:** Active — descriptive formula screening with provenance-bearing file ingestion and a web calculator

## What this is

Pulls the critical-angle, Froehlich-polaron, and metamaterial formulas out of
`src/materials/polariton_vortex.py`, `froehlich_polaron.py`, and
`metamaterials.py` into one shared, material-parameter-agnostic function
signature: `MaterialCandidate(alpha, omega_lo_mev, m_band_me, epsilon_r,
mu_r)` in, polaron binding energy, effective mass ratio, polaron radius,
metamaterial flags, and the framework's fixed critical half-angle out.

`rank_candidates()` ranks a list of candidates by absolute divergence of their
supplied Froehlich coupling `alpha` from the framework's canonical value
(`froehlich_alpha_um(5, 5, 7)`), descending. This is a descriptive sorting
criterion, **not** a performance score, uncertainty-aware significance test,
proof, or experimentally validated prediction. It does not establish which
candidate is feasible or scientifically the best falsification target.

## Epistemic status

This is Phase 0/1 only: formula consolidation and ranking logic. Phase 1's
validated-database step (checking the consolidated formula against 3-4
materials with already-published polaron/polariton measurements) and
Phase 2's inversion against a real candidate-material database (e.g. the
Materials Project) are **not** part of this product yet. You can now ingest
your own actual property records from CSV/JSON; accepting a record does not
verify its source, accuracy, experimental origin, or model applicability.
There is no remote database query, fitting, uncertainty propagation, or
experimental validation. The no-argument CLI and `/api/demo-rank` still expose
three explicitly illustrative placeholder candidates, not measured values.
These are never substituted for missing or invalid file records.

## Screening actual property records

Run from the repository root using the repository's Python environment
(the consolidated formulas depend on the existing `src/materials/` modules):

```bash
python 12-AZ-IP/30-az-materials-screening-engine/run.py screen /path/to/candidates.csv
python 12-AZ-IP/30-az-materials-screening-engine/run.py screen /path/to/candidates.json
```

The filename extension selects CSV or JSON; both must be UTF-8 (an initial BOM
is accepted). JSON must be a nonempty array of flat objects. CSV must have
one header row with these exact case-sensitive columns, in any order:

```csv
name,alpha,omega_lo_mev,m_band_me,epsilon_r,source,source_record_id,conditions
```

| Field | Contract |
|---|---|
| `name` | Nonblank material/sample description; repeated names are permitted for distinct source records. |
| `alpha` | Finite real, strictly positive, dimensionless Froehlich coupling. |
| `omega_lo_mev` | Finite real, strictly positive LO phonon **energy in meV**, not frequency in Hz or energy in eV. |
| `m_band_me` | Finite real, strictly positive band mass in units of electron mass. |
| `epsilon_r` | Finite real scalar relative permittivity; zero and negative values permitted. |
| `mu_r` | Optional finite real scalar relative permeability. If omitted, **1.0 is assumed and explicitly recorded**. If supplied, it cannot be blank/null. |
| `source` | Required nonblank source locator, e.g. DOI, dataset URL/version, or laboratory record path. Retained verbatim; not fetched or independently verified. |
| `source_record_id` | Required nonblank identifier for this property set in that source. The `(source, source_record_id)` pair must be unique within the batch (ignoring surrounding whitespace). |
| `conditions` | Required nonblank source context: phase/composition, temperature, frequency, orientation, measurement/computation method as applicable. Explicitly document unknown conditions; software cannot determine scientific adequacy. |

Files are limited to 5 MiB and 10,000 candidate records. Exceeding either limit
fails the whole batch before a report is produced.

JSON properties must be JSON numbers, not quoted numbers, booleans, or null.
CSV properties must be numeric text. No unit conversions or property
inference are performed. The source and conditions should identify a coherent
property set; do not silently mix incompatible measurement conditions.
If properties come from multiple sources, identify all of them and their
property mappings in `source`/`conditions`.

Unknown fields, missing fields, duplicate JSON keys/CSV headers, duplicate
source identities, ragged or blank CSV records, empty batches, nonfinite
values, nonpositive alpha/energy/mass, and numerically nonrepresentable formula
results are errors. The **whole batch fails**, with no skipped rows, partial
report, replacement values, or demo fallback. CLI failures return exit status
**2**, a diagnostic on stderr, and no stdout report. File access and malformed
encoding/JSON/CSV errors also fail. The CLI writes nothing to the input file.

On success, stdout contains one strict JSON document (exit status **0**):

- `schema_version`, descriptive `screening_notice`, `provenance_status`,
  ranking definition, and `formula_notes`;
- `input`: basename, format, SHA-256 of the exact source bytes, and record count;
- `candidates`: ranked formula outputs, original one-based `input_record`,
  normalized input `properties`, verbatim `provenance`, explicit `assumptions`,
  and per-candidate `warnings`.

Ties preserve input order. Retain the source file alongside its report;
the hash is an audit aid, not authentication or proof of measurement.
For automated consumers, invoke `screen`, not the legacy no-argument demo.
No measured dataset is bundled or fabricated.

### Formula limits

- Binding energy and effective mass use weak-coupling approximations valid
  for `alpha < 6`. Larger positive values remain supported for compatibility,
  but each receives an explicit out-of-range warning, not a validity claim.
- Radius uses the framework's **canonical** coupling, not the candidate's
  supplied alpha. The critical angle is also fixed across all candidates.
- Real scalar dielectric/magnetic formulas do not model dispersion, losses,
  anisotropy, stability, or experimental realizability.
- Legacy output keys such as `predicted_critical_angle_deg` are retained for
  compatibility; their names do not establish validated predictive status.

The same file workflow is available in Python:

```python
from az_materials_screening_engine import screen_file

report = screen_file("/path/to/candidates.json")
# ValueError for invalid content; OSError for unreadable files.
```

## Legacy formula/demo usage

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

`/api/screen` also accepts optional `mu_r` (default 1.0). Invalid numerical
domains, blank names, unknown/repeated parameters, and nonrepresentable formula
results return HTTP 400; unknown API routes return 404. Formula outputs carry
the descriptive-screening notice. The demo endpoint explicitly labels its
parameters as placeholders. The dashboard/API remain manual calculators:
they do not ingest or verify provenance. Use the CLI or `screen_file` for
auditable CSV/JSON batches; no file-upload HTTP endpoint is provided.

## Tests

```bash
python -m pytest 12-AZ-IP/30-az-materials-screening-engine/tests -q -p no:cacheprovider
```

Tests include strict CSV/JSON contracts, provenance/hash retention, numerical
failures, CLI success/failure subprocesses, legacy behavior, and live HTTP
responses. Fixtures are explicitly synthetic software-test inputs, not
experimental material records. Test scratch files stay inside Product 30
and are removed after each test.

## Sources

- `src/materials/polariton_vortex.py`, `froehlich_polaron.py`, `metamaterials.py`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #3

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
