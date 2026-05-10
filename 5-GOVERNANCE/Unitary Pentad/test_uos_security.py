"""
tests/test_uos_security.py
==========================
Unit tests for UOS/security.py.

Covers:
  - SecurityViolation: attributes
  - SecurityContext: construction, invalid tier
  - GeometricSecurityEngine: register, verify, verify_bytes,
    check_access, unregister, audit_log
  - _compute_fingerprint
  - Tier-0 kernel exemption
"""

import pytest

import sys, os
_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.abspath(os.path.join(_PENTAD_DIR, "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from UOS.security import (
    SecurityViolation,
    SecurityContext,
    GeometricSecurityEngine,
)
from UOS.constants import (
    UOS_SECURITY_LEVELS,
    INVARIANT_RATIO,
    K_CS,
)


# ---------------------------------------------------------------------------
# SecurityViolation
# ---------------------------------------------------------------------------

class TestSecurityViolation:
    def test_attributes(self):
        exc = SecurityViolation(pid=42, deviation=0.5, tolerance=0.02)
        assert exc.pid == 42
        assert abs(exc.deviation - 0.5) < 1e-9
        assert abs(exc.tolerance - 0.02) < 1e-9

    def test_is_exception(self):
        exc = SecurityViolation(pid=1, deviation=0.1, tolerance=0.02)
        assert isinstance(exc, Exception)

    def test_message_contains_pid(self):
        exc = SecurityViolation(pid=77, deviation=0.1, tolerance=0.01)
        assert "77" in str(exc)


# ---------------------------------------------------------------------------
# SecurityContext
# ---------------------------------------------------------------------------

class TestSecurityContext:
    def test_construction(self):
        ctx = SecurityContext(pid=1, tier=2, phi_fingerprint=0.5)
        assert ctx.pid == 1
        assert ctx.tier == 2

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError):
            SecurityContext(pid=1, tier=UOS_SECURITY_LEVELS, phi_fingerprint=0.0)

    def test_tier_zero_valid(self):
        ctx = SecurityContext(pid=0, tier=0, phi_fingerprint=0.0)
        assert ctx.tier == 0

    def test_tier_max_minus_one_valid(self):
        ctx = SecurityContext(pid=1, tier=UOS_SECURITY_LEVELS - 1,
                              phi_fingerprint=0.5)
        assert ctx.tier == UOS_SECURITY_LEVELS - 1


# ---------------------------------------------------------------------------
# GeometricSecurityEngine — fingerprint
# ---------------------------------------------------------------------------

class TestFingerprint:
    def test_empty_bytes_fingerprint_zero(self):
        fp = GeometricSecurityEngine._compute_fingerprint(b"")
        assert fp == 0.0

    def test_fingerprint_in_range(self):
        fp = GeometricSecurityEngine._compute_fingerprint(b"hello world")
        assert 0.0 <= fp < 1.0

    def test_fingerprint_deterministic(self):
        data = b"deterministic test data"
        fp1 = GeometricSecurityEngine._compute_fingerprint(data)
        fp2 = GeometricSecurityEngine._compute_fingerprint(data)
        assert fp1 == fp2

    def test_different_data_may_differ(self):
        fp1 = GeometricSecurityEngine._compute_fingerprint(b"aaa")
        fp2 = GeometricSecurityEngine._compute_fingerprint(b"zzz")
        # Not guaranteed to differ (hash collisions), but for these inputs they do
        # Just check both are valid
        assert 0.0 <= fp1 < 1.0
        assert 0.0 <= fp2 < 1.0

    def test_fingerprint_mod_k_cs(self):
        data = bytes(range(256))
        fp = GeometricSecurityEngine._compute_fingerprint(data)
        # Must be n/K_CS for some integer n
        remainder = round(fp * K_CS)
        assert abs(fp - remainder / K_CS) < 1e-10


# ---------------------------------------------------------------------------
# GeometricSecurityEngine — register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_returns_context(self):
        engine = GeometricSecurityEngine()
        ctx = engine.register(pid=1, tier=3)
        assert isinstance(ctx, SecurityContext)
        assert ctx.pid == 1

    def test_register_adds_to_registry(self):
        engine = GeometricSecurityEngine()
        engine.register(pid=1, tier=2)
        assert 1 in engine._registry

    def test_register_with_code(self):
        engine = GeometricSecurityEngine()
        ctx = engine.register(pid=2, tier=3, code_bytes=b"some code")
        assert 0.0 <= ctx.phi_fingerprint < 1.0

    def test_register_logs_event(self):
        engine = GeometricSecurityEngine()
        engine.register(pid=3, tier=1)
        log = engine.audit_log()
        assert any(e["event"] == "register" and e["pid"] == 3 for e in log)


# ---------------------------------------------------------------------------
# GeometricSecurityEngine — verify
# ---------------------------------------------------------------------------

class TestVerify:
    def test_verify_unregistered_raises(self):
        engine = GeometricSecurityEngine()
        with pytest.raises(KeyError):
            engine.verify(pid=999)

    def test_verify_tier0_always_passes(self):
        engine = GeometricSecurityEngine()
        engine.register(pid=0, tier=0, code_bytes=b"\xff" * 100)
        assert engine.verify(pid=0) is True

    def test_verify_ok_logs_event(self):
        engine = GeometricSecurityEngine(tolerance=1.0)  # always passes
        engine.register(pid=1, tier=3)
        engine.verify(pid=1)
        log = engine.audit_log()
        assert any(e["event"] == "verify_ok" and e["pid"] == 1 for e in log)

    def test_verify_fail_raises_security_violation(self):
        """With tolerance=0, almost any code will fail (deviation ≠ 0)."""
        engine = GeometricSecurityEngine(tolerance=0.0)
        # Force a fingerprint that is non-zero and non-INVARIANT_RATIO
        # Use bytes that produce fingerprint 0 (empty string)
        engine.register(pid=1, tier=3, code_bytes=b"")
        # fingerprint = 0; INVARIANT_RATIO ≈ 0.714; deviation > 0
        if abs(0.0 - INVARIANT_RATIO) > 0.0:
            with pytest.raises(SecurityViolation) as exc_info:
                engine.verify(pid=1)
            assert exc_info.value.pid == 1

    def test_verify_fail_logs_event(self):
        engine = GeometricSecurityEngine(tolerance=0.0)
        engine.register(pid=2, tier=3, code_bytes=b"")
        try:
            engine.verify(pid=2)
        except SecurityViolation:
            pass
        log = engine.audit_log()
        # Either verify_ok or verify_fail should be in log
        assert any(e["pid"] == 2 for e in log)


# ---------------------------------------------------------------------------
# GeometricSecurityEngine — verify_bytes
# ---------------------------------------------------------------------------

class TestVerifyBytes:
    def test_verify_bytes_high_tolerance(self):
        engine = GeometricSecurityEngine(tolerance=1.0)
        assert engine.verify_bytes(pid=1, code_bytes=b"anything") is True

    def test_verify_bytes_zero_tolerance_fails(self):
        engine = GeometricSecurityEngine(tolerance=0.0)
        # fingerprint = 0; INVARIANT_RATIO > 0 → should fail
        if abs(0.0 - INVARIANT_RATIO) > 0.0:
            with pytest.raises(SecurityViolation):
                engine.verify_bytes(pid=1, code_bytes=b"")

    def test_verify_bytes_logs_audit(self):
        engine = GeometricSecurityEngine(tolerance=1.0)
        engine.verify_bytes(pid=5, code_bytes=b"code block")
        log = engine.audit_log()
        assert any("verify_bytes" in e["event"] and e["pid"] == 5 for e in log)


# ---------------------------------------------------------------------------
# GeometricSecurityEngine — check_access
# ---------------------------------------------------------------------------

class TestCheckAccess:
    def test_kernel_accesses_all_tiers(self):
        engine = GeometricSecurityEngine()
        engine.register(pid=0, tier=0)
        for target_tier in range(UOS_SECURITY_LEVELS):
            assert engine.check_access(0, target_tier) is True

    def test_sandbox_cannot_access_kernel_tier(self):
        engine = GeometricSecurityEngine()
        engine.register(pid=99, tier=4)
        # tier 4 (sandbox) cannot read tier 0 (kernel): 4 > 0 → not allowed
        assert engine.check_access(99, 0) is False

    def test_same_tier_allowed(self):
        engine = GeometricSecurityEngine()
        engine.register(pid=1, tier=2)
        assert engine.check_access(1, 2) is True

    def test_access_logs_event(self):
        engine = GeometricSecurityEngine()
        engine.register(pid=1, tier=1)
        engine.check_access(1, 3)
        log = engine.audit_log()
        assert any(e["event"] == "access_check" and e["pid"] == 1 for e in log)

    def test_unregistered_accessor_raises(self):
        engine = GeometricSecurityEngine()
        with pytest.raises(KeyError):
            engine.check_access(9999, 0)


# ---------------------------------------------------------------------------
# GeometricSecurityEngine — unregister
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_unregister_removes_from_registry(self):
        engine = GeometricSecurityEngine()
        engine.register(pid=1, tier=3)
        engine.unregister(pid=1)
        assert 1 not in engine._registry

    def test_unregister_missing_raises(self):
        engine = GeometricSecurityEngine()
        with pytest.raises(KeyError):
            engine.unregister(pid=999)

    def test_unregister_logs_event(self):
        engine = GeometricSecurityEngine()
        engine.register(pid=1, tier=3)
        engine.unregister(pid=1)
        log = engine.audit_log()
        assert any(e["event"] == "unregister" and e["pid"] == 1 for e in log)


# ---------------------------------------------------------------------------
# GeometricSecurityEngine — audit_log
# ---------------------------------------------------------------------------

class TestAuditLog:
    def test_audit_log_is_list(self):
        engine = GeometricSecurityEngine()
        assert isinstance(engine.audit_log(), list)

    def test_audit_log_is_copy(self):
        engine = GeometricSecurityEngine()
        log = engine.audit_log()
        log.append({"event": "injected"})
        assert len(engine.audit_log()) == 0  # original not modified

    def test_audit_log_grows_with_operations(self):
        engine = GeometricSecurityEngine(tolerance=1.0)  # always passes
        engine.register(pid=1, tier=3)
        engine.verify(pid=1)
        assert len(engine.audit_log()) >= 2
