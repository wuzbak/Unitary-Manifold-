# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

import numpy as np
import pytest

from src.core.pmns_seesaw_5d import (
    pmns_from_rs_weinberg_seesaw,
    radion_induced_majorana_scale,
)


def test_radion_induced_majorana_scale_positive():
    assert radion_induced_majorana_scale() > 0.0


def test_radion_induced_majorana_scale_invalid_inputs_raise():
    with pytest.raises(ValueError):
        radion_induced_majorana_scale(m_r0_gev=-1.0)
    with pytest.raises(ValueError):
        radion_induced_majorana_scale(pi_kr=0.0)


def test_pmns_from_rs_weinberg_seesaw_keys():
    result = pmns_from_rs_weinberg_seesaw()
    for key in ("theta_12_deg", "theta_13_deg", "theta_23_deg", "m_r_eff_gev", "in_band_theta12"):
        assert key in result


def test_pmns_from_rs_weinberg_seesaw_is_finite():
    result = pmns_from_rs_weinberg_seesaw()
    assert np.isfinite(result["theta_12_deg"])
    assert np.isfinite(result["theta_13_deg"])
    assert np.isfinite(result["theta_23_deg"])


def test_pmns_from_rs_weinberg_seesaw_unitary_like():
    result = pmns_from_rs_weinberg_seesaw()
    u = result["U_pmns"]
    ident = u.conj().T @ u
    assert np.allclose(ident, np.eye(3), atol=1e-8)
