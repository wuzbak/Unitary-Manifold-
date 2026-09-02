# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 965 — Quark/Lepton c_L Splitting."""

import pytest
from src.core.pillar965_quark_lepton_cl_splitting import (
    K_CS,
    N_W,
    N_C,
    CL_LEPTON,
    CL_QUARK,
    DELTA_CL_QL,
    PILLAR_STATUS,
    PILLAR_VALID,
    cl_splitting_derivation,
    aps_color_index,
    quark_lepton_splitting_table,
    fallibility_update,
    pillar965_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "QUARK_LEPTON_CL_SPLITTING_DERIVED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert N_C == 3


def test_lepton_constant():
    assert CL_LEPTON == pytest.approx(69.0 / 74.0)


def test_quark_constant():
    assert CL_QUARK == pytest.approx(66.0 / 74.0)


def test_delta_constant():
    assert DELTA_CL_QL == pytest.approx(3.0 / 74.0)


def test_quark_less_than_lepton():
    assert CL_QUARK < CL_LEPTON


def test_splitting_derivation_values():
    result = cl_splitting_derivation()
    assert result["c_L_lepton"] == pytest.approx(CL_LEPTON)
    assert result["c_L_quark"] == pytest.approx(CL_QUARK)
    assert result["delta"] == pytest.approx(DELTA_CL_QL)


def test_splitting_derivation_source():
    result = cl_splitting_derivation()
    assert result["source"] == "APS_SU3_monodromy"


def test_aps_color_index_values():
    result = aps_color_index()
    assert result["N_c"] == 3
    assert result["K_CS"] == 74
    assert result["eta_color"] == pytest.approx(3.0 / 74.0)


def test_aps_color_index_derivation_text():
    result = aps_color_index()
    assert "SU(3)_C" in result["derivation"]
    assert "Atiyah-Patodi-Singer" in result["boundary_condition"]


def test_splitting_table_has_generations():
    result = quark_lepton_splitting_table()
    assert set(result["lepton"].keys()) == {"Gen 1", "Gen 2", "Gen 3"}


def test_splitting_table_gen_values():
    result = quark_lepton_splitting_table()
    assert result["lepton"]["Gen 1"]["c_L_lepton"] == pytest.approx(CL_LEPTON)
    assert result["lepton"]["Gen 2"]["c_L_quark"] == pytest.approx(CL_QUARK)


def test_splitting_table_universal_flag():
    result = quark_lepton_splitting_table()
    assert result["universal_split"] is True


def test_fallibility_update_upgrade():
    result = fallibility_update()
    assert result["pillar"] == 965
    assert "SPLITTING_DERIVED" in result["new_status"]


def test_summary_identity():
    result = pillar965_summary()
    assert result["pillar"] == 965
    assert result["status"] == PILLAR_STATUS
    assert result["valid"] is True


def test_summary_contains_sections():
    result = pillar965_summary()
    for key in ("derivation", "aps_index", "splitting_table", "fallibility_update"):
        assert key in result


def test_summary_derivation_chain_length():
    result = pillar965_summary()
    assert len(result["derivation_chain"]) >= 4
