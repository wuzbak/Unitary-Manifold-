# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 790 — DARK_MATTER_KK_TOWER (50 tests)."""

import math
import pytest
from src.core.pillar790_dark_matter_kk_tower import (
    N_W, K_CS, M_PL_GEV, M_EW_GEV, HBAR_C_GEV_M,
    K_ADS_OVER_MPL, K_R_PI,
    M_KK_TEV_CENTRAL, M_KK_TEV_LOW, M_KK_TEV_HIGH,
    SIGMA_SI_CM2, XENON_NT_LIMIT_CM2_1TEV, XENON_NT_EXCLUSION_TEV,
    OMEGA_DM_H2_PLANCK, OMEGA_DM_H2_ESTIMATE_LOW, OMEGA_DM_H2_ESTIMATE_HIGH,
    PILLAR_STATUS, PILLAR_NUMBER, GATE,
    compactification_radius_m, kk_mass_gev,
    spin_independent_cross_section_cm2, thermal_relic_density,
    is_xenon_nt_excluded, scan_kk_tower,
    compute_dm_kk_certificate, get_dm_kk_dict,
    DM_KK_CERTIFICATE, DarkMatterKKCertificate, KKModeEntry,
    run_pillar790,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 790

    def test_status_string(self):
        assert "DM_KK" in PILLAR_STATUS

    def test_gate_string(self):
        assert "DM_KK" in GATE

    def test_mass_window_ordered(self):
        assert M_KK_TEV_LOW < M_KK_TEV_CENTRAL < M_KK_TEV_HIGH

    def test_xenon_limit_positive(self):
        assert XENON_NT_LIMIT_CM2_1TEV > 0

    def test_sigma_si_positive(self):
        assert SIGMA_SI_CM2 > 0

    def test_omega_range_ordered(self):
        assert OMEGA_DM_H2_ESTIMATE_LOW < OMEGA_DM_H2_ESTIMATE_HIGH

    def test_omega_planck_in_range(self):
        # Planck central value should be broadly consistent
        assert 0.10 <= OMEGA_DM_H2_PLANCK <= 0.13


# ---------------------------------------------------------------------------
# Core physics functions
# ---------------------------------------------------------------------------
class TestPhysicsFunctions:
    def test_compactification_radius_positive(self):
        r5 = compactification_radius_m()
        assert r5 > 0

    def test_compactification_radius_small(self):
        r5 = compactification_radius_m()
        assert r5 < 1e-20  # sub-nuclear scale

    def test_k_r_pi_positive(self):
        assert K_R_PI > 0

    def test_k_r_pi_value(self):
        assert 30 < K_R_PI < 45  # log(M_Pl/M_EW) ≈ 11.3

    def test_kk_mass_n1_positive(self):
        assert kk_mass_gev(1) > 0

    def test_kk_mass_n2_greater_n1(self):
        assert kk_mass_gev(2) > kk_mass_gev(1)

    def test_kk_mass_scaling(self):
        # M_n ∝ n
        assert abs(kk_mass_gev(2) / kk_mass_gev(1) - 2.0) < 0.01

    def test_spin_independent_cs_positive(self):
        sigma = spin_independent_cross_section_cm2(1.0)
        assert sigma > 0

    def test_spin_independent_cs_small(self):
        sigma = spin_independent_cross_section_cm2(1.0)
        assert sigma == pytest.approx(3.42659256e-42)

    def test_thermal_relic_positive(self):
        omega = thermal_relic_density(1.0)
        assert omega > 0

    def test_xenon_exclusion_low_mass(self):
        assert is_xenon_nt_excluded(0.1, 0.0) is None

    def test_supplied_benchmark_above_reference(self):
        excluded = is_xenon_nt_excluded(M_KK_TEV_CENTRAL)
        assert excluded is True

    def test_mass_ansatz_actual_value(self):
        assert kk_mass_gev(1) == pytest.approx(K_ADS_OVER_MPL * M_EW_GEV)
        assert kk_mass_gev(1) == pytest.approx(24.622)

    def test_relic_unit_conversion(self):
        sigma_tev2 = K_ADS_OVER_MPL ** 4 / (16 * math.pi)
        expected = 0.1 / (sigma_tev2 * 389.4)
        assert thermal_relic_density(1.0) == pytest.approx(expected)
        assert thermal_relic_density(1.0) == pytest.approx(129.084443907)

    def test_scattering_and_relic_mass_scaling(self):
        assert spin_independent_cross_section_cm2(2.0) == pytest.approx(
            spin_independent_cross_section_cm2(1.0) / 16, abs=0
        )
        assert thermal_relic_density(2.0) == pytest.approx(
            4 * thermal_relic_density(1.0)
        )

    def test_explicit_limit_no_mass_only_exclusion(self):
        assert is_xenon_nt_excluded(0.1, 0.0, limit_cm2=1e-47) is False
        assert is_xenon_nt_excluded(0.1, 2e-47, limit_cm2=1e-47) is True
        assert is_xenon_nt_excluded(1.0, 0.0) is False

    @pytest.mark.parametrize("mass", [0, -1, float("nan"), float("inf")])
    def test_invalid_mass_rejected(self, mass):
        for function in (spin_independent_cross_section_cm2,
                         thermal_relic_density, is_xenon_nt_excluded):
            with pytest.raises(ValueError):
                function(mass)

    @pytest.mark.parametrize("limit", [0, -1, float("nan"), float("inf")])
    def test_invalid_limit_rejected(self, limit):
        with pytest.raises(ValueError):
            is_xenon_nt_excluded(1.0, limit_cm2=limit)


# ---------------------------------------------------------------------------
# KK Tower scan
# ---------------------------------------------------------------------------
class TestKKTower:
    def setup_method(self):
        self.tower = scan_kk_tower(5)

    def test_tower_length(self):
        assert len(self.tower) == 5

    def test_tower_mode_indices(self):
        for i, entry in enumerate(self.tower, 1):
            assert entry.mode_n == i

    def test_tower_masses_increasing(self):
        masses = [e.mass_tev for e in self.tower]
        for i in range(len(masses) - 1):
            assert masses[i] < masses[i + 1]

    def test_tower_masses_positive(self):
        for entry in self.tower:
            assert entry.mass_tev > 0

    def test_tower_entry_type(self):
        assert isinstance(self.tower[0], KKModeEntry)

    def test_n1_mode_mass_gev_range(self):
        m_tev = self.tower[0].mass_tev
        assert 0.01 < m_tev < 100  # broad sanity check


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------
class TestDMKKCertificate:
    def setup_method(self):
        self.cert = compute_dm_kk_certificate()

    def test_cert_type(self):
        assert isinstance(self.cert, DarkMatterKKCertificate)

    def test_pillar_number(self):
        assert self.cert.pillar == 790

    def test_status(self):
        assert self.cert.status == PILLAR_STATUS

    def test_gate(self):
        assert self.cert.gate == GATE

    def test_r5_metres_positive(self):
        assert self.cert.r5_metres > 0

    def test_m_kk_central(self):
        assert self.cert.m_kk_tev_central == pytest.approx(kk_mass_gev() / 1000)
        assert self.cert.supplied_benchmark_mass_tev == 1.0

    def test_below_xenon_limit(self):
        assert self.cert.below_xenon_limit is None
        assert self.cert.is_excluded_central is None
        assert self.cert.xenon_nt_limit_cm2 is None
        assert self.cert.xenon_nt_exclusion_below_tev is None

    def test_kk_tower_nonempty(self):
        assert len(self.cert.kk_tower) > 0

    def test_architecture_limit_set(self):
        assert len(self.cert.architecture_limit) > 20

    def test_falsification_condition_set(self):
        assert len(self.cert.falsification_condition) > 20

    def test_pre_registered_experiments_nonempty(self):
        assert len(self.cert.pre_registered_experiments) >= 2

    def test_xenon_mentioned(self):
        exps = " ".join(self.cert.pre_registered_experiments)
        assert "XENON" in exps or "xenon" in exps.lower()

    def test_zero_failures(self):
        assert self.cert.failures == 0

    def test_omega_range_low(self):
        assert self.cert.omega_h2_estimate_low is None

    def test_omega_range_high(self):
        assert self.cert.omega_h2_estimate_high is None

    def test_certificate_matches_actual_functions_and_first_mode(self):
        mass = self.cert.m_kk_tev_central
        assert self.cert.sigma_si_cm2_central == pytest.approx(
            spin_independent_cross_section_cm2(mass), abs=0
        )
        assert self.cert.omega_h2_central == pytest.approx(thermal_relic_density(mass))
        assert self.cert.omega_h2_central == pytest.approx(0.078256525554)
        assert self.cert.relic_consistent is False
        first = self.cert.kk_tower[0]
        assert first.mass_tev == mass
        assert first.omega_h2 == self.cert.omega_h2_central
        assert first.sigma_si_cm2 == self.cert.sigma_si_cm2_central
        assert first.xenon_excluded is None
        assert first.relic_consistent is False

    def test_no_derived_mass_uncertainty(self):
        assert self.cert.m_kk_tev_low is None
        assert self.cert.m_kk_tev_high is None

    def test_run_pillar790_returns_cert(self):
        cert = run_pillar790()
        assert isinstance(cert, DarkMatterKKCertificate)
        assert cert.pillar == 790


# ---------------------------------------------------------------------------
# DM_KK_CERTIFICATE dict
# ---------------------------------------------------------------------------
class TestDMKKDict:
    def test_keys_present(self):
        required = ["pillar", "status", "gate", "m_kk_tev_central",
                    "m_kk_tev_window", "sigma_si_cm2_central",
                    "omega_h2_range", "falsification_condition"]
        for k in required:
            assert k in DM_KK_CERTIFICATE

    def test_pillar_key(self):
        assert DM_KK_CERTIFICATE["pillar"] == 790

    def test_mass_window_two_elements(self):
        assert len(DM_KK_CERTIFICATE["m_kk_tev_window"]) == 2

    def test_get_dm_kk_dict_deterministic(self):
        d1 = get_dm_kk_dict()
        d2 = get_dm_kk_dict()
        assert d1["m_kk_tev_central"] == d2["m_kk_tev_central"]
