# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests — Lane 2: Closure quality gate.

Validates that every promoted DERIVED claim has a real derivation artifact
and a real test, that no promotion was made by narrative pressure, and that
the gate log itself is structurally complete.
"""
from __future__ import annotations

import pytest

pytest.importorskip("yaml", reason="pyyaml required for closure quality gate tests")

from src.core.closure_quality_gate import (  # noqa: E402
    audit_artifact_presence,
    full_audit,
    load_closure_gate,
    validate_gate_integrity,
)

# All P-numbered claims that appear in CLAIM_MASTER_BOARD as DERIVED
EXPECTED_PROMOTION_IDS = {
    "P1", "P2", "P3", "P4", "P5", "P6",
    "P7-P10", "P12", "P13", "P14", "P15",
    "P16", "P17", "P18", "P19", "P20",
    "P21", "P22", "P26", "P27", "P28",
    "P29-P33",
}


@pytest.fixture(scope="module")
def gate():
    return load_closure_gate()


class TestGateLoads:
    def test_loads_without_error(self, gate):
        assert isinstance(gate, dict)

    def test_has_promotions(self, gate):
        assert len(gate.get("promotions", [])) > 0

    def test_has_version(self, gate):
        assert "version" in gate

    def test_has_governance(self, gate):
        assert "governance" in gate

    def test_governance_has_prohibition(self, gate):
        gov = gate.get("governance", {})
        assert "prohibition" in gov


class TestGateIntegrity:
    def test_no_integrity_violations(self, gate):
        violations = validate_gate_integrity(gate)
        assert violations == [], "Closure gate integrity violations:\n" + "\n".join(violations)

    def test_all_expected_ids_logged(self, gate):
        logged_ids = {p["id"] for p in gate.get("promotions", [])}
        missing = EXPECTED_PROMOTION_IDS - logged_ids
        assert not missing, f"Promotion log missing entries for: {missing}"

    def test_all_gatekeepers_pass(self, gate):
        for promo in gate.get("promotions", []):
            assert promo.get("gatekeeper") == "PASS", (
                f"[{promo.get('id')}] gatekeeper must be PASS"
            )

    def test_all_to_labels_valid(self, gate):
        for promo in gate.get("promotions", []):
            tl = promo.get("to_label", "")
            assert tl in ("DERIVED", "ALGEBRAIC"), (
                f"[{promo.get('id')}] Invalid to_label: {tl}"
            )

    def test_no_narrative_pressure_in_grounds(self, gate):
        banned = [
            "narrative pressure", "score inflation",
            "without derivation", "community expectation"
        ]
        for promo in gate.get("promotions", []):
            grounds = str(promo.get("promotion_grounds", "")).lower()
            for phrase in banned:
                assert phrase not in grounds, (
                    f"[{promo.get('id')}] promotion_grounds contains banned phrase: '{phrase}'"
                )


class TestArtifactPresence:
    def test_all_derivation_artifacts_exist_on_disk(self, gate):
        missing = audit_artifact_presence(gate)
        assert missing == [], (
            "Missing derivation/test artifacts cited in closure gate:\n"
            + "\n".join(missing)
        )


class TestFullAudit:
    def test_full_audit_passes(self):
        result = full_audit()
        msgs = result["integrity_violations"] + result["missing_artifacts"]
        assert result["pass"], "Closure quality full audit FAILED:\n" + "\n".join(msgs)


class TestGateBlocksNarrativePromotion:
    def test_rejects_narrative_grounds(self):
        fake_gate = {
            "promotions": [{
                "id": "TEST",
                "parameter": "x",
                "from_label": "CONSTRAINED",
                "to_label": "DERIVED",
                "date": "2026-01-01",
                "wave": "test",
                "derivation_artifacts": ["src/core/test.py"],
                "test_artifacts": ["tests/test_x.py"],
                "promotion_grounds": "score inflation pressure from adjacent tracks",
                "gatekeeper": "PASS",
            }],
            "governance": {"prohibition": "narrative is not grounds"},
        }
        violations = validate_gate_integrity(fake_gate)
        assert any("score inflation" in v or "prohibited phrase" in v for v in violations)

    def test_rejects_non_pass_gatekeeper(self):
        fake_gate = {
            "promotions": [{
                "id": "TEST",
                "parameter": "x",
                "from_label": "CONSTRAINED",
                "to_label": "DERIVED",
                "date": "2026-01-01",
                "wave": "test",
                "derivation_artifacts": ["src/core/test.py"],
                "test_artifacts": ["tests/test_x.py"],
                "promotion_grounds": "Valid KK derivation with zero free parameters",
                "gatekeeper": "PENDING",
            }],
            "governance": {"prohibition": "narrative is not grounds"},
        }
        violations = validate_gate_integrity(fake_gate)
        assert any("gatekeeper" in v for v in violations)
