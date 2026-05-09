# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

from src.core.finish_line_observation_engine import (
    build_tracker_update_payload,
    build_wave_changelog_payload,
    normalize_observation_bundle,
    route_finish_line_observation_bundle,
)


def test_normalize_observation_bundle_defaults_to_all_channels():
    bundle = normalize_observation_bundle()
    assert set(bundle) == {"desi", "juno", "hyperk", "cmbs4", "litebird"}


def test_route_finish_line_observation_bundle_returns_payloads():
    result = route_finish_line_observation_bundle()
    assert "results" in result
    assert "tracker_update_payload" in result
    assert "wave_changelog_payload" in result


def test_default_bundle_keeps_desi_as_high_tension_state():
    result = route_finish_line_observation_bundle()
    assert result["results"]["desi"]["current_status"] == "HIGH_TENSION"


def test_tracker_payload_targets_observation_tracker():
    result = route_finish_line_observation_bundle()
    payload = build_tracker_update_payload(result["results"])
    assert payload["target_file"] == "3-FALSIFICATION/OBSERVATION_TRACKER.md"
    assert payload["required_same_day_sync"] is True


def test_wave_payload_targets_wave_changelog():
    result = route_finish_line_observation_bundle()
    payload = build_wave_changelog_payload(result["results"])
    assert payload["target_file"] == "docs/WAVE_CHANGELOG.md"
    assert any("JUNO routed" in line for line in payload["what_changed"])


def test_custom_bundle_can_route_falsification_paths():
    result = route_finish_line_observation_bundle(
        {
            "desi": {"wa": -0.62, "sigma": 0.18},
            "litebird": {"beta_obs": 0.30, "sigma": 0.002},
        }
    )
    assert result["results"]["desi"]["route"] == "FALSIFIED"
    assert result["results"]["litebird"]["zone"] == "GAP"
