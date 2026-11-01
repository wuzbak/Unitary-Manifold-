# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 889 — FN-corrected Jarlskog invariant."""
from __future__ import annotations

import numpy as np
import pytest

from src.sevend.pillar889_jarlskog_fn import (
    JARLSKOG_GATE,
    J_FN,
    J_PDG,
    PILLAR_GATE,
    PILLAR_NUMBER,
    RATIO_J_FN_VS_PDG,
    STATUS_LABEL,
    ckm_fn_complex_matrix,
    jarlskog_fn_summary,
    jarlskog_invariant,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 889

def test_gate_string(): assert PILLAR_GATE == "JARLSKOG_7D_NLO_FN"

def test_status_allowed(): assert STATUS_LABEL in ALLOWED

def test_fn_verdict_allowed(): assert JARLSKOG_GATE in {"JARLSKOG_7D_NLO_FN_IMPROVED", "MAGNITUDE_OPEN"}

def test_ckm_complex_shape(): assert ckm_fn_complex_matrix().shape == (3, 3)

def test_ckm_complex_dtype(): assert np.iscomplexobj(ckm_fn_complex_matrix())

def test_ckm_complex_unitary():
    matrix = ckm_fn_complex_matrix()
    assert np.allclose(matrix @ matrix.conj().T, np.eye(3), atol=1e-10)

def test_j_positive(): assert J_FN > 0.0

def test_j_smaller_than_pdg(): assert J_FN < J_PDG

def test_ratio_positive(): assert RATIO_J_FN_VS_PDG > 0.0

def test_ratio_below_one(): assert RATIO_J_FN_VS_PDG < 1.0

def test_ratio_far_from_one(): assert abs(RATIO_J_FN_VS_PDG - 1.0) > 0.5

def test_invariant_matches_default(): assert jarlskog_invariant(ckm_fn_complex_matrix()) == pytest.approx(J_FN, rel=1e-12)

def test_invariant_rejects_wrong_shape():
    with pytest.raises(ValueError):
        jarlskog_invariant(np.eye(2, dtype=complex))


def test_summary_gate(): assert jarlskog_fn_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert jarlskog_fn_summary()["pillar"] == 889

def test_summary_status(): assert jarlskog_fn_summary()["status_label"] == STATUS_LABEL

def test_summary_verdict(): assert jarlskog_fn_summary()["fn_verdict"] == JARLSKOG_GATE

def test_summary_sign_correct(): assert jarlskog_fn_summary()["sign_correct"] is True

def test_summary_angle_keys(): assert set(jarlskog_fn_summary()["angles_deg"]) == {"theta_12", "theta_13", "theta_23"}

def test_summary_ratio_positive(): assert jarlskog_fn_summary()["ratio_j_fn_vs_pdg"] > 0.0

def test_summary_tension_positive(): assert jarlskog_fn_summary()["j_tension_sigma"] > 0.0

def test_summary_delta_cp_positive(): assert jarlskog_fn_summary()["delta_cp_deg"] > 0.0

def test_no_toe_language(): assert "TOE" not in jarlskog_fn_summary()["epistemic_status"].upper()


def _generated_key_test_factory(key):
    def _test():
        assert key in jarlskog_fn_summary()
    return _test

globals()['test_generated_key_j_fn_0'] = _generated_key_test_factory('j_fn')
globals()['test_generated_key_j_pdg_1'] = _generated_key_test_factory('j_pdg')
globals()['test_generated_key_ratio_j_fn_vs_pdg_2'] = _generated_key_test_factory('ratio_j_fn_vs_pdg')
globals()['test_generated_key_j_tension_sigma_3'] = _generated_key_test_factory('j_tension_sigma')
globals()['test_generated_key_delta_cp_deg_4'] = _generated_key_test_factory('delta_cp_deg')
