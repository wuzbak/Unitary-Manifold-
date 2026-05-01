# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_realworld_comparison.py
===================================
Tests for ``src/realworld_comparison.py`` and the ``src/data_feeds``
adapters.

All tests run against the pinned April 2026 snapshot (``live=False``),
so the suite passes in CI and offline environments without any network
access.  The snapshot itself is committed to the repository, giving
reproducible, documented test inputs.

"""

from __future__ import annotations

import pytest

from src.data_feeds import noaa_co2 as _co2
from src.data_feeds import noaa_ch4 as _ch4
from src.data_feeds import noaa_enso as _enso
from src.data_feeds import open_meteo as _met
from src.data_feeds import pnsn_seismic as _pnsn
from src.data_feeds import swpc_geomagnetic as _swpc
from src.data_feeds import usgs_seismic as _usgs
from src.data_feeds.snapshot import load as snap_load, save as snap_save
from src.realworld_comparison import comparison_summary, run_comparison


# ---------------------------------------------------------------------------
# Snapshot adapter tests
# ---------------------------------------------------------------------------

class TestSnapshotLoad:
    def test_load_returns_dict(self):
        data = snap_load("noaa_co2")
        assert isinstance(data, dict)

    def test_load_usgs_seismic_has_events(self):
        data = snap_load("usgs_seismic")
        assert "events" in data
        assert isinstance(data["events"], list)
        assert len(data["events"]) > 0

    def test_load_pnsn_seismic_has_events(self):
        data = snap_load("pnsn_seismic")
        assert "events" in data
        assert isinstance(data["events"], list)

    def test_load_missing_key_raises(self):
        with pytest.raises(KeyError):
            snap_load("__nonexistent_key__")

    def test_save_and_reload(self, tmp_path, monkeypatch):
        import json
        import pathlib

        fake_snap = tmp_path / "latest_snapshot.json"
        fake_snap.write_text("{}", encoding="utf-8")
        import src.data_feeds.snapshot as snap_mod

        monkeypatch.setattr(snap_mod, "_SNAPSHOT_PATH", fake_snap)
        snap_save("test_key", {"value": 42})
        result = snap_mod.load("test_key")
        assert result == {"value": 42}


# ---------------------------------------------------------------------------
# Individual adapter tests (snapshot mode)
# ---------------------------------------------------------------------------

class TestUSGSSeismic:
    def test_fetch_returns_dict(self):
        d = _usgs.fetch()
        assert isinstance(d, dict)

    def test_has_source(self):
        d = _usgs.fetch()
        assert "source" in d

    def test_events_list(self):
        d = _usgs.fetch()
        assert "events" in d
        assert isinstance(d["events"], list)

    def test_event_fields(self):
        events = _usgs.fetch()["events"]
        for ev in events:
            assert "place" in ev
            assert "magnitude" in ev
            assert isinstance(ev["magnitude"], float)
            assert "lat" in ev
            assert "lon" in ev
            assert "depth_km" in ev

    def test_magnitudes_positive(self):
        for ev in _usgs.fetch()["events"]:
            assert ev["magnitude"] >= 0.0


class TestPNSNSeismic:
    def test_fetch_returns_dict(self):
        d = _pnsn.fetch()
        assert isinstance(d, dict)

    def test_events_in_cascadia_bbox(self):
        for ev in _pnsn.fetch()["events"]:
            assert 40.0 <= ev["lat"] <= 52.0, f"lat {ev['lat']} out of Cascadia bbox"
            assert -130.0 <= ev["lon"] <= -116.0, f"lon {ev['lon']} out of bbox"


class TestNOAACO2:
    def test_fetch_returns_dict(self):
        d = _co2.fetch()
        assert isinstance(d, dict)

    def test_co2_ppm_range(self):
        d = _co2.fetch()
        assert 380.0 < d["co2_ppm"] < 500.0, f"co2_ppm={d['co2_ppm']} out of plausible range"

    def test_has_date(self):
        d = _co2.fetch()
        assert "date" in d
        assert len(d["date"]) == 10  # YYYY-MM-DD


class TestNOAACH4:
    def test_fetch_returns_dict(self):
        d = _ch4.fetch()
        assert isinstance(d, dict)

    def test_ch4_ppb_range(self):
        d = _ch4.fetch()
        assert 1700.0 < d["ch4_ppb"] < 2200.0, f"ch4_ppb={d['ch4_ppb']} unexpected"

    def test_has_year(self):
        d = _ch4.fetch()
        assert "year" in d
        assert d["year"] >= 2020


class TestOpenMeteo:
    def test_fetch_returns_dict(self):
        d = _met.fetch()
        assert isinstance(d, dict)

    def test_delta_T_plausible(self):
        d = _met.fetch()
        assert 0.5 < d["delta_T_C"] < 3.0, f"delta_T_C={d['delta_T_C']} implausible"

    def test_baseline(self):
        d = _met.fetch()
        assert d["T_baseline_C"] == pytest.approx(14.0)

    def test_consistency(self):
        d = _met.fetch()
        assert d["delta_T_C"] == pytest.approx(
            d["T_global_C"] - d["T_baseline_C"], abs=0.01
        )


class TestSWPCGeomagnetic:
    def test_fetch_returns_dict(self):
        d = _swpc.fetch()
        assert isinstance(d, dict)

    def test_kp_range(self):
        d = _swpc.fetch()
        assert 0.0 <= d["kp_index"] <= 9.0

    def test_B_nT_positive(self):
        d = _swpc.fetch()
        assert d["B_nT"] > 0.0


class TestNOAAENSO:
    def test_fetch_returns_dict(self):
        d = _enso.fetch()
        assert isinstance(d, dict)

    def test_phase_valid(self):
        d = _enso.fetch()
        assert d["phase"] in {"el_nino", "la_nina", "neutral"}

    def test_anomaly_in_range(self):
        d = _enso.fetch()
        assert -4.0 < d["nino34_anomaly_C"] < 4.0

    def test_phase_consistent_with_anomaly(self):
        d = _enso.fetch()
        a = d["nino34_anomaly_C"]
        phase = d["phase"]
        if a > 0.5:
            assert phase == "el_nino"
        elif a < -0.5:
            assert phase == "la_nina"
        else:
            assert phase == "neutral"


# ---------------------------------------------------------------------------
# run_comparison() integration tests
# ---------------------------------------------------------------------------

class TestRunComparison:
    @pytest.fixture(scope="class")
    def report(self):
        return run_comparison(live=False)

    def test_returns_dict(self, report):
        assert isinstance(report, dict)

    def test_expected_keys(self, report):
        expected = {
            "co2_radiative_forcing_Wm2",
            "co2_phi",
            "ch4_forcing_Wm2",
            "committed_delta_T_C",
            "surface_T_phi",
            "enso_phase",
            "elsasser_lambda",
        }
        assert expected.issubset(report.keys())

    def test_co2_forcing_ok(self, report):
        assert report["co2_radiative_forcing_Wm2"]["status"] == "ok"

    def test_ch4_forcing_ok(self, report):
        assert report["ch4_forcing_Wm2"]["status"] == "ok"

    def test_enso_phase_ok(self, report):
        assert report["enso_phase"]["status"] == "ok"

    def test_elsasser_ok(self, report):
        assert report["elsasser_lambda"]["status"] == "ok"

    def test_co2_forcing_positive(self, report):
        assert report["co2_radiative_forcing_Wm2"]["predicted"] > 0.0

    def test_ch4_forcing_positive(self, report):
        assert report["ch4_forcing_Wm2"]["predicted"] > 0.0

    def test_committed_delta_T_positive(self, report):
        assert report["committed_delta_T_C"]["predicted"] > 0.0

    def test_delta_T_plausible(self, report):
        dt = report["committed_delta_T_C"]["predicted"]
        assert 0.5 < dt < 5.0, f"committed ΔT={dt} outside plausible range"

    def test_enso_phase_string(self, report):
        assert report["enso_phase"]["predicted"] in {"el_nino", "la_nina", "neutral"}

    def test_elsasser_positive(self, report):
        assert report["elsasser_lambda"]["predicted"] > 0.0

    def test_all_entries_have_status(self, report):
        for key, val in report.items():
            assert "status" in val, f"Missing 'status' in {key}"
            assert val["status"] in {"ok", "warning"}, f"Bad status in {key}"


class TestComparisonSummary:
    def test_returns_string(self):
        report = run_comparison()
        summary = comparison_summary(report)
        assert isinstance(summary, str)

    def test_contains_metric_names(self):
        report = run_comparison()
        summary = comparison_summary(report)
        assert "co2_radiative_forcing_Wm2" in summary
        assert "enso_phase" in summary

    def test_contains_separators(self):
        summary = comparison_summary(run_comparison())
        assert "=" * 10 in summary
