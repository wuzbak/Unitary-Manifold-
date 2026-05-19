# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from src.core.pillar231_lisa_omega_gw_preregistration_package import (
    ADJACENCY_TRACK_LABEL,
    omega_gw_preregistration_bounds,
    pillar231_preregistration_packet,
)


def test_prereg_bounds():
    b = omega_gw_preregistration_bounds()
    assert b["f_min_hz"] < b["f_max_hz"]
    assert b["alert_sigma"] == 3.0


def test_prereg_packet_status():
    p = pillar231_preregistration_packet()
    assert p["pillar"] == 231
    assert p["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert p["status"] == "PREREGISTERED"
