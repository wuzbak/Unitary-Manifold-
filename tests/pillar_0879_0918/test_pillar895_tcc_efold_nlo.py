# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 895 — TCC e-fold audit."""
from __future__ import annotations

import pytest

from src.core.pillar895_tcc_efold_nlo import (
    BRAIDED_SOUND_SPEED,
    N_EFOLD_LO,
    N_EFOLD_NLO,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    TCC_BOUND,
    TCC_GATE,
    quintessence_eos,
    rolling_efolds,
    tcc_efold_summary,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 895

def test_gate_string(): assert PILLAR_GATE == "TCC_EFOLD_NLO_AUDIT"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_sound_speed_value(): assert BRAIDED_SOUND_SPEED == pytest.approx(12 / 37)

def test_quintessence_today(): assert quintessence_eos(1.0) == pytest.approx(-1.05)

def test_quintessence_early(): assert quintessence_eos(0.5) == pytest.approx(-0.975)

def test_quintessence_rejects_zero():
    with pytest.raises(ValueError):
        quintessence_eos(0.0)


def test_rolling_efolds_positive(): assert rolling_efolds() > 0.0

def test_lo_positive(): assert N_EFOLD_LO > 0.0

def test_nlo_positive(): assert N_EFOLD_NLO > 0.0

def test_nlo_less_than_lo(): assert N_EFOLD_NLO < N_EFOLD_LO

def test_nlo_matches_sound_speed(): assert N_EFOLD_NLO == pytest.approx(N_EFOLD_LO * BRAIDED_SOUND_SPEED)

def test_bound_large(): assert TCC_BOUND > 1e4

def test_nlo_below_bound(): assert N_EFOLD_NLO < TCC_BOUND

def test_gate_resolved(): assert TCC_GATE == "TCC_TENSION_RESOLVED_BY_ROLLING"

def test_summary_gate(): assert tcc_efold_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert tcc_efold_summary()["pillar"] == 895

def test_summary_status(): assert tcc_efold_summary()["status_label"] == STATUS_LABEL

def test_summary_result_gate(): assert tcc_efold_summary()["result_gate"] == TCC_GATE

def test_summary_nlo_below_bound(): assert tcc_efold_summary()["n_efold_nlo"] < tcc_efold_summary()["tcc_bound"]

def test_summary_h_inf_positive(): assert tcc_efold_summary()["h_inf"] > 0.0

def test_no_toe_language(): assert "TOE" not in tcc_efold_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in tcc_efold_summary()
    return _test

globals()['test_generated_key_w0_quintessence_0'] = _generated_key_test_factory('w0_quintessence')
globals()['test_generated_key_wa_quintessence_1'] = _generated_key_test_factory('wa_quintessence')
globals()['test_generated_key_braided_sound_speed_2'] = _generated_key_test_factory('braided_sound_speed')
globals()['test_generated_key_n_efold_lo_3'] = _generated_key_test_factory('n_efold_lo')
globals()['test_generated_key_n_efold_nlo_4'] = _generated_key_test_factory('n_efold_nlo')
