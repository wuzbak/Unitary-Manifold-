# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 998 — unified UV/global-geometry + flavor completion attempt."""

from __future__ import annotations

from src.core.pillar998_unified_uv_flavor_completion_attempt import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    joint_uv_flavor_attempt,
    pillar998_summary,
    shared_parent_state_from_tau_rho,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 998
    assert PILLAR_GATE == "UNIFIED_UV_GLOBAL_GEOMETRY_FLAVOR_COMPLETION_ATTEMPT"
    assert PILLAR_STATUS == "UNIFIED_UV_FLAVOR_COMPLETION_ATTEMPT_COMPLETE"
    assert PILLAR_VALID is True


def test_shared_parent_state_shape() -> None:
    state = shared_parent_state_from_tau_rho(1.03, 0.80)
    assert state["n_w"] == 5.0
    assert state["k_cs"] == 74.0
    assert state["tau"] > 0.0
    assert state["rho"] > 0.0


def test_joint_attempt_metadata() -> None:
    report = joint_uv_flavor_attempt()
    assert report["pillar"] == 998
    assert report["search_domain"]["single_shared_parent_state_only"] is True
    assert report["search_domain"]["per_lane_rescue_parameters_allowed"] == 0


def test_joint_attempt_is_honest_architecture_limit() -> None:
    report = joint_uv_flavor_attempt()
    assert report["runtime_status"] == "UNIFIED_UV_FLAVOR_ARCHITECTURE_LIMIT_CERTIFIED"
    assert report["closed"] is False


def test_alpha_and_ckm_packets_present() -> None:
    report = joint_uv_flavor_attempt()
    best = report["best_joint_point"]
    assert best["alpha_s"]["inside_tightened_window"] is False
    assert best["alpha_s"]["pdg_rel_error"] > 0.05
    assert "theta13_rel_error" in best["ckm"]
    assert "vub_rel_error" in best["ckm"]


def test_fermion_attempt_keeps_hierarchy() -> None:
    report = joint_uv_flavor_attempt()
    best = report["best_joint_point"]
    assert best["fermion"]["hierarchy_ok"] is True
    assert len(best["fermion"]["generation_radii"]) == 3


def test_blocking_lanes_cover_full_family() -> None:
    report = joint_uv_flavor_attempt()
    lanes = {row["lane"] for row in report["blocking_lanes"]}
    assert "ALPHA_S_TYPE_B_FLOOR" in lanes
    assert "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED" in lanes
    assert "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED" in lanes
    assert "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW" in lanes
    assert "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED" in lanes


def test_missing_objects_named() -> None:
    report = joint_uv_flavor_attempt()
    assert "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR" in report["named_missing_objects"]
    assert "SPECIES_RESOLVED_RI_GEOMETRY_WITH_BUNDLE_MODULI_LOCK" in report["named_missing_objects"]


def test_summary() -> None:
    summary = pillar998_summary()
    assert summary["pillar"] == 998
    assert summary["runtime_status"] == "UNIFIED_UV_FLAVOR_ARCHITECTURE_LIMIT_CERTIFIED"
    assert summary["joint_score"] >= 0.0
