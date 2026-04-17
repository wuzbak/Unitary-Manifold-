# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_safety_imports.py
============================
Smoke tests for the SAFETY/ module suite.

These tests verify that each safety module:
  1. Imports without error.
  2. Exposes its documented public API (classes / exceptions / functions).
  3. Instantiates its primary class with default parameters.
  4. Runs a basic check_raw / check_rho call and returns the expected status.

They do NOT test physical correctness — that is covered by the unit tests of
the underlying src/ modules.  The purpose here is to ensure the safety
infrastructure is importable and functional in CI (SAF-01, SAF-02, SAF-03).
"""

import importlib
import sys
import os

import pytest

# ---------------------------------------------------------------------------
# Ensure repository root is on the path (mirrors what each SAFETY module does)
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


# ===========================================================================
# SAF-01 — AdmissibilityChecker (SAFETY/admissibility_checker.py)
# ===========================================================================

class TestAdmissibilityChecker:
    """SAF-01: SAFETY/admissibility_checker.py imports and runs correctly."""

    def test_module_imports(self):
        """Module can be imported without error."""
        mod = importlib.import_module("SAFETY.admissibility_checker")
        assert mod is not None

    def test_public_api_present(self):
        """Public API symbols are all present."""
        from SAFETY.admissibility_checker import (
            AdmissibilityChecker,
            AdmissibilityReport,
            PentagonalCollapseError,
            Z_MAX_DEFAULT,
            H_MAX_DEFAULT,
            GRAD_MAX_DEFAULT,
            PHI_FLOOR_DEFAULT,
            DET_TOL_DEFAULT,
        )
        assert AdmissibilityChecker is not None
        assert AdmissibilityReport is not None
        assert issubclass(PentagonalCollapseError, RuntimeError)
        assert Z_MAX_DEFAULT > 0
        assert H_MAX_DEFAULT > 0
        assert PHI_FLOOR_DEFAULT > 0

    def test_default_instantiation(self):
        """AdmissibilityChecker() instantiates with default parameters."""
        from SAFETY.admissibility_checker import AdmissibilityChecker
        checker = AdmissibilityChecker()
        assert checker.z_max == 10.0
        assert checker.h_max == 5.0
        assert checker.phi_floor == 1e-3

    def test_check_raw_ok_state(self):
        """check_raw returns OK status for a well-behaved field state."""
        from SAFETY.admissibility_checker import AdmissibilityChecker
        checker = AdmissibilityChecker()
        report = checker.check_raw(
            R=1.0,       # |R|  << Z_max * phi^2
            phi=1.0,     # phi  >> phi_floor
            H_norm=0.5,  # H_norm << H_max
            grad_phi=0.5,
            det_g_dev=0.01,
        )
        assert report.status == "OK"
        assert report.is_admissible
        assert report.z_proxy == pytest.approx(1.0, rel=1e-6)

    def test_check_raw_raises_on_collapse(self):
        """check_raw raises PentagonalCollapseError when Z_proxy exceeds Z_max."""
        from SAFETY.admissibility_checker import (
            AdmissibilityChecker,
            PentagonalCollapseError,
        )
        checker = AdmissibilityChecker()
        with pytest.raises(PentagonalCollapseError) as exc_info:
            checker.check_raw(
                R=1000.0,    # huge: Z_proxy >> Z_max
                phi=1.0,
                H_norm=0.5,
                grad_phi=0.5,
                det_g_dev=0.01,
            )
        err = exc_info.value
        assert "curvature_proxy" in err.violated_edges
        assert err.report.status == "SHUTDOWN"

    def test_check_raw_warning_region(self):
        """check_raw returns WARNING when approaching (but not at) a limit."""
        from SAFETY.admissibility_checker import AdmissibilityChecker
        checker = AdmissibilityChecker(z_max=10.0, warn_fraction=0.8)
        # Z_proxy = 9.5 / 1.0^2 = 9.5 > 0.8 * 10.0 = 8.0  → WARNING
        report = checker.check_raw(
            R=9.5,
            phi=1.0,
            H_norm=0.5,
            grad_phi=0.5,
            det_g_dev=0.01,
        )
        assert report.status == "WARNING"
        assert report.is_admissible

    def test_phi_floor_violation(self):
        """check_raw raises when phi < phi_floor."""
        from SAFETY.admissibility_checker import (
            AdmissibilityChecker,
            PentagonalCollapseError,
        )
        checker = AdmissibilityChecker()
        with pytest.raises(PentagonalCollapseError) as exc_info:
            checker.check_raw(
                R=0.001,
                phi=1e-6,    # << phi_floor = 1e-3
                H_norm=0.1,
                grad_phi=0.1,
                det_g_dev=0.01,
            )
        assert "phi_floor" in exc_info.value.violated_edges

    def test_admissibility_report_dataclass(self):
        """AdmissibilityReport.is_admissible works correctly."""
        from SAFETY.admissibility_checker import AdmissibilityReport
        ok_report = AdmissibilityReport(
            z_proxy=1.0, h_norm=0.5, grad_phi=0.5,
            phi_min=1.0, det_g_dev=0.01,
            edges={k: True for k in
                   ["curvature_proxy", "field_strength", "gradient",
                    "phi_floor", "volume_preservation"]},
            status="OK", message="OK",
        )
        assert ok_report.is_admissible

        fail_report = AdmissibilityReport(
            z_proxy=100.0, h_norm=0.5, grad_phi=0.5,
            phi_min=1.0, det_g_dev=0.01,
            edges={"curvature_proxy": False, "field_strength": True,
                   "gradient": True, "phi_floor": True,
                   "volume_preservation": True},
            status="SHUTDOWN", message="collapsed",
        )
        assert not fail_report.is_admissible


# ===========================================================================
# SAF-02 — UnitaritySentinel (SAFETY/unitarity_sentinel.py)
# ===========================================================================

class TestUnitaritySentinel:
    """SAF-02: SAFETY/unitarity_sentinel.py imports and runs correctly."""

    def test_module_imports(self):
        """Module can be imported without error."""
        mod = importlib.import_module("SAFETY.unitarity_sentinel")
        assert mod is not None

    def test_public_api_present(self):
        """Public API symbols are all present."""
        from SAFETY.unitarity_sentinel import (
            UnitaritySentinel,
            SentinelReport,
            GeometricShutdownError,
            monitor_evolution,
            N1_CANONICAL,
            N2_CANONICAL,
            K_CS_CANONICAL,
            RHO_CANONICAL,
            RHO_LIMIT_DEFAULT,
            PHI_MIN_DEFAULT,
        )
        assert UnitaritySentinel is not None
        assert SentinelReport is not None
        assert issubclass(GeometricShutdownError, RuntimeError)
        assert N1_CANONICAL == 5
        assert N2_CANONICAL == 7
        assert K_CS_CANONICAL == 74
        assert RHO_CANONICAL == pytest.approx(70 / 74, rel=1e-6)

    def test_default_instantiation(self):
        """UnitaritySentinel() instantiates with canonical defaults."""
        from SAFETY.unitarity_sentinel import UnitaritySentinel, RHO_LIMIT_DEFAULT
        sentinel = UnitaritySentinel()
        assert sentinel.n1 == 5
        assert sentinel.n2 == 7
        assert sentinel.k_cs == 74
        assert sentinel.rho_limit == pytest.approx(RHO_LIMIT_DEFAULT, rel=1e-6)

    def test_check_rho_ok_at_canonical(self):
        """check_rho returns OK for the canonical ρ = 70/74 ≈ 0.9459."""
        from SAFETY.unitarity_sentinel import UnitaritySentinel, RHO_CANONICAL
        sentinel = UnitaritySentinel()
        report = sentinel.check_rho(RHO_CANONICAL)
        assert report.is_safe
        assert report.status in ("OK", "WARNING")
        assert report.rho == pytest.approx(RHO_CANONICAL, rel=1e-6)
        assert report.c_s > 0.0

    def test_check_rho_raises_at_limit(self):
        """check_rho raises GeometricShutdownError when |ρ| ≥ rho_limit."""
        from SAFETY.unitarity_sentinel import (
            UnitaritySentinel,
            GeometricShutdownError,
        )
        sentinel = UnitaritySentinel(rho_limit=0.95)
        with pytest.raises(GeometricShutdownError) as exc_info:
            sentinel.check_rho(0.96)
        err = exc_info.value
        assert err.rho == pytest.approx(0.96, rel=1e-6)
        assert err.c_s >= 0.0

    def test_sentinel_report_is_safe_property(self):
        """SentinelReport.is_safe returns False only on SHUTDOWN."""
        from SAFETY.unitarity_sentinel import SentinelReport
        ok = SentinelReport(rho=0.9, c_s=0.4, phi_min=1.0, status="OK", message="ok")
        warn = SentinelReport(rho=0.94, c_s=0.3, phi_min=1.0, status="WARNING", message="warn")
        shut = SentinelReport(rho=0.96, c_s=0.1, phi_min=None, status="SHUTDOWN", message="stop")
        assert ok.is_safe
        assert warn.is_safe
        assert not shut.is_safe

    def test_rho_nominal_property(self):
        """sentinel.rho_nominal matches the canonical ρ = 70/74."""
        from SAFETY.unitarity_sentinel import UnitaritySentinel
        sentinel = UnitaritySentinel()
        assert sentinel.rho_nominal == pytest.approx(70 / 74, rel=1e-5)

    def test_margin_is_positive(self):
        """The safety margin rho_limit − rho_nominal is positive."""
        from SAFETY.unitarity_sentinel import UnitaritySentinel
        sentinel = UnitaritySentinel()
        assert sentinel.margin > 0.0


# ===========================================================================
# SAF-03 — ThermalRunawayGuard (SAFETY/thermal_runaway_mitigation.py)
# ===========================================================================

class TestThermalRunawayGuard:
    """SAF-03: SAFETY/thermal_runaway_mitigation.py imports and runs correctly."""

    def test_module_imports(self):
        """Module can be imported without error."""
        mod = importlib.import_module("SAFETY.thermal_runaway_mitigation")
        assert mod is not None

    def test_public_api_present(self):
        """Public API symbols are all present."""
        from SAFETY.thermal_runaway_mitigation import (
            ThermalRunawayGuard,
            ThermalRunawayReport,
            ThermalRunawayError,
            T_MAX_K_DEFAULT,
            T_5D_K_DEFAULT,
            X_MAX_DEFAULT,
            NEUTRON_FLUX_LIMIT_DEFAULT,
        )
        assert ThermalRunawayGuard is not None
        assert ThermalRunawayReport is not None
        assert issubclass(ThermalRunawayError, RuntimeError)
        assert T_MAX_K_DEFAULT > 0
        assert T_5D_K_DEFAULT > T_MAX_K_DEFAULT
        assert 0 < X_MAX_DEFAULT <= 1.0
        assert NEUTRON_FLUX_LIMIT_DEFAULT > 0

    def test_default_instantiation(self):
        """ThermalRunawayGuard() instantiates with default parameters."""
        from SAFETY.thermal_runaway_mitigation import (
            ThermalRunawayGuard,
            T_MAX_K_DEFAULT,
            T_5D_K_DEFAULT,
        )
        guard = ThermalRunawayGuard()
        assert guard.T_max_K == T_MAX_K_DEFAULT
        assert guard.T_5D_K == T_5D_K_DEFAULT

    def test_check_ok_at_safe_conditions(self):
        """check() returns OK status at room temperature with low loading."""
        from SAFETY.thermal_runaway_mitigation import ThermalRunawayGuard
        guard = ThermalRunawayGuard()
        report = guard.check(
            T_K=300.0,
            loading_ratio=0.5,
            phi_lattice=1.0,
            cop=2.0,
            reaction_rate=1.0,
        )
        assert report.is_safe
        assert report.status in ("OK", "WARNING")

    def test_check_raises_on_temperature_exceedance(self):
        """check() raises ThermalRunawayError (Layer 1) when T > T_max."""
        from SAFETY.thermal_runaway_mitigation import (
            ThermalRunawayGuard,
            ThermalRunawayError,
        )
        guard = ThermalRunawayGuard(T_max_K=400.0)
        with pytest.raises(ThermalRunawayError) as exc_info:
            guard.check(
                T_K=500.0,    # > T_max = 400 K
                loading_ratio=0.5,
                phi_lattice=1.0,
                cop=2.0,
                reaction_rate=1.0,
            )
        err = exc_info.value
        assert err.layer == 1
        assert err.T_K == pytest.approx(500.0, rel=1e-6)

    def test_check_raises_on_loading_exceedance(self):
        """check() raises ThermalRunawayError (Layer 3) when x > x_max."""
        from SAFETY.thermal_runaway_mitigation import (
            ThermalRunawayGuard,
            ThermalRunawayError,
        )
        guard = ThermalRunawayGuard(x_max=0.95)
        with pytest.raises(ThermalRunawayError) as exc_info:
            guard.check(
                T_K=300.0,
                loading_ratio=0.97,   # > x_max = 0.95
                phi_lattice=1.0,
                cop=2.0,
                reaction_rate=1.0,
            )
        err = exc_info.value
        assert err.layer == 3

    def test_thermal_runaway_report_is_safe(self):
        """ThermalRunawayReport.is_safe is False only on SHUTDOWN."""
        from SAFETY.thermal_runaway_mitigation import ThermalRunawayReport
        ok = ThermalRunawayReport(
            T_K=300.0, loading_ratio=0.5, phi_lattice=1.0,
            cop=2.0, neutron_flux=None, layer=None, status="OK", message="ok"
        )
        shut = ThermalRunawayReport(
            T_K=500.0, loading_ratio=0.5, phi_lattice=1.0,
            cop=2.0, neutron_flux=None, layer=1, status="SHUTDOWN", message="stop"
        )
        assert ok.is_safe
        assert not shut.is_safe
