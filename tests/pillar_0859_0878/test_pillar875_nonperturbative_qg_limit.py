# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 875 — irreducible non-perturbative quantum-gravity limit."""
from __future__ import annotations

from src.core.pillar875_nonperturbative_qg_limit import (
    ALL_IRREDUCIBLE,
    EXTERNAL_PROGRAMMES,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    LIMIT_CERTIFICATE,
    N_OBSTRUCTIONS,
    OBSTRUCTIONS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PROGRAMMES_DISTINCT,
    REMAINING_OPEN,
    is_reducible,
    nonperturbative_qg_limit_summary,
    obstruction_codes,
    required_programmes,
)


class TestPillar875Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 875
    def test_gate(self): assert PILLAR_GATE == "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT"
    def test_limit_certificate(self): assert LIMIT_CERTIFICATE == "IRREDUCIBLE_ARCHITECTURE_LIMIT"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 15
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2516
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2531
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER


class TestPillar875Obstructions:
    def test_obstruction_count(self): assert N_OBSTRUCTIONS == 4
    def test_obstructions_length(self): assert len(OBSTRUCTIONS) == N_OBSTRUCTIONS
    def test_codes(self):
        assert obstruction_codes() == [
            "O1_PERTURBATIVE_EFT_ONLY",
            "O2_NO_UV_MEASURE",
            "O3_NO_BACKGROUND_INDEPENDENCE",
            "O4_NO_TRANSPLANCKIAN_STATES",
        ]
    def test_codes_unique(self): assert len(set(obstruction_codes())) == N_OBSTRUCTIONS
    def test_every_obstruction_has_statement(self):
        assert all(entry["statement"] for entry in OBSTRUCTIONS)
    def test_statements_are_sentences(self):
        assert all(entry["statement"].endswith(".") for entry in OBSTRUCTIONS)
    def test_none_reducible(self): assert not any(is_reducible(e) for e in OBSTRUCTIONS)
    def test_is_reducible_positive_case(self):
        assert is_reducible({"reducible_within_framework": "yes"}) is True
    def test_all_irreducible_flag(self): assert ALL_IRREDUCIBLE is True


class TestPillar875Programmes:
    def test_programme_count(self): assert len(EXTERNAL_PROGRAMMES) == N_OBSTRUCTIONS
    def test_programmes_distinct(self): assert PROGRAMMES_DISTINCT is True
    def test_programmes_unique(self): assert len(set(EXTERNAL_PROGRAMMES)) == len(EXTERNAL_PROGRAMMES)
    def test_asymptotic_safety_present(self): assert "ASYMPTOTIC_SAFETY" in EXTERNAL_PROGRAMMES
    def test_lattice_qg_present(self): assert "LATTICE_QUANTUM_GRAVITY" in EXTERNAL_PROGRAMMES
    def test_lqg_present(self): assert "LOOP_QUANTUM_GRAVITY" in EXTERNAL_PROGRAMMES
    def test_string_uv_present(self):
        assert "STRING_M_THEORY_UV_COMPLETION" in EXTERNAL_PROGRAMMES
    def test_required_programmes_matches(self):
        assert required_programmes() == list(EXTERNAL_PROGRAMMES)
    def test_each_obstruction_maps_to_programme(self):
        assert all(entry["required_external_programme"] for entry in OBSTRUCTIONS)
    def test_no_programme_is_internal(self):
        assert all("UNITARY_MANIFOLD" not in p for p in EXTERNAL_PROGRAMMES)


class TestPillar875Summary:
    def test_summary_gate(self): assert nonperturbative_qg_limit_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert nonperturbative_qg_limit_summary()["pillar"] == 875
    def test_summary_lean4(self): assert nonperturbative_qg_limit_summary()["lean4_total_after"] == 2531
    def test_summary_certificate(self):
        assert nonperturbative_qg_limit_summary()["limit_certificate"] == LIMIT_CERTIFICATE
    def test_summary_all_irreducible(self):
        assert nonperturbative_qg_limit_summary()["all_irreducible"] is True
    def test_summary_obstruction_count(self):
        assert nonperturbative_qg_limit_summary()["n_obstructions"] == 4
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 1
    def test_epistemic_status_irreducible(self):
        assert "IRREDUCIBLE" in nonperturbative_qg_limit_summary()["epistemic_status"].upper()
    def test_no_closure_claim(self):
        assert "CLOSED" not in nonperturbative_qg_limit_summary()["epistemic_status"].upper()
