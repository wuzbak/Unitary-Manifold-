# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 523 — Architecture limit upgrade certificates.

Status: ARCHITECTURE_LIMIT_UPGRADED (🔵 ADJACENT TRACK)
"""

from __future__ import annotations

import pytest

from src.eleventd.architecture_limit_upgrade import (
    NEW_STATUS_P517,
    NEW_STATUS_P518,
    PRIOR_STATUS_P517,
    PRIOR_STATUS_P518,
    UPGRADE_REGISTRY,
    architecture_limit_upgrade_report,
    p517_upgrade_certificate,
    p518_upgrade_certificate,
)


# ── Module-level constants ─────────────────────────────────────────────────────


class TestModuleConstants:
    def test_prior_status_p517(self):
        assert "ARCHITECTURE_LIMIT" in PRIOR_STATUS_P517

    def test_prior_status_p518(self):
        assert "ARCHITECTURE_LIMIT" in PRIOR_STATUS_P518

    def test_new_status_p517(self):
        assert "CONDITIONAL_DERIVATION" in NEW_STATUS_P517

    def test_new_status_p518(self):
        assert "PARTIAL_CLOSURE" in NEW_STATUS_P518

    def test_upgrade_registry_has_p517(self):
        assert PRIOR_STATUS_P517 in UPGRADE_REGISTRY

    def test_upgrade_registry_has_p518(self):
        assert PRIOR_STATUS_P518 in UPGRADE_REGISTRY

    def test_registry_maps_correctly(self):
        assert UPGRADE_REGISTRY[PRIOR_STATUS_P517] == NEW_STATUS_P517
        assert UPGRADE_REGISTRY[PRIOR_STATUS_P518] == NEW_STATUS_P518


# ── p517_upgrade_certificate ──────────────────────────────────────────────────


class TestP517UpgradeCertificate:
    @pytest.fixture(scope="class")
    def cert(self):
        return p517_upgrade_certificate()

    def test_pillar_upgraded(self, cert):
        assert cert["pillar_upgraded"] == 517

    def test_upgrading_pillar(self, cert):
        assert cert["upgrading_pillar"] == 520

    def test_prior_status(self, cert):
        assert cert["prior_status"] == PRIOR_STATUS_P517

    def test_new_status(self, cert):
        assert cert["new_status"] == NEW_STATUS_P517

    def test_transition_string(self, cert):
        assert PRIOR_STATUS_P517 in cert["transition"]
        assert NEW_STATUS_P517 in cert["transition"]

    def test_p_r_conditional_positive(self, cert):
        assert cert["p_r_conditional"] > 0

    def test_remaining_open_condition_named(self, cert):
        assert "521" in cert["remaining_open_condition"]

    def test_upgrade_is_valid(self, cert):
        assert cert["upgrade_is_valid"] is True

    def test_no_hardgate_score_change(self, cert):
        assert cert["no_hardgate_score_change"] is True

    def test_status(self, cert):
        assert cert["status"] == "ARCHITECTURE_LIMIT_UPGRADED"

    def test_p_r_at_nlo_vol_present(self, cert):
        assert cert["p_r_at_nlo_vol"] > 0

    def test_deterministic(self):
        c1 = p517_upgrade_certificate()
        c2 = p517_upgrade_certificate()
        assert c1["p_r_conditional"] == pytest.approx(c2["p_r_conditional"])


# ── p518_upgrade_certificate ──────────────────────────────────────────────────


class TestP518UpgradeCertificate:
    @pytest.fixture(scope="class")
    def cert(self):
        return p518_upgrade_certificate()

    def test_pillar_upgraded(self, cert):
        assert cert["pillar_upgraded"] == 518

    def test_upgrading_pillar(self, cert):
        assert cert["upgrading_pillar"] == 519

    def test_prior_status(self, cert):
        assert cert["prior_status"] == PRIOR_STATUS_P518

    def test_new_status(self, cert):
        assert cert["new_status"] == NEW_STATUS_P518

    def test_transition_string(self, cert):
        assert PRIOR_STATUS_P518 in cert["transition"]
        assert NEW_STATUS_P518 in cert["transition"]

    def test_zphi_nlo_greater_than_zphi_0(self, cert):
        assert cert["zphi_nlo"] > cert["zphi_0"]

    def test_delta_zphi_g4_positive(self, cert):
        assert cert["delta_zphi_g4"] > 0

    def test_fraction_resolved_positive(self, cert):
        assert cert["fraction_resolved"] > 0

    def test_pct_resolved_positive(self, cert):
        assert cert["pct_resolved"] > 0

    def test_irreducible_floor_label(self, cert):
        assert cert["irreducible_floor_label"] == "5D_IRREDUCIBLE_FLOOR"

    def test_upgrade_is_valid(self, cert):
        assert cert["upgrade_is_valid"] is True

    def test_no_hardgate_score_change(self, cert):
        assert cert["no_hardgate_score_change"] is True

    def test_status(self, cert):
        assert cert["status"] == "ARCHITECTURE_LIMIT_UPGRADED"

    def test_irreducible_floor_interpretation_present(self, cert):
        assert "irreducible" in cert["irreducible_floor_interpretation"].lower()

    def test_deterministic(self):
        c1 = p518_upgrade_certificate()
        c2 = p518_upgrade_certificate()
        assert c1["fraction_resolved"] == pytest.approx(c2["fraction_resolved"])


# ── architecture_limit_upgrade_report ─────────────────────────────────────────


class TestArchitectureLimitUpgradeReport:
    @pytest.fixture(scope="class")
    def report(self):
        return architecture_limit_upgrade_report()

    def test_pillar_number(self, report):
        assert report["pillar"] == 523

    def test_status(self, report):
        assert report["status"] == "ARCHITECTURE_LIMIT_UPGRADED"

    def test_track_label(self, report):
        assert "ADJACENT TRACK" in report["track"]

    def test_upgrade_registry(self, report):
        assert PRIOR_STATUS_P517 in report["upgrade_registry"]
        assert PRIOR_STATUS_P518 in report["upgrade_registry"]

    def test_p517_certificate_present(self, report):
        assert "p517_certificate" in report
        assert report["p517_certificate"]["upgrade_is_valid"] is True

    def test_p518_certificate_present(self, report):
        assert "p518_certificate" in report
        assert report["p518_certificate"]["upgrade_is_valid"] is True

    def test_summary_both_valid(self, report):
        assert report["summary"]["both_valid"] is True

    def test_summary_upgrades_issued(self, report):
        assert report["summary"]["upgrades_issued"] == 2

    def test_no_hardgate_score_change(self, report):
        assert report["no_hardgate_score_change"] is True

    def test_upstream_pillars(self, report):
        assert 517 in report["upstream_pillars"]
        assert 518 in report["upstream_pillars"]
        assert 519 in report["upstream_pillars"]
        assert 520 in report["upstream_pillars"]
        assert 521 in report["upstream_pillars"]

    def test_downstream_pillars(self, report):
        assert 524 in report["downstream_pillars"]

    def test_epistemic_note_present(self, report):
        assert len(report["epistemic_note"]) > 50

    def test_deterministic(self):
        r1 = architecture_limit_upgrade_report()
        r2 = architecture_limit_upgrade_report()
        assert (
            r1["p517_certificate"]["p_r_conditional"]
            == pytest.approx(r2["p517_certificate"]["p_r_conditional"])
        )
        assert (
            r1["p518_certificate"]["fraction_resolved"]
            == pytest.approx(r2["p518_certificate"]["fraction_resolved"])
        )
