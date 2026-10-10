# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_formal_verification_library import (
    Z3_AVAILABLE,
    require_z3,
    SafetyProperty,
    run_property,
    run_suite,
    PENTAD_SAFETY_PROPERTIES,
)

pytestmark = pytest.mark.skipif(not Z3_AVAILABLE, reason="z3-solver not installed in this environment")


def test_require_z3_does_not_raise_when_available():
    require_z3()


def test_pentad_example_has_four_properties():
    assert len(PENTAD_SAFETY_PROPERTIES) == 4
    names = {p.name for p in PENTAD_SAFETY_PROPERTIES}
    assert names == {"trust_stability", "no_deadlock", "cs_bound", "xi_c_rational"}


def test_run_suite_all_pentad_properties_pass():
    summary = run_suite(PENTAD_SAFETY_PROPERTIES)
    assert summary["all_passed"] is True
    assert summary["n_total"] == 4
    assert summary["n_fail"] == 0


def test_run_property_trust_stability_matches_canonical_checker():
    from src.core.z3_pentad_checker import check_trust_stability

    canonical = check_trust_stability()
    prop = next(p for p in PENTAD_SAFETY_PROPERTIES if p.name == "trust_stability")
    generic = run_property(prop)
    assert generic.status == canonical["status"]


def test_run_property_cs_bound_matches_canonical_checker():
    from src.core.z3_pentad_checker import check_cs_bound

    canonical = check_cs_bound()
    prop = next(p for p in PENTAD_SAFETY_PROPERTIES if p.name == "cs_bound")
    generic = run_property(prop)
    assert generic.status == canonical["status"]


def test_run_property_xi_c_rational_matches_canonical_checker():
    from src.core.z3_pentad_checker import check_xi_c_rational

    canonical = check_xi_c_rational()
    prop = next(p for p in PENTAD_SAFETY_PROPERTIES if p.name == "xi_c_rational")
    generic = run_property(prop)
    assert generic.status == canonical["status"]


def test_run_property_no_deadlock_matches_canonical_checker():
    from src.core.z3_pentad_checker import check_no_deadlock

    canonical = check_no_deadlock()
    prop = next(p for p in PENTAD_SAFETY_PROPERTIES if p.name == "no_deadlock")
    generic = run_property(prop)
    assert generic.status == canonical["status"]


def test_custom_safety_property_fail_case():
    import z3

    def bad_constraints():
        solver = z3.Solver()
        x = z3.Real("x")
        solver.add(x > 0)
        solver.add(x < 0)
        return solver, True  # expect sat, but this is unsatisfiable -> FAIL

    prop = SafetyProperty("impossible", bad_constraints, "x > 0 and x < 0")
    result = run_property(prop)
    assert result.status == "FAIL"
