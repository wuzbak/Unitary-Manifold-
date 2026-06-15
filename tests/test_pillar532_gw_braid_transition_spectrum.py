# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 532 — GW Braid Transition Spectrum."""

from __future__ import annotations
import math
import pytest
from src.core.gw_braid_transition_spectrum import (
    F_PEAK_HZ, K_CS, LISA_BAND_HZ, N_B_SPECTRAL, N_W, OMEGA_GW_PEAK,
    PILLAR_NUMBER, PILLAR_STATUS, PILLAR_TITLE, PTA_BAND_HZ,
    detector_accessibility, gw_braid_omega_at_frequency, gw_braid_omega_peak,
    gw_braid_peak_frequency, gw_braid_spectral_index, pillar532_report,
)


class TestPillarMetadata:
    def test_pillar_number(self): assert PILLAR_NUMBER == 532
    def test_status(self): assert PILLAR_STATUS == "GW_BRAID_SPECTRUM_CERTIFIED"
    def test_k_cs(self): assert K_CS == 74
    def test_n_w(self): assert N_W == 5


class TestGWBraidSpectrum:
    def test_spectral_index(self): assert abs(gw_braid_spectral_index() - N_W/K_CS) < 1e-10
    def test_spectral_index_positive(self): assert N_B_SPECTRAL > 0
    def test_peak_frequency_positive(self): assert gw_braid_peak_frequency() > 0
    def test_peak_frequency_large(self): assert F_PEAK_HZ > 1e10
    def test_omega_peak_positive(self): assert gw_braid_omega_peak() > 0
    def test_omega_peak_small(self): assert OMEGA_GW_PEAK < 1e-6
    def test_omega_at_peak(self):
        omega = gw_braid_omega_at_frequency(F_PEAK_HZ)
        assert abs(omega - OMEGA_GW_PEAK) < 1e-20
    def test_omega_zero_for_zero_freq(self): assert gw_braid_omega_at_frequency(0.0) == 0.0
    def test_omega_decreases_above_peak(self):
        omega_at = gw_braid_omega_at_frequency(F_PEAK_HZ * 10)
        assert omega_at < OMEGA_GW_PEAK
    def test_omega_decreases_below_peak(self):
        omega_at = gw_braid_omega_at_frequency(F_PEAK_HZ / 10)
        assert omega_at < OMEGA_GW_PEAK


class TestDetectorAccessibility:
    def setup_method(self): self.v = detector_accessibility()
    def test_returns_dict(self): assert isinstance(self.v, dict)
    def test_lisa_not_accessible(self): assert self.v["lisa_accessible"] is False
    def test_pta_not_accessible(self): assert self.v["pta_accessible"] is False
    def test_verdict_outside_bands(self): assert "OUTSIDE" in self.v["verdict"]


class TestPillar532Report:
    def setup_method(self): self.r = pillar532_report()
    def test_returns_dict(self): assert isinstance(self.r, dict)
    def test_pillar_number(self): assert self.r["pillar"] == 532
    def test_status(self): assert self.r["status"] == "GW_BRAID_SPECTRUM_CERTIFIED"
    def test_spectrum_section(self):
        s = self.r["spectrum"]
        assert "f_peak_hz" in s and "omega_gw_peak" in s
    def test_detector_accessibility_outside(self):
        assert "OUTSIDE" in self.r["detector_accessibility"]["verdict"]
