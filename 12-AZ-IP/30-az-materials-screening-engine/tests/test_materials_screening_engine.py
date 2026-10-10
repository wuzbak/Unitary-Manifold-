# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_materials_screening_engine import MaterialCandidate, screen_candidate, rank_candidates
from az_materials_screening_engine.screening import ALPHA_UM_CANONICAL, CRITICAL_ANGLE_DEG


def test_alpha_um_canonical_is_positive():
    assert ALPHA_UM_CANONICAL > 0


def test_critical_angle_matches_polariton_vortex_module():
    assert CRITICAL_ANGLE_DEG == pytest.approx(18.924644416051237)


def test_screen_candidate_returns_expected_keys():
    candidate = MaterialCandidate(
        name="graphene", alpha=0.3, omega_lo_mev=180.0, m_band_me=0.02, epsilon_r=2.5
    )
    result = screen_candidate(candidate)
    assert result["name"] == "graphene"
    assert result["polaron_binding_energy_ev"] > 0
    assert result["polaron_radius_nm"] > 0
    assert result["predicted_critical_angle_deg"] == pytest.approx(CRITICAL_ANGLE_DEG)


def test_screen_candidate_alpha_divergence_zero_for_canonical_alpha():
    candidate = MaterialCandidate(
        name="UM-matched", alpha=ALPHA_UM_CANONICAL, omega_lo_mev=100.0, m_band_me=0.1, epsilon_r=3.0
    )
    result = screen_candidate(candidate)
    assert result["alpha_divergence_from_um"] == pytest.approx(0.0, abs=1e-12)


def test_rank_candidates_orders_by_divergence_descending():
    candidates = [
        MaterialCandidate("MoS2", alpha=ALPHA_UM_CANONICAL + 0.01, omega_lo_mev=50.0, m_band_me=0.5, epsilon_r=4.0),
        MaterialCandidate("hBN", alpha=ALPHA_UM_CANONICAL + 5.0, omega_lo_mev=170.0, m_band_me=0.3, epsilon_r=5.0),
        MaterialCandidate("graphene", alpha=ALPHA_UM_CANONICAL, omega_lo_mev=180.0, m_band_me=0.02, epsilon_r=2.5),
    ]
    ranked = rank_candidates(candidates)
    assert [r["name"] for r in ranked] == ["hBN", "MoS2", "graphene"]
    assert [r["rank"] for r in ranked] == [1, 2, 3]


def test_rank_candidates_rejects_empty_list():
    with pytest.raises(ValueError):
        rank_candidates([])


def test_negative_phi_index_flagged_for_double_negative_material():
    candidate = MaterialCandidate(
        name="synthetic-negative", alpha=0.2, omega_lo_mev=100.0, m_band_me=0.1,
        epsilon_r=-2.0, mu_r=-1.0,
    )
    result = screen_candidate(candidate)
    assert result["negative_phi_index"] < 0
