# AZ Calorimetry Console — Product 28

**Folder:** `12-AZ-IP/28-az-calorimetry-console/`
**Version:** 1.1.0
**TRL:** TRL-2 (software instrumentation only; no lab run performed)
**Status:** Active — Phase 0 of article-354's cold-fusion roadmap, now a runnable web product

## What this is

Instrumentation software for the cold-fusion falsification protocol already
defined in `src/cold_fusion/` and `src/physics/lattice_dynamics.py`. It does
**not** claim cold fusion occurs, and it does not run or simulate a lab
experiment. It packages two already-tested, already-passing physics modules
into artifacts a real electrochemistry lab could use:

1. **Run-sheet generator** (`generate_run_sheet`) — reads the canonical
   D/Pd loading resonance `x = 7/8 = 0.875` from `lattice_dynamics.py` and
   the F1 calorimetry gate from `falsification_protocol.falsification_criteria()`,
   and emits a concrete temperature-ramp schedule paired with a monotonic
   loading-ratio curve.
2. **Live COP tracker** (`COPTracker`) — ingests `(power_in, power_out)`
   samples and reports a running verdict using the project's own `cop()`
   and `is_excess_heat()` functions from `src/cold_fusion/excess_heat.py`,
   against the pre-registered COP > 1.01 threshold. The verdict is always
   one of `AWAITING_DATA`, `NO_EXCESS_HEAT`, or `EXCESS_HEAT_OBSERVED` — it
   never claims more than the ingested data supports.
3. **Instrument-export importer** (`import_measurements`, `import-run`) —
   validates a complete measured-power CSV and required acquisition metadata,
   retaining raw-source SHA-256 digests and every accepted sample in a JSON
   artifact. Its threshold screen is explicitly **not** a physical verdict.

## Epistemic status

This is Phase 0 only, per article-354 direction #1 ("Cold fusion: from
calculation to calorimeter"). Phase 1 (lab-reproducible procedure document),
Phase 2 (an actual external lab run), and Phase 3 (honest reporting into
`FALLIBILITY.md`) are **not** part of this product and depend on an external
lab's willingness to run the protocol. The underlying field-theoretic vertex
bridging the radion's ~10⁻³⁵ m Compton wavelength to the ~10⁻¹⁰ m palladium
lattice scale has not been computed — see `src/cold_fusion/README.md`.

## Usage

```bash
python 12-AZ-IP/28-az-calorimetry-console/run.py run-sheet --loading-target 0.875
python 12-AZ-IP/28-az-calorimetry-console/run.py track --power-in-w 100 --power-out-w 102
```

## Importing real instrument measurements

The single-reading tracker/API is not a file-ingestion or provenance workflow.
Use this local CLI to import a lab's **already calibrated power measurements**:

```bash
python 12-AZ-IP/28-az-calorimetry-console/run.py import-run \
  --csv path/to/instrument.csv --metadata path/to/acquisition.json \
  --output path/to/validated-run.json
```

The UTF-8 CSV (optional BOM, LF or CRLF) requires exactly this header/order:
`timestamp_s,power_in_w,power_out_w`. Rows contain elapsed seconds from the
acquisition start and calibrated input/output watts, not thermocouple voltages
or raw temperatures. At least two samples are required. Times must be finite,
nonnegative and strictly increasing; input power finite and positive; output
power finite and nonnegative. Duplicate/out-of-order timestamps, blank rows,
missing/extra columns, invalid numbers and numeric overflow reject the entire
run; no sorting, interpolation of missing records, or partial acceptance occurs.

Provide this JSON metadata structure with your actual identifiers (values below
are placeholders for the format, **not** a lab dataset):

```json
{
  "schema_version": 1,
  "run_id": "YOUR-RUN-ID",
  "instrument_id": "YOUR-INSTRUMENT-ID",
  "calibration_id": "YOUR-CALIBRATION-RECORD-ID",
  "acquired_at": "2026-08-01T12:00:00+00:00",
  "source_reference": "YOUR-LAB-NOTEBOOK-OR-SOURCE-REFERENCE",
  "units": {"timestamp_s": "s", "power_in_w": "W", "power_out_w": "W"}
}
```

All keys are required; unknown/duplicate keys, empty identifier strings,
nonstandard JSON numbers, wrong units, and acquisition datetimes without a
timezone are rejected. Convert other units explicitly before import and retain
the original export/conversion record referenced in `source_reference`.
Calibration identifiers and acquisition metadata are **operator declarations**,
not independently checked certificates.

The `az-calorimetry-measurements/v1` artifact includes metadata, source filenames,
SHA-256 hashes of the exact CSV/metadata bytes, accepted samples with source line
numbers, and a summary. Input/output energies use trapezoidal integration over
the recorded time interval only (no extrapolation). `energy_cop` is the ratio
of integrated energies, **not** the existing tracker's arithmetic sample-mean
COP; this matters for irregular timing and varying power. Gaps between valid
samples assume linear power evolution and require operator review.

The strict COP > 1.01 screen yields `ABOVE_THRESHOLD` or `NOT_ABOVE_THRESHOLD`.
Neither result establishes excess heat, validates the theory, or replaces
uncertainty analysis, baseline/control experiments or independent calibration.
No uncertainty propagation, baseline subtraction or sensor-to-power conversion
is performed. Software acceptance only means the declared format passed.

Validation finishes before output creation. The output parent directory must
already exist on a filesystem supporting hard links. A sibling staging file is
flushed before atomic, no-overwrite publication and removed afterward, including
on write/publication errors. An existing output is never overwritten (including
input files); failures return exit code 2. Preserve the source files alongside the
artifact for hash verification. No external lab data or lab run is supplied
or claimed here. The existing web API and single-reading tracker are unchanged.

## Running as a web product

The console also runs as a live HTTP product — a stdlib-only JSON API plus a
static dashboard, with no behavior beyond the library above (`app/server.py`
dispatches to the same `dispatch_api_request` function covered by
`tests/test_api.py`):

```bash
python 12-AZ-IP/28-az-calorimetry-console/run.py serve --port 8128
# then open http://127.0.0.1:8128/
```

Endpoints: `GET /api/status`, `GET /api/run-sheet?loading_target=&hold_minutes=`,
`GET /api/track?power_in_w=&power_out_w=`. This is a software product-surface
step, distinct from the article's own Phase 2 ("an actual external lab run"),
which still has not happened and is not claimed here.

## Tests

```bash
python -m pytest 12-AZ-IP/28-az-calorimetry-console/tests -q
```

## Sources

- `src/cold_fusion/excess_heat.py`, `falsification_protocol.py`
- `src/physics/lattice_dynamics.py`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-the-untouched-manifold-what-this-monorepo-could-still-become.md` — direction #1

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
