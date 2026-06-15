# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_az_os_hils.py — HILS Enforcement Layer Tests

Tests for the Human-in-the-Loop Safety invariant engine:
  - HILSAction enum completeness
  - Token lifecycle (issue / use / expire / double-use)
  - HILSViolation on missing approval
  - Audit trail integrity

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
import time
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from az_os.hils import HILS, HILSAction, HILSViolation, ApprovalToken


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def hils(tmp_path):
    return HILS(repo_root=tmp_path)


# ── HILSAction tests ───────────────────────────────────────────────────────

def test_hils_action_all_nine_defined():
    """There must be exactly 9 hardgate actions."""
    actions = list(HILSAction)
    assert len(actions) == 9, f"Expected 9 HILSAction variants, got {len(actions)}"


def test_hils_action_names_are_strings():
    for action in HILSAction:
        assert isinstance(action.value, str)
        assert len(action.value) > 0


def test_hils_action_pillar_canonicalise_exists():
    assert "PILLAR_CANONICALISE" in HILSAction.__members__


def test_hils_action_kernel_ring0_access_exists():
    assert "KERNEL_RING0_ACCESS" in HILSAction.__members__


def test_hils_action_test_delete_exists():
    assert "TEST_DELETE" in HILSAction.__members__


# ── ApprovalToken lifecycle (via HILS.issue_approval) ─────────────────────

def test_approval_token_is_valid_on_creation(hils):
    token = hils.issue_approval(HILSAction.KERNEL_RING0_ACCESS, ttl=60)
    assert token.is_valid()


def test_approval_token_expires_after_ttl(hils):
    token = hils.issue_approval(HILSAction.COMMIT_TO_MAIN, ttl=1)
    time.sleep(1.1)
    assert not token.is_valid()


def test_approval_token_single_use(hils):
    token = hils.issue_approval(HILSAction.TEST_DELETE, ttl=60)
    token.consume()
    assert not token.is_valid(), "Token must be invalid after single use"


def test_approval_token_cannot_be_used_twice(hils):
    token = hils.issue_approval(HILSAction.TEST_MODIFY_ASSERTION, ttl=60)
    # First use succeeds
    hils.require_approval(HILSAction.TEST_MODIFY_ASSERTION, token)
    # Second use must raise (token consumed)
    with pytest.raises(HILSViolation):
        hils.require_approval(HILSAction.TEST_MODIFY_ASSERTION, token)


def test_approval_token_action_mismatch_raises(hils):
    token = hils.issue_approval(HILSAction.AUTHORSHIP_MODIFY, ttl=60)
    with pytest.raises(HILSViolation):
        hils.require_approval(HILSAction.COMMIT_TO_MAIN, token)


# ── HILS.require_approval tests ────────────────────────────────────────────

def test_require_approval_passes_with_valid_token(hils):
    token = hils.issue_approval(HILSAction.KERNEL_RING0_ACCESS, ttl=60)
    # Should not raise
    hils.require_approval(HILSAction.KERNEL_RING0_ACCESS, token)


def test_require_approval_raises_without_token(hils):
    with pytest.raises(HILSViolation):
        hils.require_approval(HILSAction.PILLAR_CANONICALISE, None)


def test_require_approval_raises_with_expired_token(hils):
    token = hils.issue_approval(HILSAction.FALSIFICATION_MODIFY, ttl=1)
    time.sleep(1.1)
    with pytest.raises(HILSViolation):
        hils.require_approval(HILSAction.FALSIFICATION_MODIFY, token)


def test_require_approval_with_consumed_token(hils):
    token = hils.issue_approval(HILSAction.TEST_DELETE, ttl=60)
    hils.require_approval(HILSAction.TEST_DELETE, token)
    # Token is consumed; second call should raise
    with pytest.raises(HILSViolation):
        hils.require_approval(HILSAction.TEST_DELETE, token)


# ── Audit trail tests ──────────────────────────────────────────────────────

def test_audit_log_populated_on_issue(hils):
    hils.issue_approval(HILSAction.AUTHORSHIP_MODIFY, ttl=60)
    log = hils.audit_log()
    assert len(log) >= 1


def test_audit_log_populated_on_violation(hils):
    before = len(hils.audit_log())
    try:
        hils.require_approval(HILSAction.COMMIT_TO_MAIN, None)
    except HILSViolation:
        pass
    after = len(hils.audit_log())
    assert after > before, "Violation must be logged"


def test_audit_log_entries_have_required_fields(hils):
    hils.issue_approval(HILSAction.AGENT_SPAWN_UNLIMITED, ttl=60)
    for entry in hils.audit_log():
        assert "action" in entry
        assert "timestamp" in entry


# ── Integration: full HILS round-trip ──────────────────────────────────────

def test_hils_full_roundtrip(hils):
    """Issue a token, consume it, verify audit has both events."""
    token = hils.issue_approval(HILSAction.KERNEL_RING0_ACCESS, ttl=60)
    assert token.is_valid()
    hils.require_approval(HILSAction.KERNEL_RING0_ACCESS, token)
    assert not token.is_valid()
    log = hils.audit_log()
    # At least two entries: one for issue, one for consume
    assert len(log) >= 2
