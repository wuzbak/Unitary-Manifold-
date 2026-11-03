# AZ Polariton Vortex Analyzer — Product 29

**Version:** 1.1.0

**TRL:** TRL-2 (analysis software; tested only with constructed fixtures)

**Status:** Runnable local CLI/API; no laboratory deployment or real dataset bundled.

## What this is

Analyze **already tracked feature positions** exported from pump-probe measurements,
not raw images or intensities. The pipeline fits position versus time separately
at each wavefront half-angle and compares the resulting signed velocity (`v/c`)
with `src/materials/polariton_vortex.py`'s prediction (`c_s = 12/37` by default).
There was no external file format in this product: the small contract below
serializes the existing `PumpProbeFrame` position/time/angle model.

**Epistemic boundary:** accepting an export does not authenticate its experimental
origin or calibration. Source metadata is user-asserted; hashes establish input
identity, not authenticity. Residuals/crossings are descriptive, **not evidence
validating UM predictions or hardgate physics claims**. A feature/crossing-point
speed is not an information or matter transport speed.

Optics-group correspondence, calibrated uncertainty analysis, and publication-grade
experimental comparisons remain external work; this software does not perform them.

## Measurement contract (schema version 1)

UTF-8 JSON files must contain exactly:

```json
{
  "schema_version": 1,
  "dataset_id": "replace-with-acquisition-id",
  "source": "replace-with-instrument/export-reference-and-calibration-record",
  "frames": [
    {"position_um": 0.0, "timestamp_fs": 0.0, "half_angle_deg": 20.0},
    {"position_um": 1.0, "timestamp_fs": 10.0, "half_angle_deg": 20.0}
  ]
}
```

The numbers above are **illustrative, not laboratory data or a prediction-based
fixture**. Supply your own tracked positions and acquisition metadata.

CSV files use exactly these column names (column order may vary):

```csv
position_um,timestamp_fs,half_angle_deg
0.0,0.0,20.0
1.0,10.0,20.0
```

CSV requires `--dataset-id` and `--source` on the CLI; JSON carries these fields
itself and rejects overrides. There are no inferred units, optional columns,
calibration defaults, automatic image tracking, or fallback datasets.

Validation:

- Input is 1 byte–2 MiB, with 2–20,000 frame records.
- `schema_version` is integer `1`. Metadata strings are nonblank, at most
  1,024 characters. Unknown/missing fields and duplicate JSON keys are errors.
- Position is in micrometres, delay in femtoseconds, half-angle in degrees.
  JSON quantities must be numbers (not numeric strings, booleans, null,
  NaN, or infinity); CSV quantities must parse as finite numbers.
- `0 < half_angle_deg < 90`. Each **exact numeric half-angle** needs at least
  two distinct timestamps; timestamps may be negative and rows unordered.
  No rounding/nearby-angle merging or silently discarded singleton groups.
- Each angle must describe **one tracked trajectory in a consistent calibrated
  coordinate system**. Split independent runs/tracks into separate analyses.
  The software cannot establish this assumption from the three numeric columns.
- Invalid groups, duplicate timestamps, nonrepresentable fits, bad units/schema,
  missing files, or model parameters outside `0 < c_s < 1` fail explicitly.
  The schema cannot detect a numeric value expressed in the wrong units.

## CLI and Python

From the repository root:

```bash
python 12-AZ-IP/29-az-polariton-vortex-analyzer/run.py analyze measurement.json
python 12-AZ-IP/29-az-polariton-vortex-analyzer/run.py analyze measurement.csv \
  --dataset-id run-2026-001 --source "instrument-export; calibration-record-001" \
  --c-s 0.32432432432432434
```

Success prints a JSON report to stdout (redirect to a report file if desired).
Failure prints an error to stderr, returns exit code 2, and prints **no report**.
No arguments retains the prediction-only summary, not a measurement analysis.

With the product folder on `PYTHONPATH`:

```python
from az_polariton_vortex_analyzer import analyze_measurement_file
report = analyze_measurement_file("measurement.json")
```

`analyze_measurement(content_bytes, "json")` accepts the same contract in memory;
CSV additionally requires `dataset_id=` and `source=`. The existing
`PumpProbeFrame`, `extract_feature_velocity_curve`, and `compare_to_prediction`
functions remain available for programmatic use, but they alone do not provide
file provenance.

## Report and numerical assumptions

- Provenance: dataset ID, declared source, input format, exact input-byte SHA-256,
  byte/frame counts, verification disclaimer, UTC analysis timestamp.
- Extraction: ordinary least-squares straight-line fit using **every sample** at
  each angle; sorted angles, signed `v/c` using `c = 0.299792458 um/fs`.
  This replaces the old endpoint-only slope (identical for two-frame groups).
- Per-angle diagnostics: frame count, time span, position-fit RMSE in micrometres.
  Fit RMSE describes departure from constant velocity, **not calibrated uncertainty**.
  Two-frame fits cannot independently assess fit quality and produce a warning.
- Comparison: predicted velocities, signed measured-minus-predicted residuals,
  maximum/mean absolute residual and RMSE in `v/c`, predicted critical angle,
  and every sampled/interpolated `v/c = 1` crossing. No extrapolation is performed.
  Crossing angles use linear interpolation between adjacent measured angles;
  they are not fitted critical angles or uncertainty bounds. Exact sampled
  crossings are retained, including plateaus (reported as multiple crossings).
  `measured_crossing_angle_deg` retains the first crossing for compatibility;
  consult `measured_crossing_angles_deg` and `crossing_status` for ambiguity.
- Warnings flag absent/multiple crossings, negative velocities and two-frame fits.
  No match/pass/validation claim, significance test, or experimental uncertainty
  is inferred. A negative slope is never silently replaced by its magnitude.

## Local web UI and HTTP API

```bash
python 12-AZ-IP/29-az-polariton-vortex-analyzer/run.py serve --port 8129
```

Open `http://127.0.0.1:8129/` to upload a measurement **JSON** file and inspect
the report. Uploads are analyzed in memory and not saved. This is a local tool,
not an authenticated/public production service; keep the default loopback binding.

- `GET /api/status`
- `GET /api/prediction?c_s=...`
- `GET /api/demo-comparison?c_s=...` — explicitly synthetic, generated from the
  prediction itself; only a self-consistency check, **not measurement evidence**.
- `POST /api/analyze?c_s=...` — JSON contract above, `Content-Type: application/json`
  and a `Content-Length` required (no chunked transfer). Only `c_s` is accepted
  as a query parameter; omit it for the canonical `12/37` value.

```bash
curl --fail-with-body http://127.0.0.1:8129/api/analyze \
  -H 'Content-Type: application/json' --data-binary @measurement.json
```

Analysis errors return JSON errors, not synthetic substitutes: HTTP 400 for bad
schema/input/parameters, 413 for body-size violations, 415 for wrong content type,
405 for wrong method, and 404 for unknown endpoints.

## Tests

```bash
python -m pytest 12-AZ-IP/29-az-polariton-vortex-analyzer/tests -q
```

Tests use explicitly constructed fixtures, including noisy/non-prediction-based
positions; cover JSON/CSV ingestion, all-sample fits, strict failures, provenance,
CLI success/error exits, and actual local HTTP requests. They demonstrate software
behavior, not performance on real instruments or experimental physics validity.

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.

Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
