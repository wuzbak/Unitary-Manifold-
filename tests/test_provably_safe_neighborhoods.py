# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

import math

import pytest

from src.core.provably_safe_neighborhoods import (
    PosteriorInputs,
    TruncationEnvelope,
    classify_obligation,
    posterior_neighborhood_certificate,
    singularity_routing_gate,
)


def _good_inputs() -> PosteriorInputs:
    return PosteriorInputs(
        residual_bound=1e-4,
        inverse_bound=0.8,
        lipschitz_bound=0.2,
        envelope=TruncationEnvelope(
            truncation_tail_bound=2e-5,
            operator_remainder_bound=2e-5,
            interval_roundoff_bound=1e-6,
            analytic_tail_bound=1e-5,
        ),
    )


def test_envelope_total() -> None:
    env = _good_inputs().envelope
    assert env.total_bound() == pytest.approx(5.1e-5)


def test_posterior_certificate_passes_for_safe_case() -> None:
    cert = posterior_neighborhood_certificate(_good_inputs())
    assert cert["certified"] is True
    assert cert["radius"] > 0.0
    assert cert["contraction_margin"] > 0.0
    assert cert["fail_reasons"] == []


def test_posterior_certificate_fails_for_non_contractive_case() -> None:
    bad = PosteriorInputs(
        residual_bound=1e-4,
        inverse_bound=1.5,
        lipschitz_bound=1.0,
        envelope=_good_inputs().envelope,
    )
    cert = posterior_neighborhood_certificate(bad)
    assert cert["certified"] is False
    assert "non_contractive_linearization" in cert["fail_reasons"]


def test_posterior_certificate_fails_uniqueness_gate() -> None:
    bad = PosteriorInputs(
        residual_bound=1.2,
        inverse_bound=1.0,
        lipschitz_bound=0.49,
        envelope=TruncationEnvelope(0.0, 0.0, 0.0, 0.0),
    )
    cert = posterior_neighborhood_certificate(bad)
    assert cert["certified"] is False
    assert "uniqueness_gate_failed" in cert["fail_reasons"]


def test_negative_inputs_raise() -> None:
    with pytest.raises(ValueError):
        posterior_neighborhood_certificate(
            PosteriorInputs(
                residual_bound=-1.0,
                inverse_bound=1.0,
                lipschitz_bound=0.1,
                envelope=TruncationEnvelope(0.0, 0.0, 0.0, 0.0),
            )
        )


def test_nonfinite_inputs_raise() -> None:
    with pytest.raises(ValueError):
        posterior_neighborhood_certificate(
            PosteriorInputs(
                residual_bound=float("nan"),
                inverse_bound=1.0,
                lipschitz_bound=0.1,
                envelope=TruncationEnvelope(0.0, 0.0, 0.0, 0.0),
            )
        )
    with pytest.raises(ValueError):
        posterior_neighborhood_certificate(
            PosteriorInputs(
                residual_bound=0.0,
                inverse_bound=1.0,
                lipschitz_bound=0.1,
                envelope=TruncationEnvelope(float("inf"), 0.0, 0.0, 0.0),
            )
        )


def test_zero_seed_exact_solution_is_certified() -> None:
    cert = posterior_neighborhood_certificate(
        PosteriorInputs(
            residual_bound=0.0,
            inverse_bound=0.8,
            lipschitz_bound=0.2,
            envelope=TruncationEnvelope(0.0, 0.0, 0.0, 0.0),
        )
    )
    assert cert["certified"] is True
    assert cert["radius"] == pytest.approx(0.0)
    assert cert["uniqueness_gate"] == pytest.approx(0.0)


def test_obligation_split_classifier() -> None:
    assert classify_obligation("interval_roundoff_bound") == "interval"
    assert classify_obligation("sobolev_tail_control") == "analytic"
    assert classify_obligation("topology reaction") == "analytic"


def test_singularity_route_geometric_fail_closed() -> None:
    routed = singularity_routing_gate(
        coordinate_singularity_detected=True,
        invariant_curvature_blowup=True,
        topology_reaction_detected=False,
    )
    assert routed["route"] == "geometric_singularity"
    assert routed["status"] == "fail_closed"


def test_singularity_route_coordinate_rechart() -> None:
    routed = singularity_routing_gate(
        coordinate_singularity_detected=True,
        invariant_curvature_blowup=False,
        topology_reaction_detected=False,
    )
    assert routed["route"] == "coordinate_artifact"
    assert routed["status"] == "rechart_required"


def test_singularity_route_regular() -> None:
    routed = singularity_routing_gate(False, False, False)
    assert routed["status"] == "pass"
    assert routed["route"] == "regular"
