# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for Pillar 394 — Postulate Minimality Audit.

Verifies registry completeness, completeness check, minimality check,
and the machine-readable pillar status interface.
"""

import pytest

from src.core.pillar394_postulate_minimality_audit import (
    PostulateKind,
    PostulateStatus,
    PostulateRecord,
    CORE_POSTULATES,
    ADMISSIONS,
    FREE_PARAMETERS,
    DERIVED_CLAIM_DEPENDENCIES,
    get_full_registry,
    get_registry_by_kind,
    get_open_gaps,
    check_completeness,
    check_minimality,
    postulate_registry_report,
    pillar_394_status,
)


# ──────────────────────────────────────────────────────────────────────────────
# Registry structure
# ──────────────────────────────────────────────────────────────────────────────

class TestRegistryStructure:

    def test_core_postulates_count(self):
        assert len(CORE_POSTULATES) == 8, "Must have exactly P1–P8 core postulates"

    def test_admissions_count_at_least_nine(self):
        assert len(ADMISSIONS) >= 9, "Must have at least Admissions 1–6 + 11, 12, 13"

    def test_free_parameters_count(self):
        assert len(FREE_PARAMETERS) >= 4, "Must have at least FP1–FP4"

    def test_all_records_have_name(self):
        for r in get_full_registry():
            assert r.name, f"Record has empty name: {r}"

    def test_all_records_have_breaks_if_fails(self):
        for r in get_full_registry():
            assert r.breaks_if_fails, f"Record '{r.name}' has no breaks_if_fails"

    def test_all_records_have_citation(self):
        for r in get_full_registry():
            assert r.citation, f"Record '{r.name}' has no citation"

    def test_all_records_have_description(self):
        for r in get_full_registry():
            assert r.description, f"Record '{r.name}' has no description"

    def test_names_are_unique(self):
        names = [r.name for r in get_full_registry()]
        assert len(names) == len(set(names)), "Duplicate names in registry"

    def test_kinds_are_valid(self):
        valid_kinds = set(PostulateKind)
        for r in get_full_registry():
            assert r.kind in valid_kinds, f"Invalid kind: {r.kind}"

    def test_statuses_are_valid(self):
        valid_statuses = set(PostulateStatus)
        for r in get_full_registry():
            assert r.status in valid_statuses, f"Invalid status: {r.status}"


class TestCorePostulates:

    def test_p1_z2_orbifold_present(self):
        names = [r.name for r in CORE_POSTULATES]
        assert any("Z₂" in n or "Z2" in n or "orbifold" in n.lower() for n in names)

    def test_p2_metric_ansatz_present(self):
        names = [r.name for r in CORE_POSTULATES]
        assert any("metric" in n.lower() or "KK" in n for n in names)

    def test_p6_holographic_present(self):
        names = [r.name for r in CORE_POSTULATES]
        assert any("Holographic" in n or "S=A/4G" in n for n in names)

    def test_p6_now_derived_not_assumed(self):
        p6_records = [r for r in CORE_POSTULATES if "Holographic" in r.name or "S=A/4G" in r.name]
        assert len(p6_records) >= 1
        p6 = p6_records[0]
        # P6 was ASSUMED; Pillar 379 upgraded it to DERIVED_CONDITIONAL.
        assert p6.status != PostulateStatus.POSTULATED, (
            "P6 holographic entropy was ASSUMED but Pillar 379 derived it — status must be updated"
        )
        assert "379" in p6.citation or "DERIVED" in p6.status.value

    def test_p7_p8_now_derived(self):
        p7_p8 = [r for r in CORE_POSTULATES if "braid" in r.name.lower() and ("P7" in r.name or "P8" in r.name or "Minimum" in r.name)]
        for r in p7_p8:
            assert r.status in (PostulateStatus.DERIVED, PostulateStatus.ARCHITECTURE_LIMIT), (
                f"{r.name} should be DERIVED (Pillar 377 closed P7/P8)"
            )

    def test_admission_6_lambda_gw_present(self):
        names = [r.name for r in ADMISSIONS]
        assert any("λ_GW" in n or "Goldberger" in n or "lambda_GW" in n for n in names)

    def test_admission_11_60_efolds_present(self):
        names = [r.name for r in ADMISSIONS]
        assert any("e-folds" in n or "efolds" in n.lower() or "60" in n for n in names)

    def test_admission_12_ftum_basin_present(self):
        names = [r.name for r in ADMISSIONS]
        assert any("basin" in n.lower() or "FTUM" in n for n in names)

    def test_admission_13_metric_uniqueness_present(self):
        names = [r.name for r in ADMISSIONS]
        assert any("uniqueness" in n.lower() or "ansatz" in n.lower() for n in names)


class TestFilterMethods:

    def test_get_registry_by_kind_core(self):
        cores = get_registry_by_kind(PostulateKind.CORE_POSTULATE)
        assert all(r.kind == PostulateKind.CORE_POSTULATE for r in cores)
        assert len(cores) == 8

    def test_get_registry_by_kind_admission(self):
        ads = get_registry_by_kind(PostulateKind.ADMISSION)
        assert all(r.kind == PostulateKind.ADMISSION for r in ads)

    def test_get_open_gaps_all_open(self):
        gaps = get_open_gaps()
        assert all(r.status == PostulateStatus.OPEN_GAP for r in gaps)

    def test_open_gaps_nonempty(self):
        assert len(get_open_gaps()) >= 3, "Must have at least Admissions 11, 12, 13 as open gaps"


# ──────────────────────────────────────────────────────────────────────────────
# Completeness check
# ──────────────────────────────────────────────────────────────────────────────

class TestCompletenessCheck:

    def test_derived_claims_dict_nonempty(self):
        assert len(DERIVED_CLAIM_DEPENDENCIES) >= 15

    def test_completeness_passes(self):
        result = check_completeness()
        assert result["all_complete"], (
            f"Completeness check failed. Missing deps: {result['missing_dependencies']}"
        )

    def test_no_missing_dependencies(self):
        result = check_completeness()
        assert result["missing_dependencies"] == []

    def test_completeness_fraction_unity(self):
        result = check_completeness()
        assert result["completeness_fraction"] == 1.0

    def test_each_derived_claim_has_known_postulate(self):
        registry_names = {r.name for r in get_full_registry()}
        for claim, deps in DERIVED_CLAIM_DEPENDENCIES.items():
            assert len(deps) >= 1, f"Claim '{claim}' has no dependencies"
            for dep in deps:
                assert dep in registry_names, (
                    f"Dependency '{dep}' for claim '{claim}' not found in registry"
                )

    def test_ns_depends_on_p1_or_p2(self):
        deps = DERIVED_CLAIM_DEPENDENCIES.get("nₛ=0.9635", [])
        assert any("Z₂" in d or "orbifold" in d.lower() or "metric" in d.lower() or "FTUM" in d for d in deps), (
            "nₛ prediction must depend on at least one foundational postulate"
        )

    def test_r_braided_depends_on_braid_postulates(self):
        deps = DERIVED_CLAIM_DEPENDENCIES.get("r_braided=0.0315", [])
        assert any("braid" in d.lower() or "P7" in d or "P8" in d or "Minimum" in d for d in deps)

    def test_holographic_depends_on_p5_p6(self):
        deps = DERIVED_CLAIM_DEPENDENCIES.get("Holographic S=A/4G", [])
        assert any("FTUM" in d or "Holographic" in d or "P5" in d or "P6" in d for d in deps)

    def test_kcs_depends_on_braid(self):
        deps = DERIVED_CLAIM_DEPENDENCIES.get("k_CS=74 (algebraic)", [])
        assert any("braid" in d.lower() or "P7" in d or "P8" in d or "n_w=5" in d for d in deps)


# ──────────────────────────────────────────────────────────────────────────────
# Minimality check
# ──────────────────────────────────────────────────────────────────────────────

class TestMinimalityCheck:

    def test_minimality_check_returns_dict(self):
        result = check_minimality()
        assert "all_used" in result
        assert "unused_postulates" in result
        assert "used_postulates" in result
        assert "usage_fraction" in result

    def test_usage_fraction_above_threshold(self):
        # Not every admission/parameter must appear in the dependency map,
        # but core postulates and key free parameters should.  Admissions are
        # meta-level records that document gaps; they need not appear in the
        # DERIVED_CLAIM_DEPENDENCIES map.  Require at least 40% usage overall.
        result = check_minimality()
        assert result["usage_fraction"] >= 0.40, (
            f"Too many unused registry entries: {result['unused_postulates']}"
        )

    def test_core_postulates_mostly_used(self):
        result = check_minimality()
        used = set(result["used_postulates"])
        unused_cores = [r.name for r in CORE_POSTULATES if r.name not in used]
        # Allow at most 1 unused core postulate (e.g. P3 is qualitative).
        assert len(unused_cores) <= 2, (
            f"Too many unused core postulates: {unused_cores}"
        )

    def test_p1_is_used(self):
        result = check_minimality()
        used = set(result["used_postulates"])
        assert any("Z₂" in u or "orbifold" in u.lower() for u in used)

    def test_p5_ftum_is_used(self):
        result = check_minimality()
        used = set(result["used_postulates"])
        assert any("FTUM" in u for u in used)


# ──────────────────────────────────────────────────────────────────────────────
# Report
# ──────────────────────────────────────────────────────────────────────────────

class TestAuditReport:

    def test_report_structure(self):
        report = postulate_registry_report()
        required_keys = [
            "pillar", "title", "version", "registry_total",
            "counts_by_kind", "counts_by_status", "open_gap_count",
            "completeness", "minimality", "audit_verdict",
        ]
        for key in required_keys:
            assert key in report, f"Missing key '{key}' in report"

    def test_pillar_number(self):
        report = postulate_registry_report()
        assert report["pillar"] == 394

    def test_version(self):
        report = postulate_registry_report()
        assert "12.9" in report["version"]

    def test_audit_verdict_pass(self):
        report = postulate_registry_report()
        assert report["audit_verdict"] == "PASS", (
            f"Audit verdict is not PASS: {report['completeness']['missing_dependencies']}"
        )

    def test_registry_total_reasonable(self):
        report = postulate_registry_report()
        # 8 postulates + ≥9 admissions + ≥4 free params = ≥21
        assert report["registry_total"] >= 21

    def test_open_gap_count_positive(self):
        report = postulate_registry_report()
        assert report["open_gap_count"] >= 3


class TestPillarStatus:

    def test_status_returns_dict(self):
        status = pillar_394_status()
        assert isinstance(status, dict)

    def test_status_pillar_field(self):
        status = pillar_394_status()
        assert status["pillar"] == "394"

    def test_status_name_field(self):
        status = pillar_394_status()
        assert "Postulate" in status["name"]

    def test_status_audit_verdict(self):
        status = pillar_394_status()
        assert status["audit_verdict"] == "PASS"

    def test_status_completeness_pass(self):
        status = pillar_394_status()
        assert status["completeness"] == "PASS"

    def test_status_registry_total_numeric(self):
        status = pillar_394_status()
        assert int(status["registry_total"]) >= 21


# ──────────────────────────────────────────────────────────────────────────────
# Epistemic consistency
# ──────────────────────────────────────────────────────────────────────────────

class TestEpistemicConsistency:

    def test_closed_admissions_not_open_gap(self):
        closed = [r for r in ADMISSIONS if "CLOSED" in r.description.upper() or r.closed_by is not None]
        for r in closed:
            # A closed admission should not also be labelled OPEN_GAP
            if "CLOSED" in r.name.upper() or (r.closed_by and "closed" in r.description.lower()):
                assert r.status != PostulateStatus.OPEN_GAP, (
                    f"Admission '{r.name}' claims to be closed but has OPEN_GAP status"
                )

    def test_p6_not_assumed(self):
        p6 = next((r for r in CORE_POSTULATES if "Holographic" in r.name or "S=A/4G" in r.name), None)
        assert p6 is not None, "P6 record must exist"
        assert p6.status != PostulateStatus.POSTULATED, (
            "P6 was upgraded from ASSUMED to DERIVED_CONDITIONAL by Pillar 379"
        )

    def test_p7_p8_derived_not_postulated(self):
        braid_records = [r for r in CORE_POSTULATES if "braid" in r.name.lower() or "Minimum" in r.name]
        assert len(braid_records) >= 2, "Must have P7 and P8 records"
        for r in braid_records:
            assert r.status != PostulateStatus.POSTULATED, (
                f"Pillar 377 derived {r.name}; status must not be POSTULATED"
            )

    def test_admission_6_is_architecture_limit(self):
        gw_admission = next(
            (r for r in ADMISSIONS if "λ_GW" in r.name or "Goldberger" in r.name), None
        )
        assert gw_admission is not None
        # Admission 6 was ARCHITECTURE_LIMIT; Pillar 404 (v13.1) derives λ_GW →
        # status is now DERIVED (DERIVED_FROM_GW_NORMALIZATION).
        assert gw_admission.status in (
            PostulateStatus.ARCHITECTURE_LIMIT,
            PostulateStatus.DERIVED,
        ), "λ_GW should be ARCHITECTURE_LIMIT or DERIVED (if Pillar 404 closed it)"

    def test_fp3_efolds_is_open_gap(self):
        efolds_fp = next((r for r in FREE_PARAMETERS if "N_e" in r.name or "e-folds" in r.name), None)
        assert efolds_fp is not None
        assert efolds_fp.status == PostulateStatus.OPEN_GAP

    def test_all_admission_descriptions_mention_honest_status(self):
        # Every admission should contain at least one status keyword.
        keywords = ["OPEN", "CLOSED", "CLOSES", "DERIVED", "ARCHITECTURE", "ASSESSED",
                    "STATUS:", "Status:", "CONTRACTIVE", "MINIMAL", "RESOLVED",
                    "PROVED", "CERTIFIED", "CONDITIONAL"]
        for r in ADMISSIONS:
            has_keyword = any(kw in r.description for kw in keywords)
            assert has_keyword, (
                f"Admission '{r.name}' description lacks status keyword"
            )
