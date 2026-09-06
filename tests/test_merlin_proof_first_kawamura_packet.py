# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.merlin_proof_first_kawamura_packet as packet_mod
from src.core.merlin_proof_first_kawamura_packet import merlin_proof_first_kawamura_packet


def test_packet_is_valid_and_still_open() -> None:
    packet = merlin_proof_first_kawamura_packet()
    assert packet["target_gap_id"] == "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"
    assert packet["final_verdict"] == "still_open"
    assert packet["lean4"]["theorem_count"] == packet["lean4"]["expected_theorem_count"] == 8
    assert packet["substack_article"]["exists"] is True
    assert packet["valid"] is True


def test_open_residual_is_preserved() -> None:
    packet = merlin_proof_first_kawamura_packet()
    open_items = packet["burden_ledger"]["classification_buckets"]["open_residuals"]
    assert any(item.get("gap_id") == "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS" for item in open_items)
    assert any("functional-analysis" in item["item"].lower() for item in open_items)
    assert packet["burden_ledger"]["final_verdict_if_executed_today"] == "still_open"


def test_missing_article_fails_closed(monkeypatch, tmp_path) -> None:
    missing = tmp_path / "missing.md"

    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "stewardship": {
                    "default_final_verdict_until_residual_is_discharged": "still_open",
                },
                "article_contract": {
                    "path": str(missing),
                    "required_sections": [
                        "target_gap",
                        "method",
                        "merlin_contribution",
                        "cross_audit_result",
                        "remaining_residuals",
                    ],
                },
            }

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "classification_buckets": {
                    "open_residuals": [{"gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"}]
                },
                "final_verdict_if_executed_today": "still_open",
            }

        @staticmethod
        def get_merlin_cross_review_packet():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "reconciliation_policy": {
                    "final_verdict_if_unresolved_objection": "still_open",
                },
            }

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    monkeypatch.setattr(packet_mod, "_resolve_repo_path", lambda _path, _default: (missing, True))
    packet = merlin_proof_first_kawamura_packet()
    assert packet["substack_article"]["exists"] is False
    assert packet["valid"] is False


def test_empty_open_residuals_fail_closed(monkeypatch) -> None:
    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "stewardship": {
                    "default_final_verdict_until_residual_is_discharged": "still_open",
                },
            }

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {
                "classification_buckets": {"open_residuals": []},
                "final_verdict_if_executed_today": "still_open",
            }

        @staticmethod
        def get_merlin_cross_review_packet():
            return {
                "reconciliation_policy": {
                    "final_verdict_if_unresolved_objection": "still_open",
                },
            }

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    packet = merlin_proof_first_kawamura_packet()
    assert packet["burden_ledger"]["classification_buckets"]["open_residuals"] == []
    assert packet["valid"] is False


def test_missing_required_article_section_fails_closed(monkeypatch, tmp_path) -> None:
    article = tmp_path / "article.md"
    article.write_text("# Draft\n\n## The target gap\n\n## The method\n", encoding="utf-8")

    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "stewardship": {
                    "default_final_verdict_until_residual_is_discharged": "still_open",
                },
                "article_contract": {
                    "path": str(article),
                    "required_sections": [
                        "target_gap",
                        "method",
                        "merlin_contribution",
                    ],
                },
            }

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "classification_buckets": {
                    "open_residuals": [{"gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"}]
                },
                "final_verdict_if_executed_today": "still_open",
            }

        @staticmethod
        def get_merlin_cross_review_packet():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "reconciliation_policy": {
                    "final_verdict_if_unresolved_objection": "still_open",
                },
            }

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    monkeypatch.setattr(packet_mod, "_resolve_repo_path", lambda _path, _default: (article, True))
    packet = merlin_proof_first_kawamura_packet()
    assert packet["substack_article"]["required_sections"]["merlin_contribution"] is False
    assert packet["valid"] is False


def test_missing_lean_marker_fails_closed(monkeypatch, tmp_path) -> None:
    lean = tmp_path / "MerlinProofFirstKawamuraLedger.lean"
    lean.write_text(
        "namespace UnitaryManifold\n"
        "axiom KawamuraResidualStillOpen : Prop\n"
        "axiom NoTraceabilityEqualsClosure : Prop\n"
        "axiom DualLoopVerdictAgreementRequired : Prop\n"
        "theorem mpf_kawamura_kernel_1 : KawamuraResidualStillOpen := by exact KawamuraResidualStillOpen\n"
        "theorem mpf_kawamura_kernel_2 : NoTraceabilityEqualsClosure := by exact NoTraceabilityEqualsClosure\n"
        "theorem mpf_kawamura_kernel_3 : DualLoopVerdictAgreementRequired := by exact DualLoopVerdictAgreementRequired\n"
        "theorem mpf_kawamura_kernel_4 : KawamuraResidualStillOpen := by exact KawamuraResidualStillOpen\n"
        "theorem mpf_kawamura_kernel_5 : KawamuraResidualStillOpen := by exact KawamuraResidualStillOpen\n"
        "theorem mpf_kawamura_kernel_6 : KawamuraResidualStillOpen := by exact KawamuraResidualStillOpen\n"
        "theorem mpf_kawamura_kernel_7 : KawamuraResidualStillOpen := by exact KawamuraResidualStillOpen\n"
        "theorem mpf_kawamura_kernel_8 : KawamuraResidualStillOpen := by exact KawamuraResidualStillOpen\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(packet_mod, "_LEAN4_FILE", lean)
    packet = merlin_proof_first_kawamura_packet()
    assert packet["lean4"]["theorem_count"] == 8
    assert packet["lean4"]["semantic_markers"]["ExternalImportBoundaryPreserved"] is False
    assert packet["valid"] is False


def test_mismatched_ledger_target_fails_closed(monkeypatch) -> None:
    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "stewardship": {
                    "default_final_verdict_until_residual_is_discharged": "still_open",
                },
                "article_contract": {"required_sections": []},
            }

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {
                "target_gap_id": "SOME_OTHER_TARGET",
                "classification_buckets": {
                    "open_residuals": [{"gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"}]
                },
                "final_verdict_if_executed_today": "still_open",
            }

        @staticmethod
        def get_merlin_cross_review_packet():
            return {
                "reconciliation_policy": {
                    "final_verdict_if_unresolved_objection": "still_open",
                },
            }

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    packet = merlin_proof_first_kawamura_packet()
    assert packet["burden_ledger"]["target_gap_id"] == "SOME_OTHER_TARGET"
    assert packet["valid"] is False


def test_missing_ledger_structure_fails_closed(monkeypatch) -> None:
    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "stewardship": {
                    "default_final_verdict_until_residual_is_discharged": "still_open",
                },
                "article_contract": {"required_sections": []},
            }

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "final_verdict_if_executed_today": "still_open",
            }

        @staticmethod
        def get_merlin_cross_review_packet():
            return {
                "reconciliation_policy": {
                    "final_verdict_if_unresolved_objection": "still_open",
                },
            }

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    packet = merlin_proof_first_kawamura_packet()
    assert packet["burden_ledger"]["target_gap_id"] == "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"
    assert packet["valid"] is False


def test_missing_nested_policy_fields_fail_closed(monkeypatch) -> None:
    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "article_contract": {"required_sections": []},
            }

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "classification_buckets": {
                    "open_residuals": [{"gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"}]
                },
                "final_verdict_if_executed_today": "still_open",
            }

        @staticmethod
        def get_merlin_cross_review_packet():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
            }

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    packet = merlin_proof_first_kawamura_packet()
    assert packet["target_gap_id"] == "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"
    assert packet["valid"] is False


def test_non_list_open_residuals_fail_closed(monkeypatch) -> None:
    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "stewardship": {
                    "default_final_verdict_until_residual_is_discharged": "still_open",
                },
                "article_contract": {"required_sections": []},
            }

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "classification_buckets": {"open_residuals": "not-a-list"},
                "final_verdict_if_executed_today": "still_open",
            }

        @staticmethod
        def get_merlin_cross_review_packet():
            return {
                "reconciliation_policy": {
                    "final_verdict_if_unresolved_objection": "still_open",
                },
            }

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    packet = merlin_proof_first_kawamura_packet()
    assert packet["burden_ledger"]["classification_buckets"]["open_residuals"] == "not-a-list"
    assert packet["valid"] is False


def test_non_list_required_sections_fail_closed(monkeypatch) -> None:
    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "stewardship": {
                    "default_final_verdict_until_residual_is_discharged": "still_open",
                },
                "article_contract": {"required_sections": "not-a-list"},
            }

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "classification_buckets": {
                    "open_residuals": [{"gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"}]
                },
                "final_verdict_if_executed_today": "still_open",
            }

        @staticmethod
        def get_merlin_cross_review_packet():
            return {
                "reconciliation_policy": {
                    "final_verdict_if_unresolved_objection": "still_open",
                },
            }

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    packet = merlin_proof_first_kawamura_packet()
    assert packet["substack_article"]["required_sections"] == {}
    assert packet["valid"] is False


def test_loader_failure_returns_fail_closed_packet(monkeypatch) -> None:
    def _boom():
        raise ImportError("missing merlin package")

    monkeypatch.setattr(packet_mod, "_load_program_module", _boom)
    packet = merlin_proof_first_kawamura_packet()
    assert packet["charter"] == {}
    assert packet["burden_ledger"] == {}
    assert packet["cross_review_packet"] == {}
    assert packet["valid"] is False


def test_article_path_outside_repo_fails_closed(monkeypatch) -> None:
    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "stewardship": {
                    "default_final_verdict_until_residual_is_discharged": "still_open",
                },
                "article_contract": {
                    "path": "../../outside.md",
                    "required_sections": [],
                },
            }

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "classification_buckets": {
                    "open_residuals": [{"gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS"}]
                },
                "final_verdict_if_executed_today": "still_open",
            }

        @staticmethod
        def get_merlin_cross_review_packet():
            return {
                "target_gap_id": "KAWAMURA_INDEPENDENCE_FUNCTIONAL_ANALYSIS",
                "reconciliation_policy": {
                    "final_verdict_if_unresolved_objection": "still_open",
                },
            }

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    packet = merlin_proof_first_kawamura_packet()
    assert packet["substack_article"]["path"] == "7-OUTREACH/substack/posts/post-320-s04e023-merlin-proof-first-kawamura-sprint.md"
    assert packet["valid"] is False


def test_getter_failure_returns_fail_closed_packet(monkeypatch) -> None:
    class _FakeProgram:
        @staticmethod
        def get_proof_first_closure_charter():
            raise RuntimeError("broken getter")

        @staticmethod
        def get_kawamura_closure_burden_ledger():
            return {}

        @staticmethod
        def get_merlin_cross_review_packet():
            return {}

    monkeypatch.setattr(packet_mod, "_load_program_module", lambda: _FakeProgram())
    packet = merlin_proof_first_kawamura_packet()
    assert packet["charter"] == {}
    assert packet["valid"] is False
