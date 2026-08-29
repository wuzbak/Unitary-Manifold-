# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 827 — ADM/BSSN Non-linear Closure."""
from __future__ import annotations
import math
import pytest
from src.core.pillar827_adm_bssn_nonlinear_closure import (
    PILLAR, GATE_BSSN_HOMOGENEOUS, LEAN4_TOTAL, LEAN4_COUNT,
    bssn_homogeneous_evolve, hamiltonian_constraint_check, wdw_minisuperspace_action,
    wdw_wkb_wavefunction, bssn_radion_source_term, linearised_inhomogeneous_bound,
    adm_bssn_closure_report,
)


class TestPillar827Constants:
    def test_pillar_number(self): assert PILLAR == 827
    def test_gate_bssn(self): assert "BSSN" in GATE_BSSN_HOMOGENEOUS
    def test_lean4_count(self): assert LEAN4_COUNT == 40
    def test_lean4_total(self): assert LEAN4_TOTAL == 1581
    def test_lean4_accumulates(self):
        from src.core.pillar827_adm_bssn_nonlinear_closure import LEAN4_PRIOR
        assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT


class TestBssnHomogeneousEvolve:
    def test_gate_in_result(self):
        r = bssn_homogeneous_evolve()
        assert "BSSN" in r.gate or "ADM" in r.gate

    def test_phi_array_positive(self):
        r = bssn_homogeneous_evolve()
        assert all(v > 0 for v in r.phi_array)

    def test_t_array_increasing(self):
        r = bssn_homogeneous_evolve()
        assert r.t_array[-1] > r.t_array[0]

    def test_hamiltonian_violation_finite(self):
        r = bssn_homogeneous_evolve()
        assert math.isfinite(float(r.hamiltonian_violation_max))

    def test_final_phi_positive(self):
        r = bssn_homogeneous_evolve()
        assert r.final.phi > 0

    def test_final_chi_positive(self):
        r = bssn_homogeneous_evolve()
        assert r.final.chi > 0

    def test_custom_phi0(self):
        r = bssn_homogeneous_evolve(phi0=38.0)
        assert r.final.phi > 0


class TestHamiltonianConstraintCheck:
    def test_returns_dict(self):
        evol = bssn_homogeneous_evolve()
        r = hamiltonian_constraint_check(evol.final.chi, evol.final.K,
                                          evol.final.phi, evol.final.dphi_dt)
        assert isinstance(r, dict)

    def test_h_finite(self):
        evol = bssn_homogeneous_evolve()
        r = hamiltonian_constraint_check(evol.final.chi, evol.final.K,
                                          evol.final.phi, evol.final.dphi_dt)
        assert math.isfinite(r["H"])

    def test_is_satisfied_present(self):
        evol = bssn_homogeneous_evolve()
        r = hamiltonian_constraint_check(evol.final.chi, evol.final.K,
                                          evol.final.phi, evol.final.dphi_dt)
        assert "is_satisfied" in r


class TestWdwMinisuperspaceAction:
    def test_returns_dict(self):
        r = wdw_minisuperspace_action()
        assert isinstance(r, dict)

    def test_euclidean_action_positive(self):
        r = wdw_minisuperspace_action()
        val = r.get("S_euclidean", r.get("S_E", r.get("euclidean_action", 0)))
        assert val > 0

    def test_gate_closed(self):
        r = wdw_minisuperspace_action()
        assert any("CLOSED" in str(v) or "WDW" in str(v) or "BSSN" in str(v)
                   for v in r.values())


class TestWdwWkbWavefunction:
    def test_returns_dict(self):
        r = wdw_wkb_wavefunction(alpha=1.0)
        assert isinstance(r, dict)

    def test_has_content(self):
        r = wdw_wkb_wavefunction(alpha=1.0)
        assert len(r) > 0


class TestBssnRadionSourceTerm:
    def test_returns_dict(self):
        r = bssn_radion_source_term(37.0, 0.1)
        assert isinstance(r, dict)

    def test_has_fields(self):
        r = bssn_radion_source_term(37.0, 0.1)
        assert len(r) > 0


class TestLinearisedInhomogeneousBound:
    def test_returns_dict(self):
        r = linearised_inhomogeneous_bound()
        assert isinstance(r, dict)

    def test_has_content(self):
        r = linearised_inhomogeneous_bound()
        assert len(r) > 0


class TestAdmBssnClosureReport:
    def test_returns_dict(self):
        r = adm_bssn_closure_report()
        assert isinstance(r, dict)

    def test_pillar(self):
        r = adm_bssn_closure_report()
        assert r["pillar"] == 827

    def test_gates_present(self):
        r = adm_bssn_closure_report()
        assert "gates_closed" in r

    def test_lean4_present(self):
        r = adm_bssn_closure_report()
        assert r["lean4_total_after"] == 1581

    def test_open_items_honest(self):
        r = adm_bssn_closure_report()
        assert len(r["remaining_open"]) > 0

    def test_bssn_gate_in_list(self):
        r = adm_bssn_closure_report()
        assert any("BSSN" in g for g in r.get("gates_closed", []))
