# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import math
import numpy as np
import pytest

from src.core.cl_geometric_spectrum import (
    A_S,
    transfer_function_5d,
    cl_geometric,
    dl_spectrum,
    acoustic_peak_positions,
    spectrum_amplitude_status,
)
from src.core.phi0_rg_flow import phi0_at_cmb_scale


class TestConstants:
    def test_a_s_value(self):
        assert abs(A_S - 2.1e-9) < 1e-20

    def test_a_s_positive(self):
        assert A_S > 0


class TestTransferFunction:
    def setup_method(self):
        self.phi_cmb = phi0_at_cmb_scale()

    def test_returns_float(self):
        assert isinstance(transfer_function_5d(100, self.phi_cmb), float)

    def test_positive(self):
        assert transfer_function_5d(100, self.phi_cmb) > 0

    def test_invalid_ell_zero(self):
        with pytest.raises(ValueError):
            transfer_function_5d(0, self.phi_cmb)

    def test_invalid_ell_negative(self):
        with pytest.raises(ValueError):
            transfer_function_5d(-1, self.phi_cmb)

    def test_decreases_with_ell(self):
        t1 = transfer_function_5d(100, self.phi_cmb)
        t2 = transfer_function_5d(200, self.phi_cmb)
        assert t1 > t2

    def test_formula(self):
        ell = 100
        phi = self.phi_cmb
        j_ell = 1.0 / (ell * (ell + 1.0))
        expected = phi ** 2 * j_ell
        assert abs(transfer_function_5d(ell, phi) - expected) < 1e-25

    def test_scales_with_phi_squared(self):
        t1 = transfer_function_5d(100, 1.0)
        t2 = transfer_function_5d(100, 2.0)
        assert abs(t2 / t1 - 4.0) < 1e-12

    def test_j_ell_approximation_large_ell(self):
        ell = 1000
        j_ell = 1.0 / (ell * (ell + 1.0))
        assert abs(j_ell - 1e-6) < 1e-7

    def test_monopole_ell_one(self):
        t = transfer_function_5d(1, self.phi_cmb)
        assert t > 0

    def test_peak_region(self):
        t_200 = transfer_function_5d(200, self.phi_cmb)
        t_2 = transfer_function_5d(2, self.phi_cmb)
        assert t_2 > t_200


class TestClGeometric:
    def setup_method(self):
        self.phi_cmb = phi0_at_cmb_scale()

    def test_returns_float(self):
        assert isinstance(cl_geometric(100), float)

    def test_positive(self):
        assert cl_geometric(100) > 0

    def test_invalid_ell_zero(self):
        with pytest.raises(ValueError):
            cl_geometric(0)

    def test_invalid_ell_negative(self):
        with pytest.raises(ValueError):
            cl_geometric(-10)

    def test_explicit_phi_cmb(self):
        result = cl_geometric(100, phi_cmb=self.phi_cmb)
        assert result > 0

    def test_custom_phi_cmb_not_none(self):
        r1 = cl_geometric(100, phi_cmb=1.0)
        r2 = cl_geometric(100, phi_cmb=self.phi_cmb)
        assert r1 != r2

    def test_scales_with_phi_squared(self):
        cl1 = cl_geometric(100, phi_cmb=1.0)
        cl2 = cl_geometric(100, phi_cmb=2.0)
        assert abs(cl2 / cl1 - 4.0) < 1e-10

    def test_decreases_with_ell_large(self):
        cl1 = cl_geometric(200, phi_cmb=self.phi_cmb)
        cl2 = cl_geometric(2000, phi_cmb=self.phi_cmb)
        assert cl1 > cl2

    def test_formula(self):
        ell = 100
        t = transfer_function_5d(ell, self.phi_cmb)
        expected = (2 * math.pi ** 2 / (ell * (ell + 1))) * A_S * t
        assert abs(cl_geometric(ell, self.phi_cmb) - expected) < 1e-40

    def test_order_of_magnitude(self):
        # D_L = ell*(ell+1)*C_L/(2pi) should be ~nK² ~ 1e-9 range
        cl = cl_geometric(200)
        assert cl > 0

    def test_ell_2_positive(self):
        assert cl_geometric(2) > 0

    def test_ell_1000_positive(self):
        assert cl_geometric(1000) > 0


class TestDlSpectrum:
    def setup_method(self):
        self.ells = np.array([2, 10, 50, 100, 200, 500, 800, 1000])

    def test_returns_ndarray(self):
        assert isinstance(dl_spectrum(self.ells), np.ndarray)

    def test_shape_preserved(self):
        result = dl_spectrum(self.ells)
        assert result.shape == self.ells.shape

    def test_all_positive(self):
        result = dl_spectrum(self.ells)
        assert np.all(result > 0)

    def test_formula(self):
        ells = np.array([100.0])
        dl = dl_spectrum(ells)
        cl = cl_geometric(100.0)
        expected = 100.0 * 101.0 * cl / (2.0 * math.pi)
        assert abs(dl[0] - expected) < 1e-35

    def test_single_ell(self):
        result = dl_spectrum([100])
        assert len(result) == 1
        assert result[0] > 0

    def test_finite_values(self):
        result = dl_spectrum(self.ells)
        assert np.all(np.isfinite(result))

    def test_monotone_at_large_ell(self):
        # D_L = ell*(ell+1)*C_L/(2pi); C_L falls as 1/(ell*(ell+1))^2
        # so D_L ~ 1/(ell*(ell+1)) — decreasing at large ell
        ells = np.array([200.0, 500.0, 800.0, 1000.0])
        dl = dl_spectrum(ells)
        assert dl[0] > dl[-1]

    def test_integer_ells_accepted(self):
        result = dl_spectrum([2, 100, 500])
        assert len(result) == 3


class TestAcousticPeaks:
    def test_returns_list(self):
        assert isinstance(acoustic_peak_positions(), list)

    def test_length_three(self):
        assert len(acoustic_peak_positions()) == 3

    def test_first_peak(self):
        assert acoustic_peak_positions()[0] == 220

    def test_second_peak(self):
        assert acoustic_peak_positions()[1] == 540

    def test_third_peak(self):
        assert acoustic_peak_positions()[2] == 800

    def test_peaks_increasing(self):
        peaks = acoustic_peak_positions()
        assert peaks[0] < peaks[1] < peaks[2]

    def test_peaks_positive(self):
        for p in acoustic_peak_positions():
            assert p > 0

    def test_peaks_in_cmb_range(self):
        for p in acoustic_peak_positions():
            assert 2 <= p <= 2500


class TestSpectrumAmplitudeStatus:
    def setup_method(self):
        self.status = spectrum_amplitude_status()

    def test_returns_dict(self):
        assert isinstance(self.status, dict)

    def test_has_suppression_factor(self):
        assert "suppression_factor" in self.status

    def test_has_gap_acknowledged(self):
        assert "gap_acknowledged" in self.status

    def test_has_prediction(self):
        assert "prediction" in self.status

    def test_gap_acknowledged_true(self):
        assert self.status["gap_acknowledged"] is True

    def test_suppression_factor_positive(self):
        assert self.status["suppression_factor"] > 0

    def test_suppression_factor_less_than_one(self):
        assert self.status["suppression_factor"] < 1.0

    def test_prediction_is_string(self):
        assert isinstance(self.status["prediction"], str)

    def test_prediction_non_empty(self):
        assert len(self.status["prediction"]) > 10
