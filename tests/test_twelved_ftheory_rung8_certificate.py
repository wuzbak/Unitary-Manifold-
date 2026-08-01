from __future__ import annotations

import pytest

from src.twelved.ftheory_rung8_certificate import (
    EPISTEMIC_STATUS,
    GAP_B_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    RUNG_8_STATUS,
    VERSION,
    dbp_ladder_status,
    kill_switch_check,
    pillar_report,
    remaining_open_items,
    rung8_advances,
)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("PILLAR_NUMBER", PILLAR_NUMBER),
        ("PILLAR_STATUS", PILLAR_STATUS),
        ("EPISTEMIC_STATUS", EPISTEMIC_STATUS),
        ("VERSION", VERSION),
        ("RUNG_8_STATUS", RUNG_8_STATUS),
        ("GAP_B_STATUS", GAP_B_STATUS),
    ],
)
def test_constants_are_present(label, value):
    assert value is not None, label


def test_constant_values_are_exact():
    assert PILLAR_NUMBER == 579
    assert PILLAR_STATUS == "FTHEORY_RUNG8_CERTIFICATE_ADJACENT"
    assert EPISTEMIC_STATUS == "ADJACENT_TRACK"
    assert VERSION == "v20.1"
    assert RUNG_8_STATUS == "RUNG_8_PARTIAL_CLOSURE"
    assert GAP_B_STATUS == "PROVED_AT_REFERENCE_CY4"


@pytest.mark.parametrize("key", ["rung7_foundation", "rung8_closures", "kill_switch_pass"])
def test_rung8_advances_top_level_keys(key):
    advances = rung8_advances()
    assert key in advances


def test_rung8_advances_has_three_closures():
    advances = rung8_advances()
    closures = advances["rung8_closures"]
    assert len(closures) == 3
    assert [entry["pillar"] for entry in closures] == [576, 577, 578]


@pytest.mark.parametrize(
    ("index", "name_fragment"),
    [
        (0, "APS discriminator"),
        (1, "c_L lower bound"),
        (2, "D3-tadpole"),
    ],
)
def test_rung8_advance_names(index, name_fragment):
    advances = rung8_advances()
    assert name_fragment in advances["rung8_closures"][index]["name"]


@pytest.mark.parametrize("fragment", ["reference CY4", "spectral cover", "matter-curve", "curvature"])
def test_remaining_open_items_fragments(fragment):
    text = " ".join(remaining_open_items())
    assert fragment in text


def test_remaining_open_items_length_and_order():
    items = remaining_open_items()
    assert len(items) == 2
    assert items[0].startswith("Blocking Residual 2")
    assert items[1].startswith("Blocking Residual 3")


@pytest.mark.parametrize(
    "key",
    [
        "rung7_status",
        "rung8_status",
        "gap_b_status",
        "full_closure_claimed",
        "next_step",
        "remaining_open_items",
    ],
)
def test_dbp_ladder_status_keys(key):
    status = dbp_ladder_status()
    assert key in status


def test_dbp_ladder_status_values():
    status = dbp_ladder_status()
    assert status["rung7_status"] == "SCAFFOLD_COMPLETE"
    assert status["rung8_status"] == "RUNG_8_PARTIAL_CLOSURE"
    assert status["gap_b_status"] == "PROVED_AT_REFERENCE_CY4"
    assert status["full_closure_claimed"] is False
    assert len(status["remaining_open_items"]) == 2
    assert "Weierstrass" in status["next_step"]


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
        "rung_8_status",
        "gap_b_status",
        "rung8_advances",
        "dbp_ladder_status",
        "remaining_open_items",
        "kill_switch_pass",
    ],
)
def test_pillar_report_keys(key):
    report = pillar_report()
    assert key in report


def test_pillar_report_values():
    report = pillar_report()
    assert report["pillar"] == 579
    assert report["rung_8_status"] == "RUNG_8_PARTIAL_CLOSURE"
    assert report["gap_b_status"] == "PROVED_AT_REFERENCE_CY4"
    assert len(report["remaining_open_items"]) == 2
    assert report["kill_switch_pass"] is True


@pytest.mark.parametrize("status_key", ["status", "kill_switch_pass"])
def test_nested_reports_contain_status(status_key):
    report = pillar_report()
    assert status_key in report["rung8_advances"]
