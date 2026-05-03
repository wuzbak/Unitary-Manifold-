# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_m_theory_embedding.py
=================================
Tests for Pillar 113 — M-Theory Embedding G₄
(src/core/m_theory_embedding.py).
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.m_theory_embedding import (
    horava_witten_setup,
    g4_flux_quantization,
    cy3_euler_characteristic,
    kcs_from_m_theory,
    braid_from_m_theory_fluxes,
    m_theory_embedding_summary,
    K_CS,
    WINDING_NUMBER,
)


# ---------------------------------------------------------------------------
# horava_witten_setup
# ---------------------------------------------------------------------------

class TestHoravaWittenSetup:
    def setup_method(self):
        self.hw = horava_witten_setup()

    def test_returns_dict(self):
        assert isinstance(self.hw, dict)

    def test_key_bulk_dim(self):
        assert "bulk_dim" in self.hw

    def test_key_boundary_dim(self):
        assert "boundary_dim" in self.hw

    def test_key_compact_dim(self):
        assert "compact_dim" in self.hw

    def test_key_interval_dim(self):
        assert "interval_dim" in self.hw

    def test_key_total(self):
        assert "total" in self.hw

    def test_key_um_sector_dim(self):
        assert "um_sector_dim" in self.hw

    def test_bulk_dim_11(self):
        assert self.hw["bulk_dim"] == 11

    def test_boundary_dim_10(self):
        assert self.hw["boundary_dim"] == 10

    def test_compact_dim_6(self):
        assert self.hw["compact_dim"] == 6

    def test_interval_dim_1(self):
        assert self.hw["interval_dim"] == 1

    def test_total_11(self):
        assert self.hw["total"] == 11

    def test_um_sector_dim_5(self):
        assert self.hw["um_sector_dim"] == 5

    def test_dimensions_consistent(self):
        hw = self.hw
        assert hw["boundary_dim"] == hw["bulk_dim"] - 1

    def test_um_sector_is_interval_plus_4d(self):
        hw = self.hw
        assert hw["um_sector_dim"] == hw["interval_dim"] + 4

    def test_six_keys(self):
        assert len(self.hw) == 6


# ---------------------------------------------------------------------------
# g4_flux_quantization
# ---------------------------------------------------------------------------

class TestG4FluxQuantization:
    def test_default_returns_37(self):
        assert g4_flux_quantization() == 37

    def test_returns_int(self):
        assert isinstance(g4_flux_quantization(), int)

    def test_explicit_kcs_74(self):
        assert g4_flux_quantization(k_cs=74) == 37

    def test_kcs_100(self):
        assert g4_flux_quantization(k_cs=100) == 50

    def test_kcs_2(self):
        assert g4_flux_quantization(k_cs=2) == 1

    def test_half_of_kcs(self):
        for k in [10, 20, 74, 100, 148]:
            assert g4_flux_quantization(k_cs=k) == k // 2

    def test_kcs_constant(self):
        assert K_CS == 74

    def test_result_positive(self):
        assert g4_flux_quantization() > 0


# ---------------------------------------------------------------------------
# cy3_euler_characteristic
# ---------------------------------------------------------------------------

class TestCy3EulerCharacteristic:
    def setup_method(self):
        self.chi = cy3_euler_characteristic()

    def test_returns_list(self):
        assert isinstance(self.chi, list)

    def test_length_4(self):
        assert len(self.chi) == 4

    def test_contains_negative_values(self):
        assert any(c < 0 for c in self.chi)

    def test_contains_positive_values(self):
        assert any(c > 0 for c in self.chi)

    def test_all_integers(self):
        for c in self.chi:
            assert isinstance(c, int)

    def test_contains_minus_200(self):
        assert -200 in self.chi

    def test_contains_200(self):
        assert 200 in self.chi

    def test_contains_minus_6(self):
        assert -6 in self.chi

    def test_contains_6(self):
        assert 6 in self.chi

    def test_symmetric_around_zero(self):
        pos = sorted([c for c in self.chi if c > 0])
        neg = sorted([abs(c) for c in self.chi if c < 0])
        assert pos == neg


# ---------------------------------------------------------------------------
# kcs_from_m_theory
# ---------------------------------------------------------------------------

class TestKcsFromMTheory:
    def test_default_returns_74(self):
        assert kcs_from_m_theory() == 74

    def test_returns_int(self):
        assert isinstance(kcs_from_m_theory(), int)

    def test_explicit_37(self):
        assert kcs_from_m_theory(n_flux=37) == 74

    def test_n_flux_1(self):
        assert kcs_from_m_theory(n_flux=1) == 2

    def test_n_flux_50(self):
        assert kcs_from_m_theory(n_flux=50) == 100

    def test_inverse_of_g4(self):
        n = g4_flux_quantization(k_cs=74)
        assert kcs_from_m_theory(n_flux=n) == 74

    def test_roundtrip(self):
        for k in [10, 74, 100, 148]:
            n = g4_flux_quantization(k_cs=k)
            assert kcs_from_m_theory(n_flux=n) == k


# ---------------------------------------------------------------------------
# braid_from_m_theory_fluxes
# ---------------------------------------------------------------------------

class TestBraidFromMTheoryFluxes:
    def setup_method(self):
        self.b = braid_from_m_theory_fluxes()

    def test_returns_dict(self):
        assert isinstance(self.b, dict)

    def test_key_n_w(self):
        assert "n_w" in self.b

    def test_key_k_cs(self):
        assert "k_cs" in self.b

    def test_key_interpretation(self):
        assert "interpretation" in self.b

    def test_key_status(self):
        assert "status" in self.b

    def test_n_w_is_5(self):
        assert self.b["n_w"] == 5

    def test_k_cs_is_74(self):
        assert self.b["k_cs"] == 74

    def test_status_conjectural(self):
        assert self.b["status"] == "CONJECTURAL"

    def test_interpretation_is_string(self):
        assert isinstance(self.b["interpretation"], str)

    def test_four_keys(self):
        assert len(self.b) == 4


# ---------------------------------------------------------------------------
# m_theory_embedding_summary
# ---------------------------------------------------------------------------

class TestMTheoryEmbeddingSummary:
    def setup_method(self):
        self.s = m_theory_embedding_summary()

    def test_returns_dict(self):
        assert isinstance(self.s, dict)

    def test_key_setup(self):
        assert "setup" in self.s

    def test_key_g4_flux(self):
        assert "g4_flux" in self.s

    def test_key_kcs_reconstructed(self):
        assert "kcs_reconstructed" in self.s

    def test_key_braid_interpretation(self):
        assert "braid_interpretation" in self.s

    def test_key_embedding_status(self):
        assert "embedding_status" in self.s

    def test_embedding_status_partial(self):
        assert self.s["embedding_status"] == "PARTIAL"

    def test_g4_flux_37(self):
        assert self.s["g4_flux"] == 37

    def test_kcs_reconstructed_74(self):
        assert self.s["kcs_reconstructed"] == 74

    def test_setup_is_dict(self):
        assert isinstance(self.s["setup"], dict)

    def test_braid_interpretation_is_dict(self):
        assert isinstance(self.s["braid_interpretation"], dict)

    def test_five_keys(self):
        assert len(self.s) == 5

    def test_winding_number_constant(self):
        assert WINDING_NUMBER == 5
