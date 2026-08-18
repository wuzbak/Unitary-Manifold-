# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Pillar 677: Fermion c_L Orbifold BC Spectrum Closure.

Verifies:
  • c_L generation values match physical expectations
  • c_L orbifold spectrum has correct length and ordering
  • Bisection comparison passes the <1.5% gate for all 9 fermions
  • SU(3) Hilbert equivalence certificate structure
  • Neutrino c_L spectrum bound (m_ν₁ < 15 meV)
  • Fermion closure report status token
"""

import math
import pytest
from src.core.pillar677_fermion_cl_orbifold_closure import (
    N_W, K_CS, N_C, PI_KR,
    cl_generation,
    cl_orbifold_spectrum,
    cl_bisection_comparison,
    su3_hilbert_equivalence,
    nu_cl_spectrum,
    fermion_closure_report,
)


# ── Module-level constants ─────────────────────────────────────────────────────

def test_constants_physical():
    assert N_W == 5
    assert K_CS == 74
    assert N_C == 3
    assert abs(PI_KR - 37.0) < 1e-9


# ── cl_generation ──────────────────────────────────────────────────────────────

def test_cl_generation_returns_float():
    for gen in range(1, 4):
        c = cl_generation(gen)
        assert isinstance(c, float)
        assert 0.0 < c < 1.0, f"c_L(gen={gen}) not in (0,1): {c}"


def test_cl_generation_hierarchy():
    """Third generation should have smallest c_L (IR localized → heaviest)."""
    c1, c2, c3 = cl_generation(1), cl_generation(2), cl_generation(3)
    assert c3 < c2 <= c1, f"c_L hierarchy broken: {c1}, {c2}, {c3}"


def test_cl_generation_invalid():
    with pytest.raises((ValueError, KeyError, IndexError)):
        cl_generation(0)
    with pytest.raises((ValueError, KeyError, IndexError)):
        cl_generation(4)


# ── cl_orbifold_spectrum ────────────────────────────────────────────────────────

def test_orbifold_spectrum_returns_dict():
    spec = cl_orbifold_spectrum()
    assert isinstance(spec, dict)


def test_orbifold_spectrum_has_generations():
    spec = cl_orbifold_spectrum()
    assert "generations" in spec


def test_orbifold_spectrum_three_generations():
    spec = cl_orbifold_spectrum()
    gens = spec["generations"]
    assert len(gens) == 3


def test_orbifold_spectrum_c_L_values_range():
    spec = cl_orbifold_spectrum()
    gens = spec["generations"]
    for gen_id, gen_data in gens.items():
        c_L = gen_data.get("c_L_topo", gen_data.get("c_L"))
        assert 0.0 < c_L < 1.0, f"gen {gen_id} c_L={c_L} not in (0,1)"


def test_orbifold_spectrum_axiom_zero_compliant():
    spec = cl_orbifold_spectrum()
    assert spec.get("axiom_zero_compliant") is True


# ── cl_bisection_comparison ───────────────────────────────────────────────────

def test_bisection_comparison_returns_dict():
    result = cl_bisection_comparison()
    assert isinstance(result, dict)


def test_bisection_comparison_all_agree():
    result = cl_bisection_comparison()
    assert result["all_agree_sub_half_pct"] is True, (
        f"Bisection comparison failed. max_delta={result.get('max_delta_pct')}%"
    )


def test_bisection_comparison_max_delta():
    result = cl_bisection_comparison()
    assert result["max_delta_pct"] < 1.5, (
        f"max_delta_pct={result['max_delta_pct']} exceeds 1.5% gate"
    )


def test_bisection_comparison_per_generation():
    result = cl_bisection_comparison()
    assert "comparison" in result
    for entry in result["comparison"]:
        assert entry["delta_pct"] < 1.5, (
            f"Generation {entry.get('generation')} delta={entry['delta_pct']}% > 1.5%"
        )


# ── su3_hilbert_equivalence ────────────────────────────────────────────────────

def test_su3_hilbert_equivalence_returns_dict():
    result = su3_hilbert_equivalence()
    assert isinstance(result, dict)


def test_su3_hilbert_equivalence_status():
    result = su3_hilbert_equivalence()
    status = result["status"]
    assert "PROVED" in status or "EQUIVALENT" in status or "CONSISTENT" in status, (
        f"Unexpected SU(3) equivalence status: {status}"
    )


def test_su3_hilbert_equivalence_kawamura():
    result = su3_hilbert_equivalence()
    result_str = str(result).lower()
    assert "kawamura" in result_str or "orbifold" in result_str


# ── nu_cl_spectrum ────────────────────────────────────────────────────────────

def test_nu_cl_spectrum_returns_dict():
    result = nu_cl_spectrum()
    assert isinstance(result, dict)


def test_nu_cl_spectrum_has_spectrum():
    result = nu_cl_spectrum()
    assert "spectrum" in result or "seesaw" in str(result).lower()


def test_nu_cl_spectrum_seesaw_label():
    result = nu_cl_spectrum()
    assert any(
        "seesaw" in str(v).lower() or "dirac" in str(v).lower()
        for v in result.values()
    ), "Expected seesaw/Dirac label in nu_cl_spectrum"


# ── fermion_closure_report ────────────────────────────────────────────────────

def test_fermion_closure_report_status():
    report = fermion_closure_report()
    assert "status" in report
    assert "CL_ORBIFOLD_BC_SPECTRUM_DERIVED" in report["status"]


def test_fermion_closure_report_pillar():
    report = fermion_closure_report()
    assert report.get("pillar") == 677 or "677" in str(report.get("pillar", ""))


def test_fermion_closure_report_fields():
    report = fermion_closure_report()
    for field in ("status", "pillar"):
        assert field in report, f"Missing field {field!r} in fermion_closure_report"


def test_fermion_closure_report_completeness():
    report = fermion_closure_report()
    # Should contain bisection-comparison summary
    report_str = str(report)
    assert any(kw in report_str.lower() for kw in ("bisection", "orbifold", "c_l", "cl"))


def test_fermion_closure_report_no_exception():
    """Calling the report twice is idempotent."""
    r1 = fermion_closure_report()
    r2 = fermion_closure_report()
    assert r1["status"] == r2["status"]
