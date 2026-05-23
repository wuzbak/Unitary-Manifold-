# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar382_quadrupole_topology_framework.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar382_quadrupole_topology_framework import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    D_H_MPC, L_HUBBLE_MPC, ELL_QUADRUPOLE, QUADRUPOLE_DEFICIT_FRACTION,
    separation_guard,
    l_min_torus,
    l_min_half_turn_space,
    l_min_poincare_dodecahedron,
    l_min_hyperbolic,
    compact_manifold_catalogue,
    um_geometry_topology_constraint,
    quadrupole_suppression_condition,
    topology_verdict,
    pillar382_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 382
    def test_status(self): assert PILLAR_STATUS == "POSSIBLE_CANDIDATE_SPECIFIED"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_d_h_mpc_positive(self): assert D_H_MPC > 0
    def test_ell_quadrupole(self): assert ELL_QUADRUPOLE == 2
    def test_quadrupole_deficit(self): assert 0 < QUADRUPOLE_DEFICIT_FRACTION < 1


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_possible_candidate(self): assert "POSSIBLE_CANDIDATE" in separation_guard()


class TestLMinTorus:
    def test_returns_dict(self):
        assert isinstance(l_min_torus(1.0 * D_H_MPC), dict)

    def test_k_min_positive(self):
        r = l_min_torus(1.0 * D_H_MPC)
        assert r["k_min_mpc"] > 0

    def test_ell_min_positive(self):
        r = l_min_torus(1.0 * D_H_MPC)
        assert r["ell_min"] > 0

    def test_suppresses_quadrupole_large_l(self):
        # L_fd >> L_Hubble → suppresses quadrupole (ℓ_min < 2)
        r = l_min_torus(10.0 * D_H_MPC)
        assert r["suppresses_quadrupole"] is True

    def test_no_suppression_small_l(self):
        # L_fd << L_Hubble → does NOT suppress quadrupole
        r = l_min_torus(0.1 * D_H_MPC)
        assert r["suppresses_quadrupole"] is False

    def test_um_compatible(self):
        r = l_min_torus(D_H_MPC)
        assert r["um_compatible"] is True

    def test_l_min_required_correct(self):
        r = l_min_torus(D_H_MPC)
        assert abs(r["l_min_required_mpc"] - math.pi * D_H_MPC) < 1.0

    def test_invalid_l(self):
        with pytest.raises(ValueError):
            l_min_torus(0.0)

    def test_ell_min_formula(self):
        L = 2.0 * D_H_MPC
        r = l_min_torus(L)
        expected_ell_min = 2.0 * math.pi / L * D_H_MPC
        assert abs(r["ell_min"] - expected_ell_min) < 0.01


class TestLMinHalfTurnSpace:
    def test_returns_dict(self):
        assert isinstance(l_min_half_turn_space(D_H_MPC), dict)

    def test_ell_min_positive(self):
        r = l_min_half_turn_space(D_H_MPC)
        assert r["ell_min"] > 0

    def test_suppresses_quadrupole_large_l(self):
        r = l_min_half_turn_space(5.0 * D_H_MPC)
        assert r["suppresses_quadrupole"] is True

    def test_um_compatible(self):
        r = l_min_half_turn_space(D_H_MPC)
        assert r["um_compatible"] is True

    def test_z2_compatibility(self):
        r = l_min_half_turn_space(D_H_MPC)
        assert "Z₂" in r["z2_compatibility"] or "Z2" in r["z2_compatibility"]

    def test_ell_min_greater_than_torus(self):
        # Half-turn space has smaller k_min → larger ell_min for same L
        r_t3 = l_min_torus(D_H_MPC)
        r_hw = l_min_half_turn_space(D_H_MPC)
        assert r_hw["ell_min"] < r_t3["ell_min"]  # π vs 2π → smaller ell_min

    def test_invalid_l(self):
        with pytest.raises(ValueError):
            l_min_half_turn_space(-1.0)


class TestLMinPoincareDohecahedron:
    def test_returns_dict(self):
        assert isinstance(l_min_poincare_dodecahedron(), dict)

    def test_ell_min_positive(self):
        r = l_min_poincare_dodecahedron()
        assert r["ell_min"] > 0

    def test_um_compatible_false(self):
        r = l_min_poincare_dodecahedron()
        assert r["um_compatible"] is False

    def test_less_favored(self):
        r = l_min_poincare_dodecahedron()
        assert "LESS_FAVORED" in r["verdict"]

    def test_reference_luminet(self):
        r = l_min_poincare_dodecahedron()
        assert "Luminet" in r["reference"]


class TestLMinHyperbolic:
    def test_returns_dict(self):
        assert isinstance(l_min_hyperbolic(D_H_MPC), dict)

    def test_ell_min_positive(self):
        r = l_min_hyperbolic(D_H_MPC)
        assert r["ell_min"] > 0

    def test_um_compatible_false(self):
        r = l_min_hyperbolic(D_H_MPC)
        assert r["um_compatible"] is False

    def test_less_favored(self):
        r = l_min_hyperbolic(D_H_MPC)
        assert "LESS_FAVORED" in r["verdict"]

    def test_invalid_l(self):
        with pytest.raises(ValueError):
            l_min_hyperbolic(0.0)


class TestCompactManifoldCatalogue:
    def test_returns_list(self):
        assert isinstance(compact_manifold_catalogue(), list)

    def test_five_entries(self):
        cat = compact_manifold_catalogue()
        assert len(cat) == 5

    def test_all_have_manifold_key(self):
        cat = compact_manifold_catalogue()
        for entry in cat:
            assert "manifold" in entry

    def test_has_torus(self):
        cat = compact_manifold_catalogue()
        manifolds = [c["manifold"] for c in cat]
        assert any("T3" in m or "torus" in m.lower() for m in manifolds)

    def test_has_poincare(self):
        cat = compact_manifold_catalogue()
        manifolds = [c["manifold"] for c in cat]
        assert any("Poincare" in m or "dodecahedron" in m.lower() for m in manifolds)

    def test_ell_min_positive(self):
        cat = compact_manifold_catalogue()
        for entry in cat:
            assert entry.get("ell_min", 1) > 0


class TestUMGeometryTopologyConstraint:
    def test_returns_dict(self): assert isinstance(um_geometry_topology_constraint(), dict)

    def test_no_constraint_on_m3(self):
        r = um_geometry_topology_constraint()
        assert "NONE" in r["um_constraint"]

    def test_not_derived(self):
        r = um_geometry_topology_constraint()
        assert "NOT_DERIVED" in r["status"]

    def test_required_extension_present(self):
        r = um_geometry_topology_constraint()
        assert "required_extension" in r
        assert len(r["required_extension"]) > 20

    def test_z2_compatibility_noted(self):
        r = um_geometry_topology_constraint()
        assert "z2_half_turn_compatibility" in r


class TestQuadrupoleSuppression:
    def test_returns_dict(self): assert isinstance(quadrupole_suppression_condition(), dict)

    def test_requirement_present(self):
        r = quadrupole_suppression_condition()
        assert "requirement" in r

    def test_t3_l_min_correct(self):
        r = quadrupole_suppression_condition()
        expected = math.pi * D_H_MPC
        assert abs(r["t3_L_min_mpc"] - expected) < 1.0

    def test_half_turn_l_min_half(self):
        r = quadrupole_suppression_condition()
        assert abs(r["half_turn_L_min_mpc"] - 0.5 * math.pi * D_H_MPC) < 1.0


class TestTopologyVerdict:
    def test_returns_dict(self): assert isinstance(topology_verdict(), dict)

    def test_new_status(self):
        r = topology_verdict()
        assert r["new_status"] == "POSSIBLE_CANDIDATE_SPECIFIED"

    def test_preferred_candidate(self):
        r = topology_verdict()
        assert "T³/Z₂" in r["preferred_candidate"] or "Z2" in r["preferred_candidate"]

    def test_falsifier_present(self):
        r = topology_verdict()
        assert "falsifier" in r

    def test_honest_caveat(self):
        r = topology_verdict()
        assert "honest_caveat" in r
        assert "extension" in r["honest_caveat"].lower()


class TestPillar382Summary:
    def test_returns_dict(self): assert isinstance(pillar382_summary(), dict)
    def test_pillar_number(self):
        r = pillar382_summary()
        assert r["pillar_number"] == PILLAR_NUMBER
    def test_status(self):
        r = pillar382_summary()
        assert r["status"] == "POSSIBLE_CANDIDATE_SPECIFIED"
    def test_key_result(self):
        r = pillar382_summary()
        assert "key_result" in r
        assert "T³" in r["key_result"] or "T3" in r["key_result"]
    def test_previous_status(self):
        r = pillar382_summary()
        assert r["previous_status"] == "MECHANISM_INCONCLUSIVE"
    def test_new_status(self):
        r = pillar382_summary()
        assert r["new_status"] == "POSSIBLE_CANDIDATE_SPECIFIED"
