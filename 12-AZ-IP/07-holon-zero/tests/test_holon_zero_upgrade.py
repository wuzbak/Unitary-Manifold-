# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Upgrade tests for the Holon Zero governance app."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from holon_zero.engine.holon_explorer import HOLON_HIERARCHY, expand_holon
from holon_zero.engine.phi0_calibration import (
    OMEGA_0_SUB_PILLARS,
    PHI_0_STATUS,
    calibrate_ground_state,
    get_sub_pillar,
    run_ground_state_audit,
)


def test_phi0_status_exact_values():
    assert PHI_0_STATUS["value"] == 1.0
    assert PHI_0_STATUS["closure"] == "PARTIAL"
    assert PHI_0_STATUS["pillar"] == "P853"


def test_phi0_status_carries_caveat():
    assert "remains open" in PHI_0_STATUS["caveat"]


def test_calibrate_ground_state_default_is_consistent():
    result = calibrate_ground_state()
    assert result["phi0"] == 1.0
    assert result["kk_mass_ratio"] == 1.0
    assert result["status"] == "CONSISTENT"


def test_calibrate_ground_state_drifted_case():
    result = calibrate_ground_state(1.2)
    assert result["status"] == "DRIFTED"
    assert result["radion_vev"] > 2.0


def test_sub_pillars_registered():
    assert [pillar["id"] for pillar in OMEGA_0_SUB_PILLARS] == ["70-B", "70-C", "70-D"]


@pytest.mark.parametrize("sub_id", ["70-B", "70-C", "70-D"])
def test_get_sub_pillar_by_id(sub_id):
    assert get_sub_pillar(sub_id)["id"] == sub_id


def test_get_sub_pillar_is_case_insensitive():
    assert get_sub_pillar("70-c")["name"] == "Co-emergence coupling"


def test_get_sub_pillar_invalid_raises():
    with pytest.raises(KeyError):
        get_sub_pillar("70-Z")


def test_run_ground_state_audit_is_consistent():
    audit = run_ground_state_audit()
    assert audit["consistent"] is True
    assert audit["omega_0"] == "Ω₀ Ground State"


def test_run_ground_state_audit_counts_subpillars():
    audit = run_ground_state_audit()
    assert audit["n_sub_pillars"] == len(OMEGA_0_SUB_PILLARS)
    assert len(audit["sub_pillars"]) == len(OMEGA_0_SUB_PILLARS)


def test_run_ground_state_audit_includes_partial_closure_note():
    audit = run_ground_state_audit()
    assert audit["phi0_status"]["closure"] == "PARTIAL"


def test_holon_hierarchy_exact_sequence():
    assert HOLON_HIERARCHY == [
        "Ω₀ Ground State",
        "P1-P208 Hardgate Physics",
        "P209-P785 Adjacent Tracks",
        "Unitary Pentad HILS",
    ]


def test_expand_root_holon():
    root = expand_holon("Ω₀ Ground State")
    assert root["parent"] is None
    assert root["children"] == HOLON_HIERARCHY[1:]
    assert root["coupling_strength"] == 1.0


def test_expand_hardgate_holon():
    node = expand_holon("P1-P208 Hardgate Physics")
    assert node["parent"] == "Ω₀ Ground State"
    assert node["children"] == []
    assert node["coupling_strength"] == 0.95


def test_expand_adjacent_holon():
    node = expand_holon("adjacent")
    assert node["holon_id"] == "P209-P785 Adjacent Tracks"
    assert node["coupling_strength"] == 0.74


def test_expand_pentad_holon_uses_xi_c_fraction():
    node = expand_holon("pentad")
    assert node["coupling_strength"] == pytest.approx(35 / 74)


def test_expand_holon_alias_for_omega0():
    node = expand_holon("omega0")
    assert node["holon_id"] == "Ω₀ Ground State"


def test_expand_holon_invalid_raises():
    with pytest.raises(KeyError):
        expand_holon("unknown")
