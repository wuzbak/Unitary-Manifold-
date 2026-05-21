# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 320 — CONDITIONAL_DERIVATION Audit."""
import pytest
from src.core.pillar320_conditional_derivation_audit import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    CONDITIONAL_DERIVATION_REGISTRY,
    conditional_derivation_audit_report,
    sprint_v11_15_label_upgrades,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 320


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


# ── Registry ───────────────────────────────────────────────────────────────────

def test_registry_is_list():
    assert isinstance(CONDITIONAL_DERIVATION_REGISTRY, list)


def test_registry_has_entries():
    assert len(CONDITIONAL_DERIVATION_REGISTRY) >= 6


def test_registry_p17_present():
    claim_ids = [c["claim_id"] for c in CONDITIONAL_DERIVATION_REGISTRY]
    assert "P17__DM2_31" in claim_ids


def test_registry_convention_279_3_present():
    claim_ids = [c["claim_id"] for c in CONDITIONAL_DERIVATION_REGISTRY]
    assert "CONVENTION_279_3" in claim_ids


def test_registry_seesaw_gap_present():
    claim_ids = [c["claim_id"] for c in CONDITIONAL_DERIVATION_REGISTRY]
    assert "SEESAW_TEXTURE_PARTICIPATION_GAP" in claim_ids


def test_registry_wkk_formula_present():
    claim_ids = [c["claim_id"] for c in CONDITIONAL_DERIVATION_REGISTRY]
    assert "WKK_FORMULA_VALIDITY" in claim_ids


def test_registry_braid_stability_present():
    claim_ids = [c["claim_id"] for c in CONDITIONAL_DERIVATION_REGISTRY]
    assert "BRAID_STABILITY_57" in claim_ids


def test_registry_ftum_convergence_present():
    claim_ids = [c["claim_id"] for c in CONDITIONAL_DERIVATION_REGISTRY]
    assert "FTUM_CONVERGENCE_GENERAL" in claim_ids


def test_registry_all_have_claim_id():
    for claim in CONDITIONAL_DERIVATION_REGISTRY:
        assert "claim_id" in claim


def test_registry_all_have_prior_label():
    for claim in CONDITIONAL_DERIVATION_REGISTRY:
        assert "prior_label" in claim


def test_registry_all_have_new_label():
    for claim in CONDITIONAL_DERIVATION_REGISTRY:
        assert "new_label" in claim


def test_registry_all_have_outcome():
    for claim in CONDITIONAL_DERIVATION_REGISTRY:
        assert "outcome" in claim
        assert claim["outcome"] in (
            "UPGRADE_TO_DERIVED",
            "UPGRADE_TO_CONSTRAINED",
            "CERTIFY_ARCHITECTURE_LIMIT",
        )


def test_registry_all_have_resolution_pillar():
    for claim in CONDITIONAL_DERIVATION_REGISTRY:
        assert "resolution_pillar" in claim
        assert 300 <= claim["resolution_pillar"] <= 320


# ── Specific claim checks ──────────────────────────────────────────────────────

def test_p17_outcome():
    p17 = next(c for c in CONDITIONAL_DERIVATION_REGISTRY if c["claim_id"] == "P17__DM2_31")
    assert p17["outcome"] == "CERTIFY_ARCHITECTURE_LIMIT"


def test_p17_resolution_pillar():
    p17 = next(c for c in CONDITIONAL_DERIVATION_REGISTRY if c["claim_id"] == "P17__DM2_31")
    assert p17["resolution_pillar"] == 319


def test_convention_279_3_outcome_derived():
    c = next(c for c in CONDITIONAL_DERIVATION_REGISTRY if c["claim_id"] == "CONVENTION_279_3")
    assert c["outcome"] == "UPGRADE_TO_DERIVED"


def test_wkk_formula_outcome_derived():
    c = next(c for c in CONDITIONAL_DERIVATION_REGISTRY if c["claim_id"] == "WKK_FORMULA_VALIDITY")
    assert c["outcome"] == "UPGRADE_TO_DERIVED"


def test_braid_stability_outcome_derived():
    c = next(c for c in CONDITIONAL_DERIVATION_REGISTRY if c["claim_id"] == "BRAID_STABILITY_57")
    assert c["outcome"] == "UPGRADE_TO_DERIVED"


def test_ftum_convergence_outcome_derived():
    c = next(c for c in CONDITIONAL_DERIVATION_REGISTRY if c["claim_id"] == "FTUM_CONVERGENCE_GENERAL")
    assert c["outcome"] == "UPGRADE_TO_DERIVED"


# ── Audit report ───────────────────────────────────────────────────────────────

def test_audit_report_returns_dict():
    report = conditional_derivation_audit_report()
    assert isinstance(report, dict)


def test_audit_report_version():
    report = conditional_derivation_audit_report()
    assert report["audit_version"] == "v11.15"


def test_audit_report_total_claims():
    report = conditional_derivation_audit_report()
    assert report["total_claims"] == len(CONDITIONAL_DERIVATION_REGISTRY)


def test_audit_report_all_resolved():
    report = conditional_derivation_audit_report()
    assert report["all_claims_resolved"] is True


def test_audit_report_verdict():
    report = conditional_derivation_audit_report()
    assert "ALL" in report["audit_verdict"]


def test_audit_report_outcomes_positive():
    report = conditional_derivation_audit_report()
    total = (
        report["upgrades_to_derived"]
        + report["upgrades_to_constrained"]
        + report["architecture_limits_certified"]
    )
    assert total == report["total_claims"]


def test_audit_report_arch_limits_positive():
    report = conditional_derivation_audit_report()
    assert report["architecture_limits_certified"] >= 2   # P17 + seesaw


def test_audit_report_derived_upgrades_positive():
    report = conditional_derivation_audit_report()
    assert report["upgrades_to_derived"] >= 3   # wkk + braid + ftum + convention


# ── Sprint label upgrades ──────────────────────────────────────────────────────

def test_label_upgrades_returns_list():
    result = sprint_v11_15_label_upgrades()
    assert isinstance(result, list)


def test_label_upgrades_length():
    result = sprint_v11_15_label_upgrades()
    assert len(result) == len(CONDITIONAL_DERIVATION_REGISTRY)


def test_label_upgrades_all_have_keys():
    result = sprint_v11_15_label_upgrades()
    for entry in result:
        assert "claim_id" in entry
        assert "prior_label" in entry
        assert "new_label" in entry
        assert "pillar" in entry
        assert "outcome" in entry


# ── Separation guard ───────────────────────────────────────────────────────────

def test_separation_guard():
    assert "SEPARATION_INTACT" in separation_guard()
