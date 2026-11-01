# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 894 — alpha_s volume pinning."""
from __future__ import annotations

import pytest

from src.nined.pillar894_alpha_s_vol_pinning import (
    ALPHA_S_INTERVAL_PINNED,
    ALPHA_S_PINNED,
    ALPHA_S_PINNING_GATE,
    G_S_CANONICAL,
    G_S_SCAN,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    VOL_T2_ALPHA_PRIME,
    alpha_s_from_gs,
    inverse_g3_squared,
    vol_pinning_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 894

def test_gate_string(): assert PILLAR_GATE == "ALPHA_S_M7_VOL_PINNING"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_volume_value(): assert VOL_T2_ALPHA_PRIME == pytest.approx(74 / 25)

def test_volume_positive(): assert VOL_T2_ALPHA_PRIME > 0.0

def test_canonical_gs(): assert G_S_CANONICAL == pytest.approx(2.95)

def test_scan_length(): assert len(G_S_SCAN) == 3

def test_inverse_g3_positive(): assert inverse_g3_squared() > 0.0

def test_alpha_positive(): assert ALPHA_S_PINNED > 0.0

def test_alpha_interval_ordered(): assert ALPHA_S_INTERVAL_PINNED[0] < ALPHA_S_INTERVAL_PINNED[1]

def test_alpha_inside_interval(): assert ALPHA_S_INTERVAL_PINNED[0] <= ALPHA_S_PINNED <= ALPHA_S_INTERVAL_PINNED[1]

def test_gate_expected(): assert ALPHA_S_PINNING_GATE == "BOUNDED_NOT_PINNED"

def test_alpha_in_phenomenology_band(): assert 0.09 < ALPHA_S_PINNED < 0.13

def test_alpha_monotone_in_gs(): assert alpha_s_from_gs(G_S_SCAN[0]) < alpha_s_from_gs(G_S_SCAN[-1])

def test_summary_gate(): assert vol_pinning_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert vol_pinning_summary()["pillar"] == 894

def test_summary_status(): assert vol_pinning_summary()["status_label"] == STATUS_LABEL

def test_summary_result_gate(): assert vol_pinning_summary()["result_gate"] == ALPHA_S_PINNING_GATE

def test_summary_scan_matches(): assert vol_pinning_summary()["g_s_scan"] == list(G_S_SCAN)

def test_summary_interval_len(): assert len(vol_pinning_summary()["alpha_s_interval_pinned"]) == 2

def test_summary_alpha_match(): assert vol_pinning_summary()["alpha_s_pinned"] == pytest.approx(ALPHA_S_PINNED)

def test_no_toe_language(): assert "TOE" not in vol_pinning_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in vol_pinning_summary()
    return _test

globals()['test_generated_key_result_gate_0'] = _generated_key_test_factory('result_gate')
globals()['test_generated_key_alpha_prime_1'] = _generated_key_test_factory('alpha_prime')
globals()['test_generated_key_i3_topology_2'] = _generated_key_test_factory('i3_topology')
globals()['test_generated_key_g_s_canonical_3'] = _generated_key_test_factory('g_s_canonical')
globals()['test_generated_key_g_s_scan_4'] = _generated_key_test_factory('g_s_scan')
