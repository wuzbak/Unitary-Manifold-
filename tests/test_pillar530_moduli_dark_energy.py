# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 530 — Moduli-Coupled Dark Energy."""

from __future__ import annotations
import pytest
from src.eleventd.moduli_dark_energy import (
    DESI_TENSION_SIGMA, DESI_WA_PREFERRED, DESI_WA_SIGMA,
    K_CS, N_W, PILLAR_NUMBER, PILLAR_STATUS, PILLAR_TITLE,
    W0_UM, WA_NLO_CORRECTION, WA_UM_LO, WA_UM_NLO,
    dark_energy_eos, desi_tension_verdict, moduli_wa_correction, pillar530_report,
)


class TestPillarMetadata:
    def test_pillar_number(self): assert PILLAR_NUMBER == 530
    def test_status(self): assert PILLAR_STATUS == "MODULI_DARK_ENERGY_CERTIFIED"
    def test_title_mentions_wa(self): assert "w" in PILLAR_TITLE.lower() or "dark" in PILLAR_TITLE.lower()
    def test_k_cs(self): assert K_CS == 74
    def test_n_w(self): assert N_W == 5


class TestConstants:
    def test_w0_is_minus_one(self): assert W0_UM == -1.0
    def test_wa_lo_zero(self): assert WA_UM_LO == 0.0
    def test_wa_nlo_tiny(self): assert abs(WA_UM_NLO) < 0.01
    def test_wa_nlo_close_to_lo(self): assert abs(WA_UM_NLO - WA_UM_LO) < 1e-4
    def test_desi_tension_below_3sigma(self): assert DESI_TENSION_SIGMA < 3.0


class TestModuliWaCorrection:
    def test_negative(self): assert moduli_wa_correction() < 0
    def test_smaller_than_desi_sigma(self): assert abs(moduli_wa_correction()) < DESI_WA_SIGMA
    def test_default_tiny(self): assert abs(moduli_wa_correction()) < 1e-3


class TestDarkEnergyEOS:
    def test_at_a1_equals_w0(self): assert abs(dark_energy_eos(1.0) - W0_UM) < 1e-10
    def test_at_a0(self): assert abs(dark_energy_eos(0.0) - (W0_UM + WA_UM_NLO)) < 1e-10
    def test_custom_params(self):
        w = dark_energy_eos(0.5, -1.0, -0.5)
        assert abs(w - (-1.0 + (-0.5) * 0.5)) < 1e-10


class TestDESITensionVerdict:
    def setup_method(self): self.v = desi_tension_verdict()
    def test_returns_dict(self): assert isinstance(self.v, dict)
    def test_below_threshold(self): assert self.v["below_threshold"] is True
    def test_verdict_low_tension(self): assert "LOW_TENSION" in self.v["verdict"]
    def test_desi_sigma_recorded(self): assert self.v["desi_tension_sigma"] == DESI_TENSION_SIGMA
    def test_threshold_3sigma(self): assert self.v["falsification_threshold_sigma"] == 3.0


class TestPillar530Report:
    def setup_method(self): self.r = pillar530_report()
    def test_returns_dict(self): assert isinstance(self.r, dict)
    def test_pillar_number(self): assert self.r["pillar"] == 530
    def test_status(self): assert self.r["status"] == "MODULI_DARK_ENERGY_CERTIFIED"
    def test_desi_verdict_present(self): assert "desi_verdict" in self.r
    def test_desi_below_threshold(self): assert self.r["desi_verdict"]["below_threshold"] is True
    def test_dark_energy_eos_section(self):
        eos = self.r["dark_energy_eos"]
        assert eos["w0_um"] == -1.0
        assert eos["wa_um_lo"] == 0.0
    def test_summary_mentions_desi(self): assert "DESI" in self.r["summary"]
