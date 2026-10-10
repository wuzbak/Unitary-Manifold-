# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_cosmology_slider import (
    JAX_AVAILABLE,
    N_S_PLANCK_2018,
    N_S_UM_CANONICAL,
    slider_reading,
    sweep_phi0,
    require_jax,
)

pytestmark = pytest.mark.skipif(not JAX_AVAILABLE, reason="JAX not installed in this environment")


def test_slider_reading_returns_gradient_fields():
    reading = slider_reading(phi0=10.0, n_w=5.0)
    assert reading.n_s != 0.0
    assert reading.dn_s_dphi0 != 0.0
    assert reading.dn_s_dnw != 0.0


def test_slider_reading_gap_to_planck_is_consistent():
    reading = slider_reading(phi0=10.0, n_w=5.0)
    assert reading.gap_to_planck == pytest.approx(reading.n_s - N_S_PLANCK_2018)


def test_closer_if_phi0_increases_is_boolean():
    reading = slider_reading(phi0=10.0, n_w=5.0)
    assert isinstance(reading.closer_if_phi0_increases, bool)


def test_sweep_phi0_returns_one_reading_per_value():
    readings = sweep_phi0(n_w=5.0, phi0_values=[8.0, 9.0, 10.0, 11.0])
    assert len(readings) == 4
    assert all(r.n_w == 5.0 for r in readings)


def test_increasing_phi0_monotonically_changes_n_s():
    readings = sweep_phi0(n_w=5.0, phi0_values=[8.0, 9.0, 10.0, 11.0, 12.0])
    n_s_values = [r.n_s for r in readings]
    # n_s = 1 - 8*n_w/phi0^2 is monotonically increasing in phi0 for phi0 > 0
    assert n_s_values == sorted(n_s_values)


def test_require_jax_does_not_raise_when_available():
    require_jax()


def test_n_s_constants_match_known_repo_values():
    assert N_S_PLANCK_2018 == pytest.approx(0.9649)
    assert N_S_UM_CANONICAL == pytest.approx(0.9635)


def test_require_jax_raises_runtime_error_when_unavailable(monkeypatch):
    import az_cosmology_slider.slider as slider_module

    monkeypatch.setattr(slider_module, "JAX_AVAILABLE", False)
    monkeypatch.setattr(slider_module, "_IMPORT_ERROR", "simulated missing jax")
    with pytest.raises(RuntimeError):
        slider_module.require_jax()
