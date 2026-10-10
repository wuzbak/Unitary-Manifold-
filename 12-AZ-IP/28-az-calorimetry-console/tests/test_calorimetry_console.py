# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_calorimetry_console import generate_run_sheet, COPTracker
from az_calorimetry_console.run_sheet import LOADING_TARGET, COP_PASS_THRESHOLD


def test_loading_target_matches_canonical_resonance():
    assert LOADING_TARGET == 0.875


def test_generate_run_sheet_shape():
    sheet = generate_run_sheet()
    d = sheet.to_dict()
    assert d["loading_target"] == LOADING_TARGET
    assert d["cop_pass_threshold"] == COP_PASS_THRESHOLD
    assert len(d["steps"]) == 7
    assert d["steps"][0]["target_loading_ratio"] < d["steps"][-1]["target_loading_ratio"]
    assert d["steps"][-1]["target_loading_ratio"] == pytest.approx(LOADING_TARGET)


def test_generate_run_sheet_monotonic_loading_curve():
    sheet = generate_run_sheet(temperature_ramp_c=[20, 40, 60, 80])
    loadings = [s.target_loading_ratio for s in sheet.steps]
    assert loadings == sorted(loadings)


def test_generate_run_sheet_rejects_empty_ramp():
    with pytest.raises(ValueError):
        generate_run_sheet(temperature_ramp_c=[])


def test_cop_tracker_awaiting_data_before_any_reading():
    tracker = COPTracker()
    assert tracker.verdict() == "AWAITING_DATA"
    assert tracker.latest_cop() is None


def test_cop_tracker_no_excess_heat_below_threshold():
    tracker = COPTracker()
    tracker.ingest(0.0, power_in_w=100.0, power_out_w=100.5)
    assert tracker.verdict() == "NO_EXCESS_HEAT"


def test_cop_tracker_excess_heat_above_threshold():
    tracker = COPTracker()
    tracker.ingest(0.0, power_in_w=100.0, power_out_w=102.0)
    assert tracker.verdict() == "EXCESS_HEAT_OBSERVED"


def test_cop_tracker_rejects_nonpositive_input_power():
    tracker = COPTracker()
    with pytest.raises(ValueError):
        tracker.ingest(0.0, power_in_w=0.0, power_out_w=10.0)


def test_cop_tracker_mean_cop_across_multiple_readings():
    tracker = COPTracker()
    tracker.ingest(0.0, 100.0, 99.0)
    tracker.ingest(1.0, 100.0, 103.0)
    report = tracker.to_report()
    assert report["n_readings"] == 2
    assert report["mean_cop"] == pytest.approx((0.99 + 1.03) / 2)
