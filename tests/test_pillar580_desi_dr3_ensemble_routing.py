from __future__ import annotations

import pytest

from src.core.pillar580_desi_dr3_ensemble_routing import (
    EUCLID_W0_WINDOW,
    EUCLID_WA_WINDOW,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SIGMA_DR2,
    SIGMA_DR3_PROJECTED,
    SIGMA_FALSIFIED,
    SIGMA_PASS,
    VERSION,
    W0_CANONICAL,
    WA_CANONICAL,
    dr3_routing_summary,
    ensemble_branches,
    extension_trigger_probability,
    pillar_report,
    route_dr3_observation,
)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("PILLAR_NUMBER", PILLAR_NUMBER),
        ("PILLAR_STATUS", PILLAR_STATUS),
        ("VERSION", VERSION),
        ("SIGMA_DR2", SIGMA_DR2),
        ("SIGMA_DR3_PROJECTED", SIGMA_DR3_PROJECTED),
        ("SIGMA_FALSIFIED", SIGMA_FALSIFIED),
        ("SIGMA_PASS", SIGMA_PASS),
        ("W0_CANONICAL", W0_CANONICAL),
        ("WA_CANONICAL", WA_CANONICAL),
        ("EUCLID_W0_WINDOW", EUCLID_W0_WINDOW),
        ("EUCLID_WA_WINDOW", EUCLID_WA_WINDOW),
    ],
)
def test_constants_are_present(label, value):
    assert value is not None, label


def test_constant_values_are_exact():
    assert PILLAR_NUMBER == 580
    assert PILLAR_STATUS == "DESI_DR3_ENSEMBLE_ROUTING_HARDENED"
    assert VERSION == "v20.1"
    assert SIGMA_DR2 == pytest.approx(2.75)
    assert SIGMA_DR3_PROJECTED == pytest.approx(3.64)
    assert SIGMA_FALSIFIED == pytest.approx(3.0)
    assert SIGMA_PASS == pytest.approx(2.0)
    assert W0_CANONICAL == pytest.approx(-1.0)
    assert WA_CANONICAL == pytest.approx(0.0)
    assert EUCLID_W0_WINDOW == pytest.approx(0.05)
    assert EUCLID_WA_WINDOW == pytest.approx(0.3)


@pytest.mark.parametrize(
    ("sigma", "decision_branch", "ensemble_branch", "extension_triggered"),
    [
        (0.0, "PASS", "PASS", False),
        (1.99, "PASS", "PASS", False),
        (2.0, "TENSION", "TENSION", False),
        (2.75, "TENSION", "TENSION", False),
        (3.0, "FALSIFIED", "FALSIFIED", False),
        (3.2, "FALSIFIED", "FALSIFIED", False),
        (3.64, "FALSIFIED", "EXTENSION_TRIGGER", True),
        (4.2, "FALSIFIED", "EXTENSION_TRIGGER", True),
    ],
)
def test_route_dr3_observation_branches(sigma, decision_branch, ensemble_branch, extension_triggered):
    route = route_dr3_observation(sigma)
    assert route["decision_branch"] == decision_branch
    assert route["ensemble_branch"] == ensemble_branch
    assert route["extension_triggered"] is extension_triggered
    assert route["falsified"] == (decision_branch == "FALSIFIED")


@pytest.mark.parametrize("key", ["sigma", "decision_branch", "ensemble_branch", "falsified", "extension_triggered", "action", "euclid_cross_check_window", "honest_note"])
def test_route_dr3_observation_keys(key):
    route = route_dr3_observation(2.75)
    assert key in route


def test_route_dr3_observation_euclid_window_values():
    route = route_dr3_observation(2.75)
    assert route["euclid_cross_check_window"]["w0"] == pytest.approx((-1.05, -0.95))
    assert route["euclid_cross_check_window"]["wa"] == pytest.approx((-0.3, 0.3))
    assert "Pillar 551" in route["honest_note"]


def test_route_dr3_observation_rejects_negative_sigma():
    with pytest.raises(ValueError):
        route_dr3_observation(-0.1)


def test_ensemble_branches_count_and_names():
    branches = ensemble_branches()
    assert len(branches) == 4
    assert [entry["branch"] for entry in branches] == ["PASS", "TENSION", "FALSIFIED", "EXTENSION_TRIGGER"]


@pytest.mark.parametrize("index", [0, 1, 2, 3])
def test_ensemble_branches_have_condition_and_verdict(index):
    entry = ensemble_branches()[index]
    assert "condition" in entry
    assert "verdict" in entry
    assert isinstance(entry["condition"], str)
    assert isinstance(entry["verdict"], str)


@pytest.mark.parametrize("key", ["mean_sigma", "threshold", "scatter_sigma", "z_score", "probability_sigma_exceeds_threshold"])
def test_extension_trigger_probability_keys(key):
    result = extension_trigger_probability()
    assert key in result


def test_extension_trigger_probability_values():
    result = extension_trigger_probability()
    assert result["mean_sigma"] == pytest.approx(3.64)
    assert result["threshold"] == pytest.approx(3.0)
    assert result["scatter_sigma"] == pytest.approx(0.64)
    assert result["z_score"] == pytest.approx(-1.0)
    assert result["probability_sigma_exceeds_threshold"] == pytest.approx(0.841344746, rel=1e-6)


def test_extension_trigger_probability_rejects_nonpositive_scatter():
    with pytest.raises(ValueError):
        extension_trigger_probability(scatter_sigma=0.0)


@pytest.mark.parametrize(
    "key",
    [
        "dr2_baseline_sigma",
        "dr3_year5_central_projection",
        "pass_threshold",
        "falsified_threshold",
        "projected_route",
        "extension_trigger_probability",
        "euclid_cross_check",
    ],
)
def test_dr3_routing_summary_keys(key):
    summary = dr3_routing_summary()
    assert key in summary


def test_dr3_routing_summary_values():
    summary = dr3_routing_summary()
    assert summary["dr2_baseline_sigma"] == pytest.approx(2.75)
    assert summary["dr3_year5_central_projection"] == pytest.approx(3.64)
    assert summary["projected_route"]["ensemble_branch"] == "EXTENSION_TRIGGER"
    assert summary["euclid_cross_check"]["w0_center"] == pytest.approx(-1.0)
    assert summary["euclid_cross_check"]["wa_window"] == pytest.approx(0.3)


@pytest.mark.parametrize(
    "key",
    [
        "pillar",
        "title",
        "status",
        "version",
        "ensemble_branches",
        "dr3_routing_summary",
        "sample_pass_route",
        "sample_tension_route",
        "sample_falsified_route",
    ],
)
def test_pillar_report_keys(key):
    report = pillar_report()
    assert key in report


def test_pillar_report_values():
    report = pillar_report()
    assert report["pillar"] == 580
    assert report["sample_pass_route"]["decision_branch"] == "PASS"
    assert report["sample_tension_route"]["decision_branch"] == "TENSION"
    assert report["sample_falsified_route"]["decision_branch"] == "FALSIFIED"
    assert report["dr3_routing_summary"]["projected_route"]["extension_triggered"] is True
