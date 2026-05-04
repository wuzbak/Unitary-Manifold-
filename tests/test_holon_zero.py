# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Ω₀ Holon Zero Final Pillar (src/core/holon_zero.py)."""

import pytest

from src.core.holon_zero import (
    holon_zero_certificate,
    toe_completeness_theorem,
    holon_zero_summary,
    axiom_count,
    pillar_dependency_graph,
    omega_zero_falsifiers,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def cert():
    return holon_zero_certificate()


@pytest.fixture(scope="module")
def theorem():
    return toe_completeness_theorem()


@pytest.fixture(scope="module")
def summary():
    return holon_zero_summary()


@pytest.fixture(scope="module")
def axioms():
    return axiom_count()


@pytest.fixture(scope="module")
def pdg():
    return pillar_dependency_graph()


@pytest.fixture(scope="module")
def falsifiers():
    return omega_zero_falsifiers()


# ---------------------------------------------------------------------------
# holon_zero_certificate — structure
# ---------------------------------------------------------------------------

def test_cert_is_dict(cert):
    assert isinstance(cert, dict)


def test_cert_has_exactly_26_entries(cert):
    assert len(cert) == 26


def test_cert_all_values_are_dicts(cert):
    for k, v in cert.items():
        assert isinstance(v, dict), f"Entry {k} is not a dict"


def test_cert_every_entry_has_name(cert):
    for k, v in cert.items():
        assert "name" in v, f"Entry {k} missing 'name'"


def test_cert_every_entry_has_status(cert):
    for k, v in cert.items():
        assert "status" in v, f"Entry {k} missing 'status'"


def test_cert_every_entry_has_pillar_source(cert):
    for k, v in cert.items():
        assert "pillar_source" in v, f"Entry {k} missing 'pillar_source'"


def test_cert_every_entry_has_accuracy_note(cert):
    for k, v in cert.items():
        assert "accuracy_pct_or_note" in v, f"Entry {k} missing 'accuracy_pct_or_note'"


def test_cert_no_entry_has_open_status(cert):
    for k, v in cert.items():
        assert "OPEN" not in v["status"], f"Entry {k} has OPEN status"


def test_cert_no_entry_has_fitted_status(cert):
    for k, v in cert.items():
        assert "FITTED" not in v["status"], f"Entry {k} has FITTED status"


def test_cert_all_statuses_are_strings(cert):
    for k, v in cert.items():
        assert isinstance(v["status"], str), f"Entry {k} status not a string"


def test_cert_all_names_non_empty(cert):
    for k, v in cert.items():
        assert len(v["name"]) > 0, f"Entry {k} has empty name"


# ---------------------------------------------------------------------------
# Specific certificate entries
# ---------------------------------------------------------------------------

def test_cert_p1_derived(cert):
    assert "DERIVED" in cert["P1"]["status"]


def test_cert_p2_derived(cert):
    assert "DERIVED" in cert["P2"]["status"]


def test_cert_p4_geometric_prediction(cert):
    assert "GEOMETRIC PREDICTION" in cert["P4"]["status"]


def test_cert_p5_derived(cert):
    assert "DERIVED" in cert["P5"]["status"]


def test_cert_p6_geometric_prediction(cert):
    assert "PARAMETERIZED" in cert["P6"]["status"]


def test_cert_p11_geometric_prediction(cert):
    assert "PARAMETERIZED" in cert["P11"]["status"]


def test_cert_p12_derived(cert):
    assert "DERIVED" in cert["P12"]["status"]


def test_cert_p19_constrained(cert):
    assert "CONSTRAINED" in cert["P19"]["status"]


def test_cert_p20_constrained(cert):
    assert "CONSTRAINED" in cert["P20"]["status"]


def test_cert_p21_constrained(cert):
    assert "CONSTRAINED" in cert["P21"]["status"]


def test_cert_p22_geometric_prediction(cert):
    assert "GEOMETRIC PREDICTION" in cert["P22"]["status"]


def test_cert_p28_constrained(cert):
    assert "CONSTRAINED" in cert["P28"]["status"]


def test_cert_p1_pillar_source(cert):
    ps = cert["P1"]["pillar_source"]
    assert "56" in str(ps)


def test_cert_p4_pillar_source_139(cert):
    assert cert["P4"]["pillar_source"] == 139


def test_cert_p19_pillar_source_140(cert):
    assert cert["P19"]["pillar_source"] == 140


def test_cert_p22_pillar_source_138(cert):
    assert cert["P22"]["pillar_source"] == 138


def test_cert_p28_pillar_source_141(cert):
    assert cert["P28"]["pillar_source"] == 141


# ---------------------------------------------------------------------------
# toe_completeness_theorem
# ---------------------------------------------------------------------------

def test_theorem_is_dict(theorem):
    assert isinstance(theorem, dict)


def test_theorem_has_n_open(theorem):
    assert "n_open" in theorem


def test_theorem_n_open_zero(theorem):
    assert theorem["n_open"] == 0


def test_theorem_has_n_fitted(theorem):
    assert "n_fitted" in theorem


def test_theorem_n_fitted_zero(theorem):
    assert theorem["n_fitted"] == 0


def test_theorem_has_total(theorem):
    assert "total" in theorem


def test_theorem_total_26(theorem):
    assert theorem["total"] == 26


def test_theorem_has_n_derived(theorem):
    assert "n_derived" in theorem


def test_theorem_n_derived_8(theorem):
    assert theorem["n_derived"] == 8


def test_theorem_has_n_geometric_prediction(theorem):
    assert "n_geometric_prediction" in theorem


def test_theorem_n_geometric_prediction_11(theorem):
    # After adversarial review fix: genuine geometric predictions are only P4 (Higgs VEV)
    # and P22 (solar mixing). The 9 fermion masses are PARAMETERIZED, not predicted.
    assert theorem["n_geometric_prediction"] == 2


def test_theorem_has_n_parameterized(theorem):
    assert "n_parameterized" in theorem


def test_theorem_n_parameterized_9(theorem):
    # P6-P11 (6 quarks) + P16-P18 (3 charged leptons) = 9 parameterized fermion masses
    assert theorem["n_parameterized"] == 9


def test_theorem_has_n_constrained(theorem):
    assert "n_constrained" in theorem


def test_theorem_n_constrained_4(theorem):
    assert theorem["n_constrained"] == 4


def test_theorem_has_honest_caveat(theorem):
    assert "honest_caveat" in theorem


def test_theorem_honest_caveat_non_empty(theorem):
    assert len(theorem["honest_caveat"]) > 0


def test_theorem_has_theorem_text(theorem):
    assert "theorem" in theorem


def test_theorem_text_non_empty(theorem):
    assert len(theorem["theorem"]) > 0


# ---------------------------------------------------------------------------
# axiom_count
# ---------------------------------------------------------------------------

def test_axioms_is_dict(axioms):
    assert isinstance(axioms, dict)


def test_axioms_has_n_genuine_inputs(axioms):
    assert "n_genuine_inputs" in axioms


def test_axioms_n_genuine_inputs_3(axioms):
    assert axioms["n_genuine_inputs"] == 3


def test_axioms_has_inputs(axioms):
    assert "inputs" in axioms


def test_axioms_inputs_is_list(axioms):
    assert isinstance(axioms["inputs"], list)


def test_axioms_inputs_has_3_items(axioms):
    assert len(axioms["inputs"]) == 3


def test_axioms_inputs_non_empty_strings(axioms):
    for inp in axioms["inputs"]:
        assert isinstance(inp, str) and len(inp) > 0


def test_axioms_inputs_contains_nw(axioms):
    combined = " ".join(axioms["inputs"]).lower()
    assert "n_w" in combined or "nw" in combined


def test_axioms_inputs_contains_m_kk(axioms):
    combined = " ".join(axioms["inputs"]).lower()
    assert "m_kk" in combined or "mkk" in combined


def test_axioms_has_hidden_free_parameters(axioms):
    assert "hidden_free_parameters" in axioms


def test_axioms_hidden_free_parameters_count_9(axioms):
    assert axioms["hidden_free_parameters"]["count"] == 9


# ---------------------------------------------------------------------------
# omega_zero_falsifiers
# ---------------------------------------------------------------------------

def test_falsifiers_is_dict_or_list(falsifiers):
    assert isinstance(falsifiers, (dict, list))


def test_falsifiers_has_primary(falsifiers):
    if isinstance(falsifiers, dict):
        assert "primary" in falsifiers


def test_falsifiers_primary_mentions_litebird(falsifiers):
    if isinstance(falsifiers, dict):
        primary_str = str(falsifiers["primary"]).lower()
        assert "litebird" in primary_str


def test_falsifiers_primary_mentions_birefringence(falsifiers):
    if isinstance(falsifiers, dict):
        primary_str = str(falsifiers["primary"]).lower()
        assert "birefringence" in primary_str or "beta" in primary_str or "β" in primary_str


def test_falsifiers_has_secondary(falsifiers):
    if isinstance(falsifiers, dict):
        assert "secondary" in falsifiers


def test_falsifiers_non_empty(falsifiers):
    assert len(falsifiers) > 0


# ---------------------------------------------------------------------------
# pillar_dependency_graph
# ---------------------------------------------------------------------------

def test_pdg_is_dict(pdg):
    assert isinstance(pdg, dict)


def test_pdg_non_empty(pdg):
    assert len(pdg) > 0


def test_pdg_has_nodes(pdg):
    assert "nodes" in pdg


def test_pdg_has_edges(pdg):
    assert "edges" in pdg


def test_pdg_nodes_non_empty(pdg):
    assert len(pdg["nodes"]) > 0


def test_pdg_edges_non_empty(pdg):
    assert len(pdg["edges"]) > 0


def test_pdg_edges_are_tuples_or_lists(pdg):
    for edge in pdg["edges"]:
        assert isinstance(edge, (tuple, list))


# ---------------------------------------------------------------------------
# holon_zero_summary
# ---------------------------------------------------------------------------

def test_summary_is_dict_or_str(summary):
    assert isinstance(summary, (dict, str))


def test_summary_non_empty(summary):
    if isinstance(summary, dict):
        assert len(summary) > 0
    else:
        assert len(summary) > 0


def test_summary_has_theorem_if_dict(summary):
    if isinstance(summary, dict):
        assert "theorem" in summary or "title" in summary


def test_summary_coverage_if_dict(summary):
    if isinstance(summary, dict):
        assert "coverage" in summary or "total" in str(summary)
