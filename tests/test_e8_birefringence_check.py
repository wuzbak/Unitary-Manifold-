# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 177 — E8 Birefringence Check."""
import pytest
from src.core.e8_birefringence_check import (
    UM_BETA_CANONICAL_DEG, UM_ADMISSIBLE_MIN_DEG, UM_ADMISSIBLE_MAX_DEG,
    LITEBIRD_LAUNCH_YEAR, E8_DIM, E8_RANK, N_W, K_CS, K_E8,
    um_birefringence_angles_deg, e8_chern_simons_level, e8_birefringence_estimate_deg,
    um_e8_beta_overlap, litebird_discriminability, e8_birefringence_audit, pillar175_summary,
)

class TestConstants:
    def test_um_beta_length(self): assert len(UM_BETA_CANONICAL_DEG) == 2
    def test_um_beta_low(self): assert UM_BETA_CANONICAL_DEG[0] == pytest.approx(0.273, rel=1e-3)
    def test_um_beta_high(self): assert UM_BETA_CANONICAL_DEG[1] == pytest.approx(0.331, rel=1e-3)
    def test_admissible_window(self): assert UM_ADMISSIBLE_MIN_DEG == 0.22 and UM_ADMISSIBLE_MAX_DEG == 0.38
    def test_litebird_year(self): assert LITEBIRD_LAUNCH_YEAR == 2032
    def test_e8_dim(self): assert E8_DIM == 248
    def test_k_e8(self): assert K_E8 == 60
    def test_canonical_in_window(self):
        for b in UM_BETA_CANONICAL_DEG: assert UM_ADMISSIBLE_MIN_DEG <= b <= UM_ADMISSIBLE_MAX_DEG

class TestUmBirefringenceAngles:
    def test_length(self): assert len(um_birefringence_angles_deg()) == 2
    def test_low_value(self): assert um_birefringence_angles_deg()[0] == pytest.approx(0.273, rel=1e-3)
    def test_all_positive(self):
        for b in um_birefringence_angles_deg(): assert b > 0

class TestE8ChernSimonsLevel:
    def test_returns_60(self): assert e8_chern_simons_level() == 60

class TestE8BirefringenceEstimate:
    def test_positive(self): assert e8_birefringence_estimate_deg() > 0
    def test_formula(self):
        avg = (0.273+0.331)/2
        expected = (60/74)*avg*(248/240.0)
        assert e8_birefringence_estimate_deg() == pytest.approx(expected, rel=1e-6)

class TestLitebirdDiscriminability:
    def setup_method(self): self.r = litebird_discriminability()
    def test_can_discriminate_true(self): assert self.r["can_discriminate"] is True
    def test_year_2032(self): assert self.r["year"] == 2032
    def test_gap_positive(self): assert self.r["gap_deg"] >= 0
    def test_verdict_litebird(self): assert "LiteBIRD" in self.r["verdict"]

class TestAudit:
    def setup_method(self): self.r = e8_birefringence_audit()
    def test_status_discriminator(self): assert self.r["status"] == "DISCRIMINATOR"
    def test_implication_present(self): assert len(self.r["implication"]) > 20

class TestPillar175Summary:
    def test_returns_string(self): assert isinstance(pillar175_summary(), str)
    def test_contains_175(self): assert "175" in pillar175_summary()
    def test_contains_status(self): assert "DISCRIMINATOR" in pillar175_summary()
