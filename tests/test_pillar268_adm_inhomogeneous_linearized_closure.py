# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 268 — ADM linearized inhomogeneous closure."""
from __future__ import annotations

from src.core.pillar268_adm_inhomogeneous_linearized_closure import (
    ADJACENCY_TRACK_LABEL,
    adm_linearized_inhomogeneous_report,
    linearized_constraint_packet,
    linearized_inhomogeneous_scan,
    linearized_kk_profile,
)


def test_linearized_profile_shapes():
    profile = linearized_kk_profile()
    assert profile["phi"].shape == (64,)
    assert profile["B"].shape == (64, 4)
    assert profile["g"].shape == (64, 4, 4)


def test_linearized_packet_has_verdict():
    packet = linearized_constraint_packet()
    assert packet["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert packet["verdict"] in {"PASS", "TENSION", "FALSIFIED"}


def test_scan_is_nonempty():
    scan = linearized_inhomogeneous_scan()
    assert scan["n_packets"] == 9
    assert scan["pass_count"] + scan["tension_count"] <= scan["n_packets"]


def test_report_status_and_scope():
    report = adm_linearized_inhomogeneous_report()
    assert report["status"] in {
        "KINEMATIC_AND_LINEARIZED_DYNAMICAL_CLOSED",
        "KINEMATIC_CLOSED_LINEARIZED_TENSION",
    }
    assert "Non-perturbative" in report["remaining_open"]
