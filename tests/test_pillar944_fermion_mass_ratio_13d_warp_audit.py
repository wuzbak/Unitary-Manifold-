# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 944 — Fermion Mass Ratio 13D Orbifold Warp Audit."""
from __future__ import annotations
import math
from src.core.pillar944_fermion_mass_ratio_13d_warp_audit import (
    LEPTON_MASS_RATIOS_13D,
    LEPTON_MASS_RATIOS_PDG,
    LEPTON_RATIO_RESIDUALS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    QUARK_MASS_RATIOS_13D,
    QUARK_MASS_RATIOS_PDG,
    QUARK_RATIO_RESIDUALS,
    WARP_FACTORS,
    fermion_mass_ratio_13d_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 944
def test_gate(): assert PILLAR_GATE == "FERMION_MASS_RATIO_13D_ORBIFOLD_WARP_AUDIT"

def test_warp_factors_keys():
    for k in ["gen1", "gen2", "gen3"]:
        assert k in WARP_FACTORS

def test_warp_factors_positive():
    for v in WARP_FACTORS.values():
        assert v > 0

def test_warp_factors_decreasing():
    assert WARP_FACTORS["gen1"] > WARP_FACTORS["gen2"] > WARP_FACTORS["gen3"]

def test_warp_gen1_range():
    # exp(-5π) < ε₁ = exp(-5π) — this is gen1
    assert 0 < WARP_FACTORS["gen1"] < 1

def test_quark_pdg_keys():
    for k in ["m_u_over_m_t", "m_d_over_m_b", "m_s_over_m_b"]:
        assert k in QUARK_MASS_RATIOS_PDG

def test_quark_pdg_positive():
    for v in QUARK_MASS_RATIOS_PDG.values():
        assert v > 0

def test_lepton_pdg_keys():
    for k in ["m_e_over_m_tau", "m_mu_over_m_tau"]:
        assert k in LEPTON_MASS_RATIOS_PDG

def test_lepton_pdg_positive():
    for v in LEPTON_MASS_RATIOS_PDG.values():
        assert v > 0

def test_quark_13d_positive():
    for v in QUARK_MASS_RATIOS_13D.values():
        assert v > 0

def test_lepton_13d_positive():
    for v in LEPTON_MASS_RATIOS_13D.values():
        assert v > 0

def test_quark_residuals_nonneg():
    for v in QUARK_RATIO_RESIDUALS.values():
        assert v >= 0

def test_lepton_residuals_nonneg():
    for v in LEPTON_RATIO_RESIDUALS.values():
        assert v >= 0

def test_status_set():
    assert PILLAR_STATUS in {
        "FERMION_MASS_RATIO_13D_CLOSED",
        "FERMION_MASS_RATIO_13D_PARTIAL",
        "FERMION_MASS_RATIO_13D_IRREDUCIBLE",
    }

def test_pillar_valid():
    assert PILLAR_VALID is True

def test_summary_keys():
    s = fermion_mass_ratio_13d_summary()
    for key in ["pillar", "gate", "status", "valid", "warp_factors",
                "quark_ratios_pdg", "lepton_ratios_pdg", "n_pass", "n_total"]:
        assert key in s

def test_summary_pillar():
    assert fermion_mass_ratio_13d_summary()["pillar"] == 944

def test_n_total():
    s = fermion_mass_ratio_13d_summary()
    assert s["n_total"] == 5  # 3 quark + 2 lepton

def test_n_pass_le_n_total():
    s = fermion_mass_ratio_13d_summary()
    assert s["n_pass"] <= s["n_total"]

def test_generation_hierarchy_direction():
    # m_u/m_t < m_s/m_b: up quark much lighter than strange
    assert QUARK_MASS_RATIOS_PDG["m_u_over_m_t"] < QUARK_MASS_RATIOS_PDG["m_s_over_m_b"]

def test_log_residual_positive():
    for v in list(QUARK_RATIO_RESIDUALS.values()) + list(LEPTON_RATIO_RESIDUALS.values()):
        assert math.isfinite(v)
        assert v >= 0
