# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

import numpy as np
import pytest

from src.core.ckm_nlo_g5_expansion import (
    ckm_nlo_from_yukawa_and_epsilon,
    default_epsilon_matrices,
    extract_mixing_angles,
    nlo_yukawa_from_epsilon,
)
from src.core.ckm_pmns_orbifold import C_L_QUARKS, yukawa_matrix_down, yukawa_matrix_up


def test_default_epsilon_matrices_shape():
    eps_u, eps_d = default_epsilon_matrices(C_L_QUARKS)
    assert eps_u.shape == (3, 3)
    assert eps_d.shape == (3, 3)


def test_default_epsilon_requires_valid_lambda():
    with pytest.raises(ValueError):
        default_epsilon_matrices(C_L_QUARKS, lambda_target=0.0)


def test_nlo_yukawa_from_epsilon_shape():
    m = yukawa_matrix_up()
    eps = np.zeros((3, 3))
    m_nlo = nlo_yukawa_from_epsilon(m, eps)
    assert m_nlo.shape == (3, 3)


def test_nlo_yukawa_from_epsilon_invalid_shape():
    with pytest.raises(ValueError):
        nlo_yukawa_from_epsilon(np.eye(2), np.eye(3))


def test_extract_mixing_angles_shape_validation():
    with pytest.raises(ValueError):
        extract_mixing_angles(np.eye(2))


def test_ckm_nlo_from_yukawa_and_epsilon_keys():
    m_u = yukawa_matrix_up()
    m_d = yukawa_matrix_down()
    eps_u, eps_d = default_epsilon_matrices(C_L_QUARKS)
    result = ckm_nlo_from_yukawa_and_epsilon(m_u, m_d, eps_u, eps_d)
    for key in ("V_ckm_nlo", "theta_12_deg", "theta_13_deg", "theta_23_deg", "wolfenstein_hierarchy"):
        assert key in result


def test_ckm_nlo_angles_nonnegative():
    m_u = yukawa_matrix_up()
    m_d = yukawa_matrix_down()
    eps_u, eps_d = default_epsilon_matrices(C_L_QUARKS)
    result = ckm_nlo_from_yukawa_and_epsilon(m_u, m_d, eps_u, eps_d)
    assert result["theta_12_deg"] >= 0.0
    assert result["theta_13_deg"] >= 0.0
    assert result["theta_23_deg"] >= 0.0
