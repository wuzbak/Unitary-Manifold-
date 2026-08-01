from __future__ import annotations

import pytest

from src.twelved.ftheory_rung8_aps_discriminator import (
    DISCRIMINATOR_STRENGTH,
    EPISTEMIC_STATUS,
    K_CS,
    N_2,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    aps_discriminator,
    axiomzero_seed_purity_check,
    kill_switch_check,
    monodromy_matrix,
    nw_selection_verdict,
    pillar_report,
    rung8_anchor_b_status,
)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("PILLAR_NUMBER", PILLAR_NUMBER),
        ("PILLAR_STATUS", PILLAR_STATUS),
        ("EPISTEMIC_STATUS", EPISTEMIC_STATUS),
        ("VERSION", VERSION),
        ("K_CS", K_CS),
        ("N_W", N_W),
        ("N_2", N_2),
    ],
)
def test_constants_are_present(name, value):
    assert value is not None, name


def test_constant_values_are_exact():
    assert PILLAR_NUMBER == 576
    assert PILLAR_STATUS == "FTHEORY_RUNG8_APS_DISCRIMINATOR_ADJACENT"
    assert EPISTEMIC_STATUS == "ADJACENT_TRACK"
    assert VERSION == "v20.1"
    assert K_CS == 74
    assert N_W == 5
    assert N_2 == 7
    assert DISCRIMINATOR_STRENGTH == pytest.approx(24.0 / 74.0)


@pytest.mark.parametrize("k", [1, 5, 7, 9])
def test_monodromy_matrix_shape_and_entries(k):
    matrix = monodromy_matrix(k)
    assert matrix == [[1, k], [0, 1]]
    assert len(matrix) == 2
    assert len(matrix[0]) == 2
    assert len(matrix[1]) == 2


@pytest.mark.parametrize("k", [0, -1, -5])
def test_monodromy_matrix_rejects_nonpositive_k(k):
    with pytest.raises(ValueError):
        monodromy_matrix(k)


@pytest.mark.parametrize(
    "key",
    [
        "check",
        "eta_t5_proxy",
        "eta_t7_proxy",
        "discriminator_strength",
        "expected_strength",
        "k_cs_preserved",
        "pass",
        "honest_status",
        "evidence",
    ],
)
def test_aps_discriminator_has_expected_keys(key):
    result = aps_discriminator()
    assert key in result


def test_aps_discriminator_numeric_values():
    result = aps_discriminator()
    assert result["eta_t5_proxy"] == pytest.approx(25.0 / 74.0)
    assert result["eta_t7_proxy"] == pytest.approx(49.0 / 74.0)
    assert result["discriminator_strength"] == pytest.approx(DISCRIMINATOR_STRENGTH)
    assert result["expected_strength"] == pytest.approx(DISCRIMINATOR_STRENGTH)
    assert result["k_cs_preserved"] is True
    assert result["pass"] is True


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("selected_winding", 5),
        ("su5_matches_nw", True),
        ("su7_conflicts_with_nw", True),
        ("t5_off_diagonal", 5),
        ("t7_off_diagonal", 7),
        ("selection_is_quantified", True),
    ],
)
def test_selection_verdict_fields(key, expected):
    verdict = nw_selection_verdict()
    assert verdict[key] == expected


def test_selection_verdict_uses_discriminator_strength():
    verdict = nw_selection_verdict()
    assert verdict["relative_weight"] == pytest.approx(DISCRIMINATOR_STRENGTH)
    assert "favored" in verdict["verdict"]


@pytest.mark.parametrize(
    "key",
    ["check", "geometric_inputs", "pdg_fit_inputs", "pass", "evidence"],
)
def test_axiomzero_seed_purity_shape(key):
    purity = axiomzero_seed_purity_check()
    assert key in purity


def test_axiomzero_seed_purity_values():
    purity = axiomzero_seed_purity_check()
    assert len(purity["geometric_inputs"]) == 4
    assert purity["pdg_fit_inputs"] == []
    assert purity["pass"] is True
    assert "0 PDG" in purity["evidence"]


@pytest.mark.parametrize(
    "key",
    [
        "pillar",
        "anchor",
        "status",
        "adjacent_track",
        "blocking_residual_closed",
        "selection_strength",
        "selected_winding",
        "remaining_open_item",
        "kill_switch_pass",
    ],
)
def test_rung8_anchor_b_status_keys(key):
    status = rung8_anchor_b_status()
    assert key in status


def test_rung8_anchor_b_status_values():
    status = rung8_anchor_b_status()
    assert status["pillar"] == 576
    assert status["anchor"] == "B"
    assert status["selection_strength"] == pytest.approx(DISCRIMINATOR_STRENGTH)
    assert status["selected_winding"] == 5
    assert "Weierstrass" in status["remaining_open_item"]
    assert status["kill_switch_pass"] is True


def test_kill_switch_passes():
    assert kill_switch_check() is True


@pytest.mark.parametrize(
    "key",
    [
        "pillar",
        "title",
        "status",
        "version",
        "epistemic_status",
        "constants",
        "aps_discriminator",
        "nw_selection_verdict",
        "axiomzero_seed_purity",
        "rung8_anchor_b_status",
        "kill_switch_pass",
    ],
)
def test_pillar_report_keys(key):
    report = pillar_report()
    assert key in report


def test_pillar_report_nested_values():
    report = pillar_report()
    assert report["constants"]["k_cs"] == 74
    assert report["constants"]["n_w"] == 5
    assert report["constants"]["n_2"] == 7
    assert report["kill_switch_pass"] is True
    assert report["aps_discriminator"]["pass"] is True
    assert report["nw_selection_verdict"]["su7_conflicts_with_nw"] is True
