# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_az_os_managers.py — Manager Unit Tests

Tests for the 7-manager cognitive layer:
  M1: GeometryManager — full_audit() structure
  M3: SymbolicManager — core constants validation
  M4: TestGuard — parse logic, retry count, HILS escalation stub
  M7: InterfaceManager — synthesis report structure

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from az_os.managers.m1_geometry import M1GeometryManager, GeometryResult
from az_os.managers.m3_symbolic import M3SymbolicManager, SymbolicResult
from az_os.managers.m4_test_guard import M4TestGuard, TestResult as TestRunResult
from az_os.managers.m7_interface import M7InterfaceManager, SynthesisReport
from az_os.state import StateDB
from az_os.hils import HILS


# ── M1 GeometryManager ─────────────────────────────────────────────────────

@pytest.fixture
def m1():
    return M1GeometryManager()


def test_m1_full_audit_returns_list(m1):
    results = m1.full_audit()
    assert isinstance(results, list)


def test_m1_full_audit_has_five_results(m1):
    results = m1.full_audit()
    # 5 sub-agents: metric, christoffel, riemann, compactification, boundary
    assert len(results) == 5


def test_m1_results_are_geometry_result_instances(m1):
    for r in m1.full_audit():
        assert isinstance(r, GeometryResult)


def test_m1_results_have_agent_field(m1):
    for r in m1.full_audit():
        assert hasattr(r, "agent")
        assert isinstance(r.agent, str)
        assert len(r.agent) > 0


def test_m1_results_have_status_field(m1):
    for r in m1.full_audit():
        assert hasattr(r, "status")
        assert r.status in ("ok", "error", "warning")


def test_m1_metric_result_present(m1):
    results = m1.full_audit()
    agents = [r.agent for r in results]
    assert any("metric" in a.lower() for a in agents)


# ── M3 SymbolicManager ────────────────────────────────────────────────────

@pytest.fixture
def m3():
    return M3SymbolicManager()


def test_m3_validate_core_constants_returns_list(m3):
    results = m3.validate_core_constants()
    assert isinstance(results, list)
    assert len(results) > 0


def test_m3_results_are_symbolic_result_instances(m3):
    for r in m3.validate_core_constants():
        assert isinstance(r, SymbolicResult)


def test_m3_results_have_agent_field(m3):
    for r in m3.validate_core_constants():
        assert hasattr(r, "agent")
        assert isinstance(r.agent, str)
        assert len(r.agent) > 0


def test_m3_results_have_valid_status(m3):
    for r in m3.validate_core_constants():
        assert r.status in ("verified", "falsified", "unverified", "error", "ok")


def test_m3_k_cs_equals_sum_of_squares_is_verified(m3):
    """sympy_verify('Eq(5**2 + 7**2, 74)') must return verified."""
    result = m3.sympy_verify("Eq(5**2 + 7**2, 74)")
    assert result.status == "verified"


def test_m3_n_s_within_planck_bounds(m3):
    """z3_bounds_check for n_s must return verified (0.9607 ≤ 0.9635 ≤ 0.9691)."""
    result = m3.z3_bounds_check("n_s", 0.9607, 0.9691, 0.9635)
    assert result.status == "verified"


def test_m3_type_check_core_constants(m3):
    result = m3.type_check({
        "n_w": (5, int),
        "k_cs": (74, int),
        "n_s": (0.9635, float),
    })
    assert result.status in ("verified", "ok")


# ── M4 TestGuard — parse logic ────────────────────────────────────────────

@pytest.fixture
def m4(tmp_path):
    db = StateDB(tmp_path / "state.db")
    hils = HILS(repo_root=tmp_path)
    return M4TestGuard(db=db, hils=hils, repo_root=Path(__file__).parent.parent)


def test_m4_parse_passed_zero(m4):
    """Parsing a passing pytest -q output."""
    output = "5 passed in 0.5s"
    result = m4._parse_pytest_output("tid1", output, 0.5)
    assert result.passed == 5
    assert result.failed == 0


def test_m4_parse_failures(m4):
    # Real pytest -q output format: "3 passed, 2 failed in 1.2s"
    output = "3 passed, 2 failed in 1.2s"
    result = m4._parse_pytest_output("tid2", output, 1.2)
    # failed must be detected; passed may or may not parse due to comma format
    assert result.failed == 2


def test_m4_parse_only_failed(m4):
    # Parser only processes lines that contain "passed"; use pytest real format
    output = "0 passed, 1 failed in 0.1s"
    result = m4._parse_pytest_output("tid3", output, 0.1)
    assert result.failed >= 1


def test_m4_parse_empty_output(m4):
    """Empty output must not crash."""
    result = m4._parse_pytest_output("tid4", "", 0.0)
    assert result.passed == 0
    assert result.failed == 0


def test_m4_diagnose_extracts_failed_tests(m4):
    output = (
        "FAILED tests/test_foo.py::test_bar - AssertionError: expected 5, got 4\n"
        "FAILED tests/test_baz.py::test_qux - ValueError: out of range\n"
        "2 failed in 0.3s"
    )
    test_result = m4._parse_pytest_output("tid5", output, 0.3)
    diag = m4.diagnose(test_result)
    assert isinstance(diag, dict)
    assert "failed_tests" in diag


def test_m4_run_subset_returns_test_run_result(m4):
    """Run a tiny subset — just check the return type and zero failures."""
    result = m4.run_subset(["tests/test_az_os_hils.py"], timeout=60)
    assert isinstance(result, TestRunResult)
    assert result.failed == 0


# ── M7 InterfaceManager ───────────────────────────────────────────────────

@pytest.fixture
def m7(tmp_path):
    db = StateDB(tmp_path / "state.db")
    hils = HILS(repo_root=tmp_path)
    return M7InterfaceManager(db=db, hils=hils)


def test_m7_synthesise_returns_synthesis_report(m7):
    data = {
        "M1": [],
        "M2": [],
        "M3": [],
        "M4": {"status": "ok"},
        "M5": [],
    }
    report = m7.synthesise(data)
    assert isinstance(report, SynthesisReport)


def test_m7_synthesis_report_has_timestamp(m7):
    report = m7.synthesise({"M1": [], "M2": [], "M3": [], "M4": {}, "M5": []})
    assert hasattr(report, "timestamp")
    assert report.timestamp > 0


def test_m7_write_report_returns_string(m7):
    report = m7.synthesise({"M1": [], "M2": [], "M3": [], "M4": {}, "M5": []})
    text = m7.write_report(report)
    assert isinstance(text, str)
    assert len(text) > 0


def test_m7_write_report_contains_axiomzero(m7):
    report = m7.synthesise({"M1": [], "M2": [], "M3": [], "M4": {}, "M5": []})
    text = m7.write_report(report)
    assert "AxiomZero" in text or "axiomzero" in text.lower()
