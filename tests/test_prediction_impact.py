# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_prediction_impact.py
================================
Tests for ``realworld/prediction_impact.py``.

Verifies that substituting April 2026 observed values into the Unitary
Manifold Earth-system functions produces the expected prediction shifts
relative to the pre-industrial reference baseline.  All tests use the
pinned snapshot so no network access is required.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""

from __future__ import annotations

import pytest

from realworld.prediction_impact import (
    impact_report,
    impact_summary,
    _CO2_REF_PPM,
    _CH4_REF_PPB,
    _T_BASE_C,
    _DELTA_T_REF,
    _PHI_PACIFIC_REF,
)


@pytest.fixture(scope="module")
def entries():
    return impact_report(live=False)


@pytest.fixture(scope="module")
def entry_map(entries):
    return {e["metric"]: e for e in entries}


# ---------------------------------------------------------------------------
# Structure tests
# ---------------------------------------------------------------------------

class TestImpactReportStructure:
    def test_returns_list(self, entries):
        assert isinstance(entries, list)

    def test_eight_entries(self, entries):
        assert len(entries) == 8

    def test_all_have_required_keys(self, entries):
        required = {"metric", "unit", "reference_prediction",
                    "april2026_prediction", "shift", "significance"}
        for e in entries:
            assert required.issubset(e.keys()), f"Missing keys in {e['metric']}"

    def test_significance_values_valid(self, entries):
        for e in entries:
            assert e["significance"] in {"significant", "negligible"}, \
                f"Bad significance in {e['metric']}"

    def test_metric_names_present(self, entry_map):
        expected = {
            "co2_radiative_forcing",
            "ch4_forcing",
            "committed_equilibrium_delta_T",
            "co2_greenhouse_phi",
            "co2_atmospheric_phi",
            "surface_T_phi",
            "enso_phase",
            "elsasser_lambda",
        }
        assert expected == set(entry_map.keys())


# ---------------------------------------------------------------------------
# Reference baseline tests (pre-industrial inputs → reference outputs)
# ---------------------------------------------------------------------------

class TestReferenceBaseline:
    def test_co2_forcing_at_reference_is_zero(self, entry_map):
        assert entry_map["co2_radiative_forcing"]["reference_prediction"] == pytest.approx(0.0, abs=1e-6)

    def test_ch4_forcing_at_reference_is_zero(self, entry_map):
        assert entry_map["ch4_forcing"]["reference_prediction"] == pytest.approx(0.0, abs=1e-6)

    def test_delta_T_at_reference_is_zero(self, entry_map):
        assert entry_map["committed_equilibrium_delta_T"]["reference_prediction"] == pytest.approx(0.0, abs=1e-6)

    def test_co2_ghg_phi_at_reference_is_zero(self, entry_map):
        assert entry_map["co2_greenhouse_phi"]["reference_prediction"] == pytest.approx(0.0, abs=1e-6)

    def test_surface_T_phi_at_reference_is_zero(self, entry_map):
        assert entry_map["surface_T_phi"]["reference_prediction"] == pytest.approx(0.0, abs=1e-6)

    def test_atmospheric_co2_phi_at_reference_is_unity(self, entry_map):
        # atmospheric_co2_phi(280) = log2(280/280) + 1 = 1.0 (or similar normalisation)
        ref = entry_map["co2_atmospheric_phi"]["reference_prediction"]
        assert ref == pytest.approx(1.0, abs=0.1)


# ---------------------------------------------------------------------------
# April 2026 value tests (snapshot: co2=425.3, ch4=1923, dT=1.4)
# ---------------------------------------------------------------------------

class TestApril2026Predictions:
    def test_co2_forcing_positive(self, entry_map):
        assert entry_map["co2_radiative_forcing"]["april2026_prediction"] > 1.5

    def test_ch4_forcing_positive(self, entry_map):
        assert entry_map["ch4_forcing"]["april2026_prediction"] > 0.3

    def test_delta_T_positive_and_plausible(self, entry_map):
        dT = entry_map["committed_equilibrium_delta_T"]["april2026_prediction"]
        assert 0.5 < dT < 6.0

    def test_co2_ghg_phi_positive(self, entry_map):
        assert entry_map["co2_greenhouse_phi"]["april2026_prediction"] > 1.0

    def test_surface_T_phi_equals_delta_T(self, entry_map):
        # temperature_phi_anomaly(T, T_base) = T - T_base = delta_T
        phi_T = entry_map["surface_T_phi"]["april2026_prediction"]
        assert phi_T == pytest.approx(1.4, abs=0.05)

    def test_enso_phase_is_la_nina(self, entry_map):
        # snapshot: nino34 = -0.6 → la_nina
        assert entry_map["enso_phase"]["april2026_prediction"] == "la_nina"

    def test_elsasser_lambda_positive(self, entry_map):
        assert entry_map["elsasser_lambda"]["april2026_prediction"] > 0.0


# ---------------------------------------------------------------------------
# Shift direction tests (all climate forcings should increase from reference)
# ---------------------------------------------------------------------------

class TestShiftDirection:
    def test_co2_forcing_shift_positive(self, entry_map):
        assert entry_map["co2_radiative_forcing"]["shift"] > 0.0

    def test_ch4_forcing_shift_positive(self, entry_map):
        assert entry_map["ch4_forcing"]["shift"] > 0.0

    def test_delta_T_shift_positive(self, entry_map):
        assert entry_map["committed_equilibrium_delta_T"]["shift"] > 0.0

    def test_co2_ghg_phi_shift_positive(self, entry_map):
        assert entry_map["co2_greenhouse_phi"]["shift"] > 0.0

    def test_surface_T_phi_shift_positive(self, entry_map):
        assert entry_map["surface_T_phi"]["shift"] > 0.0


# ---------------------------------------------------------------------------
# Significance classification tests
# ---------------------------------------------------------------------------

class TestSignificanceClassification:
    def test_co2_forcing_significant(self, entry_map):
        assert entry_map["co2_radiative_forcing"]["significance"] == "significant"

    def test_ch4_forcing_significant(self, entry_map):
        assert entry_map["ch4_forcing"]["significance"] == "significant"

    def test_delta_T_significant(self, entry_map):
        assert entry_map["committed_equilibrium_delta_T"]["significance"] == "significant"

    def test_co2_ghg_phi_significant(self, entry_map):
        assert entry_map["co2_greenhouse_phi"]["significance"] == "significant"

    def test_surface_T_phi_significant(self, entry_map):
        assert entry_map["surface_T_phi"]["significance"] == "significant"

    def test_enso_phase_unchanged_negligible(self, entry_map):
        # snapshot: both reference and April 2026 are la_nina
        assert entry_map["enso_phase"]["significance"] == "negligible"

    def test_at_least_five_significant(self, entries):
        sig = [e for e in entries if e["significance"] == "significant"]
        assert len(sig) >= 5, f"Expected ≥5 significant metrics, got {len(sig)}"


# ---------------------------------------------------------------------------
# impact_summary() tests
# ---------------------------------------------------------------------------

class TestImpactSummary:
    def test_returns_string(self, entries):
        summary = impact_summary(entries)
        assert isinstance(summary, str)

    def test_contains_all_metric_names(self, entries):
        summary = impact_summary(entries)
        for e in entries:
            assert e["metric"] in summary

    def test_contains_significance_count(self, entries):
        summary = impact_summary(entries)
        assert "SIGNIFICANT shifts" in summary

    def test_contains_reference_column(self, entries):
        summary = impact_summary(entries)
        assert "Reference" in summary

    def test_contains_april2026_column(self, entries):
        summary = impact_summary(entries)
        assert "Apr 2026" in summary
