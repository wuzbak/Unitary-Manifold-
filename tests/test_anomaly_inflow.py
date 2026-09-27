# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.anomaly_inflow_3sector import (
    N_W_UV,
    N_PARENT_BULK,
    N_SHADOW_IR,
    K_CS,
    eta_invariants_3sector,
    anomaly_coefficients_3sector,
    required_weyl_fermions_3sector,
)


def test_three_sector_constants():
    assert N_W_UV == 5
    assert N_PARENT_BULK == 6
    assert N_SHADOW_IR == 7
    assert K_CS == 74


def test_eta_invariants_are_expected_classes():
    info = eta_invariants_3sector()
    assert info["eta_uv_y0"] == 0.5
    assert info["eta_ir_yPiR"] == 0.0
    assert info["bulk_instanton_number"] == 6.0


def test_linear_candidate_is_18():
    coeffs = anomaly_coefficients_3sector()
    assert coeffs["linear_sector_sum"] == 18.0


def test_18_is_not_uniquely_forced():
    req = required_weyl_fermions_3sector()
    assert req["required_by_linear_model"] == 18
    assert req["is_unique_at_18"] is False
    assert req["status"] == "OPEN_GAP"

