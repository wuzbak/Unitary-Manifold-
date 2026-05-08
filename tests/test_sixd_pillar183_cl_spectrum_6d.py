# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/sixd/pillar183_cl_spectrum_6d.py."""

from __future__ import annotations

import math

from src.sixd.pillar183_cl_spectrum_6d import (
    CHARGE_QUANTA,
    KAEHLER_UPLIFT,
    K_CS,
    N_W,
    PI_KR,
    cl_spectrum_pillar183,
    pillar183_closure_report,
    yukawa_ratio_spectrum_pillar183,
)


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert PI_KR == K_CS / 2.0


def test_charge_quanta_present():
    assert set(CHARGE_QUANTA.keys()) == {"top", "bottom", "tau", "electron"}
    assert CHARGE_QUANTA["top"] == 0


def test_cl_spectrum_monotone():
    c_l = cl_spectrum_pillar183()
    assert c_l["top"] < c_l["bottom"] < c_l["tau"] < c_l["electron"]
    for fermion, qf in CHARGE_QUANTA.items():
        assert c_l[fermion] == 0.5 + qf / (4.0 * K_CS)


def test_ratio_hierarchy():
    ratios = yukawa_ratio_spectrum_pillar183()
    c_l = cl_spectrum_pillar183()
    assert ratios["top"] > ratios["bottom"] > ratios["tau"] > ratios["electron"]
    for fermion in CHARGE_QUANTA:
        expected = math.exp(-PI_KR * (c_l[fermion] - c_l["top"])) * KAEHLER_UPLIFT[fermion]
        assert ratios[fermion] == expected


def test_electron_has_kaehler_uplift():
    assert KAEHLER_UPLIFT["electron"] > 1.0
    assert KAEHLER_UPLIFT["top"] == 1.0


def test_closure_report_axiomzero():
    report = pillar183_closure_report()
    assert report["pillar"] == 183
    assert report["axiomzero_purity"] is True
    assert report["pdg_anchors_used"] == []
