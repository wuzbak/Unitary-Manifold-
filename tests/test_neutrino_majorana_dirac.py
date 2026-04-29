# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_majorana_dirac.py
========================================
Tests for Pillar 86 — PMNS CP Phase (Corrected) + Majorana/Dirac Mechanism
(src/core/neutrino_majorana_dirac.py).

All tests verify:
  - The corrected geometric PMNS CP phase prediction is −108°
  - The prediction is within 0.1σ of PDG −107° (sigma deviation < 0.1)
  - The CKM phase prediction is +72° (consistent with Pillar 82)
  - The Pillar 83 error (sign convention) is documented and corrected
  - Brane-localised Majorana masses are Z₂-odd (FORBIDDEN at fixed planes)
  - Bulk Majorana masses are Z₂-even (ALLOWED in bulk)
  - The minimal UM predicts Dirac neutrinos
  - The pillar 86 summary runs and is self-consistent

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.neutrino_majorana_dirac import (
    N_W_CANONICAL,
    DELTA_CKM_DEG,
    DELTA_COMPLEMENT_DEG,
    DELTA_CP_PMNS_CORRECTED_DEG,
    DELTA_CP_PMNS_CORRECTED_RAD,
    DELTA_CP_PMNS_PDG_DEG,
    SIGMA_DELTA_CP_PMNS_PDG_DEG,
    DELTA_CP_CKM_DEG,
    DELTA_CP_CKM_PDG_DEG,
    pmns_cp_phase_geometric_corrected,
    z2_majorana_mass_analysis,
    neutrino_mass_type_prediction,
    pmns_cp_phase_comparison,
    pillar86_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_delta_ckm_deg(self):
        # CKM phase = 360/5 = 72°
        assert abs(DELTA_CKM_DEG - 72.0) < 1e-10

    def test_delta_complement_deg(self):
        # Complement = 180° − 72° = 108°
        assert abs(DELTA_COMPLEMENT_DEG - 108.0) < 1e-10

    def test_corrected_pmns_phase_deg(self):
        # Corrected PMNS: −108°
        assert abs(DELTA_CP_PMNS_CORRECTED_DEG - (-108.0)) < 1e-10

    def test_corrected_pmns_phase_rad(self):
        assert abs(DELTA_CP_PMNS_CORRECTED_RAD - math.radians(-108.0)) < 1e-10

    def test_pdg_pmns_phase_deg(self):
        assert abs(DELTA_CP_PMNS_PDG_DEG - (-107.0)) < 0.1

    def test_sigma_pdg_positive(self):
        assert SIGMA_DELTA_CP_PMNS_PDG_DEG > 0.0

    def test_delta_ckm_pdg(self):
        # CKM PDG best fit ~68.5°
        assert 60.0 < DELTA_CP_CKM_PDG_DEG < 80.0


# ---------------------------------------------------------------------------
# Corrected PMNS CP phase
# ---------------------------------------------------------------------------

class TestPmnsCpPhaseGeometricCorrected:
    def test_n_w_5_returns_minus_108(self):
        r = pmns_cp_phase_geometric_corrected(n_w=5)
        assert abs(r["delta_pmns_corrected_deg"] - (-108.0)) < 1e-10

    def test_ckm_phase_72(self):
        r = pmns_cp_phase_geometric_corrected(n_w=5)
        assert abs(r["delta_ckm_deg"] - 72.0) < 1e-10

    def test_complement_108(self):
        r = pmns_cp_phase_geometric_corrected(n_w=5)
        assert abs(r["delta_complement_deg"] - 108.0) < 1e-10

    def test_pdg_value_stored(self):
        r = pmns_cp_phase_geometric_corrected(n_w=5)
        assert abs(r["delta_pmns_pdg_deg"] - (-107.0)) < 0.1

    def test_discrepancy_is_1_degree(self):
        r = pmns_cp_phase_geometric_corrected(n_w=5)
        # |−108 − (−107)| = 1°
        assert abs(r["discrepancy_deg"] - 1.0) < 0.1

    def test_sigma_deviation_less_than_0_1(self):
        r = pmns_cp_phase_geometric_corrected(n_w=5)
        assert r["sigma_deviation"] < 0.1

    def test_status_consistent(self):
        r = pmns_cp_phase_geometric_corrected(n_w=5)
        # Should be "CONSISTENT" (within 0.1σ)
        assert "CONSISTENT" in r["status"]

    def test_sign_origin_documented(self):
        r = pmns_cp_phase_geometric_corrected(n_w=5)
        assert "dagger" in r["sign_origin"].lower() or "†" in r["sign_origin"]

    def test_n_w_7_gives_different_phase(self):
        r5 = pmns_cp_phase_geometric_corrected(n_w=5)
        r7 = pmns_cp_phase_geometric_corrected(n_w=7)
        assert r5["delta_pmns_corrected_deg"] != r7["delta_pmns_corrected_deg"]

    def test_n_w_7_complement(self):
        r = pmns_cp_phase_geometric_corrected(n_w=7)
        # For n_w=7: δ_ckm = 360/7 ≈ 51.43°, complement = 180-51.43 = 128.57°
        expected_ckm = 360.0 / 7.0
        expected_complement = 180.0 - expected_ckm
        assert abs(r["delta_ckm_deg"] - expected_ckm) < 1e-8
        assert abs(r["delta_complement_deg"] - expected_complement) < 1e-8

    def test_invalid_n_w_raises(self):
        with pytest.raises(ValueError):
            pmns_cp_phase_geometric_corrected(n_w=3)


# ---------------------------------------------------------------------------
# Z₂ Majorana mass analysis
# ---------------------------------------------------------------------------

class TestZ2MajoranaMassAnalysis:
    def setup_method(self):
        self.r = z2_majorana_mass_analysis()

    def test_brane_majorana_z2_parity_odd(self):
        assert self.r["brane_majorana_mass"]["z2_parity"] == "ODD"

    def test_brane_majorana_not_allowed(self):
        assert self.r["brane_majorana_mass"]["allowed_at_fixed_planes"] is False

    def test_bulk_majorana_z2_parity_even(self):
        assert self.r["bulk_majorana_mass"]["z2_parity"] == "EVEN"

    def test_bulk_majorana_allowed(self):
        assert self.r["bulk_majorana_mass"]["allowed_in_bulk"] is True

    def test_minimal_um_prediction_dirac(self):
        assert self.r["prediction_minimal_um"]["neutrino_type"] == "DIRAC"

    def test_brane_term_documented(self):
        assert "ν_R^T C ν_R" in self.r["brane_majorana_mass"]["term"]

    def test_z2_action_documented(self):
        assert "Z₂-odd" in self.r["z2_action_on_rh_neutrino"]

    def test_honest_status_present(self):
        assert "honest_status" in self.r
        assert "DERIVED" in self.r["honest_status"]
        assert "OPEN" in self.r["honest_status"]

    def test_0vbb_test_mentioned(self):
        obs_test = self.r["prediction_minimal_um"]["observable_test"]
        assert "0νββ" in obs_test or "double beta" in obs_test.lower()


# ---------------------------------------------------------------------------
# Neutrino mass type prediction
# ---------------------------------------------------------------------------

class TestNeutrinoMassTypePrediction:
    def setup_method(self):
        self.r = neutrino_mass_type_prediction()

    def test_predicted_type_dirac(self):
        assert self.r["predicted_type_minimal_um"] == "DIRAC"

    def test_brane_majorana_forbidden(self):
        assert self.r["brane_majorana_forbidden"] is True

    def test_bulk_majorana_allowed(self):
        assert self.r["bulk_majorana_allowed"] is True

    def test_effective_majorana_mass_zero_minimal(self):
        assert self.r["effective_majorana_mass_minimal"] == 0.0

    def test_0vbb_prediction_minimal_absent(self):
        assert "ABSENT" in self.r["0vbb_prediction_minimal"].upper()

    def test_falsification_present(self):
        assert "falsification" in self.r

    def test_test_experiment_mentioned(self):
        exp = self.r["falsification"]["test"]
        assert "KamLAND" in exp or "LEGEND" in exp or "double beta" in exp.lower()


# ---------------------------------------------------------------------------
# PMNS CP phase comparison
# ---------------------------------------------------------------------------

class TestPmnsCpPhaseComparison:
    def test_returns_dict(self):
        r = pmns_cp_phase_comparison()
        assert isinstance(r, dict)

    def test_predicted_minus_108(self):
        r = pmns_cp_phase_comparison()
        assert abs(r["delta_pmns_predicted_deg"] - (-108.0)) < 1e-10

    def test_pdg_minus_107(self):
        r = pmns_cp_phase_comparison()
        assert abs(r["delta_pmns_pdg_deg"] - (-107.0)) < 0.1

    def test_discrepancy_1_degree(self):
        r = pmns_cp_phase_comparison()
        assert abs(r["discrepancy_deg"] - 1.0) < 0.1

    def test_consistent_at_1sigma(self):
        r = pmns_cp_phase_comparison()
        assert r["consistent_at_1sigma"] is True

    def test_consistent_at_2sigma(self):
        r = pmns_cp_phase_comparison()
        assert r["consistent_at_2sigma"] is True

    def test_sigma_deviation_small(self):
        r = pmns_cp_phase_comparison()
        assert r["sigma_deviation"] < 0.1


# ---------------------------------------------------------------------------
# Pillar 86 summary
# ---------------------------------------------------------------------------

class TestPillar86Summary:
    def setup_method(self):
        self.r = pillar86_summary()

    def test_pillar_number(self):
        assert self.r["pillar"] == 86

    def test_cp_phase_present(self):
        assert "pmns_cp_phase" in self.r

    def test_comparison_present(self):
        assert "cp_phase_comparison" in self.r

    def test_majorana_analysis_present(self):
        assert "majorana_dirac_analysis" in self.r

    def test_neutrino_type_present(self):
        assert "neutrino_type_prediction" in self.r

    def test_corrections_from_pillar_83_present(self):
        c = self.r["corrections_from_pillar_83"]
        assert "pillar_83_reported" in c
        assert "correct_result" in c

    def test_correction_says_minus_108(self):
        c = self.r["corrections_from_pillar_83"]["correct_result"]
        assert "−108°" in c or "-108" in c

    def test_honest_status_corrected(self):
        hs = self.r["honest_status"]
        assert "CORRECTED" in hs
        assert "DERIVED" in hs
        assert "OPEN" in hs

    def test_gap_closed_in_status(self):
        assert "CLOSED" in self.r["honest_status"]["CORRECTED"].upper()
