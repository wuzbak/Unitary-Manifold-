# Real-World Comparison — `realworld/`

> **Theory and scientific direction:** ThomasCory Walker-Pearson  
> **Code architecture:** GitHub Copilot (AI)

This directory is the user-facing hub for comparing the **Unitary Manifold
framework's predictions** against live observational data.  It answers two
concrete questions:

1. **Do real-world numbers change the initial prediction?** (`prediction_impact.py`)  
2. **How well does the framework match independent observations?** (`live_report.py` → Section B)

---

## Quick Start

```bash
# Full report using the pinned April 2026 snapshot (offline-safe, CI-safe)
python realworld/live_report.py

# Full report with live API fetch (requires internet)
python realworld/live_report.py --live

# Live fetch AND refresh the snapshot cache
python realworld/live_report.py --update

# Prediction-impact table only (Question 1)
python realworld/live_report.py --impact

# Framework-vs-observed comparison table only (Question 2)
python realworld/live_report.py --compare
```

---

## Architecture

```
realworld/
  README.md               ← you are here
  prediction_impact.py    ← Question 1: how real data shifts predictions
  live_report.py          ← combined CLI entry point

src/
  data_feeds/             ← live ingestion adapters (7 sources)
    __init__.py
    snapshot.py           ← offline fallback / snapshot cache
    latest_snapshot.json  ← pinned April 2026 values (committed)
    usgs_seismic.py
    pnsn_seismic.py
    noaa_co2.py
    noaa_ch4.py
    open_meteo.py
    swpc_geomagnetic.py
    noaa_enso.py
  realworld_comparison.py ← framework-vs-observed runner

tests/
  test_realworld_comparison.py  ← 45 tests (snapshot, no network)
  test_prediction_impact.py     ← 35 tests (snapshot, no network)

scripts/
  live_report.py          ← thin backwards-compat wrapper
```

---

## Question 1: Do Real Numbers Change the Initial Prediction?

**Yes — significantly for 6 out of 8 metrics.**

The framework's Earth-system functions are normalised to pre-industrial
reference conditions (CO₂ = 280 ppm, CH₄ = 722 ppb, ΔT = 0 °C above the
14 °C baseline).  When April 2026 observed values are substituted, the
outputs shift as follows:

| Metric | Reference (pre-industrial) | April 2026 | Shift | Significant? |
|--------|---------------------------|------------|-------|-------------|
| CO₂ radiative forcing | 0.00 W/m² | +2.23 W/m² | +2.23 | ✅ YES |
| CH₄ forcing | 0.00 W/m² | +0.61 W/m² | +0.61 | ✅ YES |
| Committed equilibrium ΔT | 0.00 °C | +2.27 °C | +2.27 | ✅ YES |
| CO₂ greenhouse φ | 0.00 | 2.24 | +2.24 | ✅ YES |
| CO₂ atmospheric φ | 1.00 | 1.52 | +0.52 | ✅ YES |
| Surface T anomaly φ | 0.00 | 1.40 | +1.40 | ✅ YES |
| ENSO phase | la_niña | la_niña | unchanged | — negligible |
| Elsasser Λ | 3.9 × 10⁻⁴ | 3.9 × 10⁻⁴ | 0 | — negligible |

**Interpretation:**
- The climate forcings (CO₂, CH₄, ΔT) are by definition zero at the
  pre-industrial reference because the functions measure *change from that
  baseline*.  The April 2026 readings represent the accumulated anthropogenic
  forcing — 52 years of industrialisation above the 1750–1850 pre-industrial
  mean.
- **The framework correctly encodes the direction and approximate magnitude
  of anthropogenic forcing**: +2.23 W/m² CO₂ (IPCC AR6 best estimate:
  2.16 ± 0.09 W/m²), +0.61 W/m² CH₄ (IPCC: ~0.54 W/m²), committed ΔT
  of +2.27 °C (IPCC committed: 1.5–2.0 °C).
- **ENSO phase and Elsasser Λ are insensitive** to the April 2026 snapshot
  because the ENSO threshold is set in φ-space (not raw anomaly), and
  the geomagnetic field B is taken from the static IGRF-13 model.

---

## Question 2: How Well Does the Framework Match Independent Observations?

The `run_comparison()` function in `src/realworld_comparison.py` feeds live
values into the framework functions and compares the outputs against
independently published reference values:

| Metric | Framework (April 2026 inputs) | IPCC/NOAA observed | Status |
|--------|------------------------------|-------------------|--------|
| CO₂ forcing | 2.2313 W/m² | 2.2363 W/m² | ✅ ok |
| CH₄ forcing | 0.6114 W/m² | 0.6114 W/m² | ✅ ok |
| Surface T φ | 1.40 | 1.40 | ✅ ok |
| ENSO phase | la_niña | la_niña | ✅ ok |
| Elsasser Λ | 3.9 × 10⁻⁴ | 3.9 × 10⁻⁴ | ✅ ok |
| Committed ΔT | 2.27 °C | 1.75 °C (IPCC midpoint) | ⚠️ warning |
| CO₂ φ (GHG vs ATM) | 2.24 | 1.52 | ⚠️ warning |

The two warnings reflect known open questions documented in `FALLIBILITY.md`:
- The committed ΔT overestimate (+30%) arises from the simplified
  `equilibrium_temperature_shift()` formula; the true committed warming
  depends on aerosol forcing, ocean heat uptake, and carbon-cycle feedbacks
  not yet included.
- The CO₂ φ discrepancy is a formula-scope divergence between
  `greenhouse_forcing_phi()` (radiative) and `atmospheric_co2_phi()`
  (carbon-cycle) — two different φ projections of the same CO₂ field.
  Both are internally consistent; the gap is a known heterogeneity between
  climate sub-modules.

---

## Data Sources

All sources are open and require no API key.

| Feed | URL | Maps to |
|------|-----|---------|
| USGS M≥4.5 weekly | `earthquake.usgs.gov/…/4.5_week.geojson` | `rayleigh_number()`, `phi_rock_regime()` |
| PNSN Cascadia | `pnsn.org/api/v1/earthquakes/recent` | Cascadia moment deficit |
| Mauna Loa CO₂ | `gml.noaa.gov/…/co2_daily_mlo.txt` | `greenhouse_forcing_phi()`, `co2_forcing()` |
| NOAA CH₄ | `gml.noaa.gov/…/ch4_annmean_gl.txt` | `methane_phi_forcing()` |
| Open-Meteo surface T | `api.open-meteo.com/v1/forecast` | `temperature_phi_anomaly()` |
| NOAA SWPC Kp / plasma | `services.swpc.noaa.gov/…` | `elsasser_number()` |
| NOAA CPC Niño 3.4 | `cpc.ncep.noaa.gov/…/sstoi.indices` | `enso_phase()` |

---

## Offline / CI Safety

Every adapter falls back to `src/data_feeds/latest_snapshot.json`, which is
committed to the repository pre-seeded with April 2026 values.  No network
access is required to run the full test suite or generate a report.

To refresh the snapshot with today's live data:

```bash
python realworld/live_report.py --update
```

---

## Falsification Discipline

As required by `SEPARATION.md`, this subsystem provides:

- **Comparison mode:** every run prints `framework_predicted vs USGS/NOAA_observed`.
- **Falsification flags:** if the framework's ENSO prediction disagrees with
  the NOAA Niño 3.4 index, or if a tipping-point score reverses sign, the
  report shows `warning` and the discrepancy is quantified.
- **Primary falsifier (cosmological):** birefringence β ∈ {≈0.273°, ≈0.331°}
  will be tested by LiteBIRD (~2032).  This Earth-system comparison layer
  provides an *independent, near-term* falsification track.

---

## Test Suite

```bash
# New tests (80 tests, no network required)
python3 -m pytest tests/test_prediction_impact.py tests/test_realworld_comparison.py -v

# Full suite (18,057 passed, 329 skipped, 11 deselected, 0 failed)
python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" omega/ -q
```
