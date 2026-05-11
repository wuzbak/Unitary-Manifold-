# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

from src.core.finish_line_observation_engine import (
    build_provenance_sync_payload,
    build_tracker_update_payload,
    build_wave_changelog_payload,
    normalize_observation_bundle,
    route_finish_line_observation_bundle,
)


def test_normalize_observation_bundle_defaults_to_all_channels():
    bundle = normalize_observation_bundle()
    assert set(bundle) == {"desi", "juno", "hyperk", "cmbs4", "litebird", "pmns", "lisa"}
    assert bundle["desi"]["mode"] == "published_dr2"
    assert "dm2_31_obs" in bundle["juno"]
    assert "sigma_pct" in bundle["juno"]
    assert "dm2_31_obs" in bundle["hyperk"]
    assert "sigma_pct" in bundle["hyperk"]
    assert "ns_obs" in bundle["cmbs4"]
    assert "r_obs" in bundle["cmbs4"]
    assert "beta_obs" in bundle["litebird"]
    assert "sigma" in bundle["litebird"]
    assert "sin2_theta12_obs" in bundle["pmns"]
    assert "omega_gw_obs" in bundle["lisa"]


def test_route_finish_line_observation_bundle_returns_payloads():
    result = route_finish_line_observation_bundle()
    assert "results" in result
    assert "tracker_update_payload" in result
    assert "wave_changelog_payload" in result
    assert "provenance_sync_payload" in result


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


def test_provenance_payload_targets_canonical_ledgers():
    result = route_finish_line_observation_bundle()
    payload = build_provenance_sync_payload(result["results"])
    assert "STATUS.md" in payload["target_files"]
    assert "docs/mas_tracker.yml" in payload["target_files"]
    assert payload["required_same_commit"] is True


def test_custom_bundle_can_route_falsification_paths():
    result = route_finish_line_observation_bundle(
        {
            "desi": {"wa": -0.62, "sigma": 0.18},
            "litebird": {"beta_obs": 0.30, "sigma": 0.002},
        }
    )
    assert result["results"]["desi"]["route"] == "FALSIFIED"
    assert result["results"]["litebird"]["zone"] == "GAP"


def test_partial_bundle_keeps_default_channels():
    result = route_finish_line_observation_bundle({"litebird": {"beta_obs": 0.331}})
    assert result["results"]["juno"]["experiment"] == "JUNO"
    assert result["results"]["hyperk"]["experiment"] == "Hyper-K"
    assert result["results"]["cmbs4"]["experiment"] == "CMB-S4 forecast"
    assert result["results"]["pmns"]["experiment"] == "NuFIT/PDG"
    assert result["results"]["lisa"]["experiment"] == "LISA forecast"
