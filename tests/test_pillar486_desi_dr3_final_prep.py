# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 486 — DESI DR3 Final Preparation and GATEKEEPER Sync."""
from __future__ import annotations

import math

from src.core.pillar486_desi_dr3_final_prep import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    UM_PREDICTION,
    DESI_DR2_CPL_CORRECTED,
    DR2_SIGMA_1D_CORRECTED,
    DESI_DR3_EXPECTED_SIGMA_WA,
    compute_1d_tension,
    compute_2d_tension_approx,
    apply_decision_protocol,
    dr3_tripwire,
    desi_dr3_one_page_statement,
    sha256_preregistration_486,
    gatekeeper_sync_note,
    dr2_status_corrected,
    dr3_projection,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'DESI_DR3_FINAL_PREPARATION_COMPLETE'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 486

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_um_prediction(self):
        assert UM_PREDICTION['w0'] == -1.0
        assert UM_PREDICTION['wa'] == 0.0

    def test_dr2_corrected_sigma(self):
        # Pillar 428 CPL-corrected value
        assert abs(DR2_SIGMA_1D_CORRECTED - 2.30) < 0.05

    def test_desi_dr3_expected_smaller_error(self):
        assert DESI_DR3_EXPECTED_SIGMA_WA < DESI_DR2_CPL_CORRECTED['wa_err']

    def test_dr2_has_required_fields(self):
        for field in ['w0', 'w0_err', 'wa', 'wa_err', 'rho_w0_wa', 'source']:
            assert field in DESI_DR2_CPL_CORRECTED


class TestCompute1DTension:
    def test_zero_wa_is_zero(self):
        assert compute_1d_tension(0.0, 1.0) == 0.0

    def test_um_prediction_wa_is_zero(self):
        # wₐ = 0 is the UM prediction; tension from nonzero measured value
        result = compute_1d_tension(-0.75, 0.30)
        assert abs(result - 2.5) < 0.01

    def test_positive(self):
        assert compute_1d_tension(-0.62, 0.30) > 0

    def test_invalid_error_raises(self):
        import pytest
        with pytest.raises(ValueError):
            compute_1d_tension(-0.5, 0.0)

    def test_larger_wa_larger_tension(self):
        t1 = compute_1d_tension(-0.5, 0.30)
        t2 = compute_1d_tension(-1.0, 0.30)
        assert t2 > t1


class TestCompute2DTensionApprox:
    def test_positive(self):
        result = compute_2d_tension_approx(
            -0.827, 0.072, -0.75, 0.30, -0.97
        )
        assert result > 0

    def test_perfect_match_is_zero(self):
        result = compute_2d_tension_approx(
            UM_PREDICTION['w0'], 0.1, UM_PREDICTION['wa'], 0.1, 0.0
        )
        assert result < 0.001

    def test_invalid_error_raises(self):
        import pytest
        with pytest.raises(ValueError):
            compute_2d_tension_approx(
                -0.9, -0.1, -0.5, 0.3, 0.0
            )

    def test_invalid_rho_raises(self):
        import pytest
        with pytest.raises(ValueError):
            compute_2d_tension_approx(
                -0.9, 0.1, -0.5, 0.3, 1.0
            )


class TestApplyDecisionProtocol:
    def test_falsified_at_3sigma(self):
        assert apply_decision_protocol(3.1, 3.5) == 'FALSIFIED'

    def test_confirmed_below_2sigma(self):
        assert apply_decision_protocol(1.5, 1.8) == 'CONFIRMED'

    def test_inconclusive_between(self):
        assert apply_decision_protocol(2.5, 2.5) == 'INCONCLUSIVE'

    def test_need_both_for_falsified(self):
        # Only 1D ≥ 3σ is not enough
        assert apply_decision_protocol(3.5, 2.5) != 'FALSIFIED'

    def test_need_both_below_2_for_confirmed(self):
        assert apply_decision_protocol(2.5, 1.0) != 'CONFIRMED'

    def test_exact_threshold_falsified(self):
        assert apply_decision_protocol(3.0, 3.0) == 'FALSIFIED'

    def test_exact_threshold_confirmed(self):
        assert apply_decision_protocol(1.99, 1.99) == 'CONFIRMED'


class TestDR3Tripwire:
    def test_returns_dict(self):
        result = dr3_tripwire(-0.75, 0.18)
        assert isinstance(result, dict)

    def test_has_verdict(self):
        result = dr3_tripwire(-0.75, 0.18)
        assert 'verdict' in result
        assert result['verdict'] in ('FALSIFIED', 'CONFIRMED', 'INCONCLUSIVE')

    def test_has_sigma_fields(self):
        result = dr3_tripwire(-0.75, 0.18)
        assert 'sigma_1d' in result
        assert 'sigma_2d' in result

    def test_falsified_with_small_error(self):
        # With σ_wₐ = 0.10 and central = -0.75, should be well above 3σ
        result = dr3_tripwire(-0.75, 0.10)
        assert result['verdict'] == 'FALSIFIED'

    def test_confirmed_if_wa_near_zero(self):
        # If DR3 (w0, wa) both near UM prediction (-1, 0), should be confirmed
        result = dr3_tripwire(-0.02, 0.30, w0_dr3=-1.0, w0_err_dr3=0.1, rho_dr3=0.0)
        assert result['verdict'] == 'CONFIRMED'

    def test_has_preregistration_note(self):
        result = dr3_tripwire(-0.75, 0.18)
        assert 'note' in result
        assert 'pre-registered' in result['note'].lower() or 'Pre-registered' in result['note']

    def test_has_um_prediction(self):
        result = dr3_tripwire(-0.75, 0.18)
        assert 'um_prediction' in result

    def test_falsified_bool_consistent_with_verdict(self):
        result = dr3_tripwire(-0.75, 0.18)
        assert result['falsified'] == (result['verdict'] == 'FALSIFIED')


class TestDesIDR3OnePagerStatement:
    def setup_method(self):
        self.statement = desi_dr3_one_page_statement()

    def test_returns_string(self):
        assert isinstance(self.statement, str)

    def test_has_prediction(self):
        assert 'w₀ = -1' in self.statement or 'w0 = -1' in self.statement.lower()
        assert 'wₐ = 0' in self.statement or 'wa = 0' in self.statement.lower()

    def test_has_decision_rule(self):
        assert 'FALSIFIED' in self.statement
        assert 'CONFIRMED' in self.statement

    def test_has_tripwire_code(self):
        assert 'dr3_tripwire' in self.statement

    def test_has_sha256_reference(self):
        assert 'SHA-256' in self.statement or 'sha256' in self.statement.lower()

    def test_mentions_3sigma_threshold(self):
        assert '3.0' in self.statement or '3σ' in self.statement


class TestSHA256Preregistration486:
    def test_returns_string(self):
        h = sha256_preregistration_486()
        assert isinstance(h, str)

    def test_is_hex_64_chars(self):
        h = sha256_preregistration_486()
        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h)

    def test_deterministic(self):
        h1 = sha256_preregistration_486()
        h2 = sha256_preregistration_486()
        assert h1 == h2


class TestGatekeeperSyncNote:
    def setup_method(self):
        self.note = gatekeeper_sync_note()

    def test_returns_dict(self):
        assert isinstance(self.note, dict)

    def test_has_document(self):
        assert 'GATEKEEPER_SUMMARY.md' in self.note['document']

    def test_corrected_tension(self):
        # Must reference the corrected 2.30σ
        assert '2.30' in self.note['new_text']

    def test_pillar_428_cited(self):
        assert 'Pillar 428' in self.note['new_text'] or 'pillar 428' in self.note['new_text'].lower()

    def test_version(self):
        assert 'v14.2' in self.note['version']


class TestDR2StatusCorrected:
    def setup_method(self):
        self.dr2 = dr2_status_corrected()

    def test_returns_dict(self):
        assert isinstance(self.dr2, dict)

    def test_sigma_1d_near_2_30(self):
        assert abs(self.dr2['sigma_1d'] - DR2_SIGMA_1D_CORRECTED) < 0.30

    def test_not_falsified(self):
        assert self.dr2['falsified'] is False

    def test_status_high_tension(self):
        assert self.dr2['status'] == 'HIGH_TENSION'

    def test_has_note(self):
        assert 'note' in self.dr2

    def test_dataset(self):
        assert 'DESI_DR2' in self.dr2['dataset']


class TestDR3Projection:
    def setup_method(self):
        self.proj = dr3_projection()

    def test_returns_dict(self):
        assert isinstance(self.proj, dict)

    def test_sigma_1d_larger_than_dr2(self):
        dr2 = dr2_status_corrected()
        # Smaller error → larger sigma
        assert self.proj['projected_sigma_1d'] > dr2['sigma_1d']

    def test_has_verdict(self):
        assert 'projected_verdict' in self.proj
        assert self.proj['projected_verdict'] in ('FALSIFIED', 'CONFIRMED', 'INCONCLUSIVE')

    def test_dr3_err_smaller(self):
        assert self.proj['dr3_wa_err'] < DESI_DR2_CPL_CORRECTED['wa_err']

    def test_falsification_risk_classified(self):
        assert self.proj['falsification_risk'] in ('HIGH', 'MEDIUM', 'LOW')

    def test_has_note(self):
        assert 'note' in self.proj


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 486

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_has_dr2_corrected(self):
        assert 'dr2_corrected' in self.report

    def test_has_dr3_projection(self):
        assert 'dr3_projection' in self.report

    def test_has_gatekeeper_sync(self):
        assert 'gatekeeper_sync' in self.report

    def test_has_sha256(self):
        assert 'sha256_hash' in self.report
        assert len(self.report['sha256_hash']) == 64

    def test_tripwire_ready(self):
        assert self.report['tripwire_ready'] is True

    def test_has_verdict(self):
        assert 'verdict' in self.report
        assert 'DR2 corrected' in self.report['verdict']
