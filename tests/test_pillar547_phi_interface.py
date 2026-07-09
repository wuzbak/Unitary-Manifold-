# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 547 — AxiomZero OS φ-Field Interface."""
from __future__ import annotations

import math
import pytest
from az_os.phi_field_interface import (
    PHI0,
    PHI_FIELD_CONSTANTS,
    PhiDebtEntry,
    PhiFieldInterface,
    PhiFieldState,
    kk_level_to_radion_mode,
    phi_debt_to_energy,
    radion_tension,
)
from src.core.pillar547_az_os_phi_interface import (
    INTERFACE_CONTRACT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    pillar_report,
    phi_field_interface_report,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 547


def test_pillar_status():
    assert "PHI_FIELD_INTERFACE" in PILLAR_STATUS


def test_version():
    assert VERSION == "v19.0"


# ─── Constants ───────────────────────────────────────────────────────────────

def test_phi0_value():
    # φ₀ = 5 × 2π
    assert PHI0 == pytest.approx(5 * 2 * math.pi, rel=1e-10)


def test_phi_field_constants_keys():
    required = ["phi0", "n_w", "k_cs", "c_s", "delta_c", "kk_levels", "xi_c"]
    for key in required:
        assert key in PHI_FIELD_CONSTANTS


def test_n_w():
    assert PHI_FIELD_CONSTANTS["n_w"] == 5


def test_k_cs():
    assert PHI_FIELD_CONSTANTS["k_cs"] == 74


def test_xi_c():
    assert PHI_FIELD_CONSTANTS["xi_c"] == pytest.approx(35 / 74)


# ─── PhiFieldState ───────────────────────────────────────────────────────────

def test_at_fixed_point():
    state = PhiFieldState.at_fixed_point()
    assert state.phi_value == pytest.approx(PHI0)
    assert state.phi_dot == pytest.approx(0.0)
    assert state.kk_level == 0


def test_at_fixed_point_zero_tension():
    state = PhiFieldState.at_fixed_point()
    assert state.os_tension() == pytest.approx(0.0)


def test_is_near_fixed_point_at_fp():
    state = PhiFieldState.at_fixed_point()
    assert state.is_near_fixed_point() is True


def test_is_not_near_fixed_point_far():
    state = PhiFieldState(phi_value=PHI0 * 2.0)
    assert state.is_near_fixed_point() is False


def test_update_phi_debt_increments_step():
    state = PhiFieldState.at_fixed_point()
    new_state = state.update_phi_debt(0.01)
    assert new_state.step == 1
    assert new_state.phi_debt_total == pytest.approx(0.01)


def test_kk_excitation_energy_level_0():
    state = PhiFieldState.at_fixed_point()
    energy = state.kk_excitation_energy()
    assert energy == pytest.approx(0.0)


def test_kk_excitation_energy_level_1():
    state = PhiFieldState(phi_value=PHI0, kk_level=1)
    energy = state.kk_excitation_energy()
    assert energy == pytest.approx(5 / 74, rel=1e-10)


def test_to_dict_keys():
    state = PhiFieldState.at_fixed_point()
    d = state.to_dict()
    for key in ["phi_value", "phi_dot", "os_tension", "near_fixed_point", "kk_excitation_energy"]:
        assert key in d


# ─── PhiDebtEntry ────────────────────────────────────────────────────────────

def test_phi_debt_energy_cost():
    entry = PhiDebtEntry(agent_id="M1.A", manager="M1", kk_level=0, delta_phi=0.0)
    assert entry.energy_cost() == pytest.approx(0.0)


def test_phi_debt_energy_positive():
    entry = PhiDebtEntry(agent_id="M2.B", manager="M2", kk_level=1, delta_phi=1.0)
    assert entry.energy_cost() > 0


def test_phi_debt_kk_mode():
    entry = PhiDebtEntry(agent_id="M3.C", manager="M3", kk_level=2, delta_phi=0.5)
    assert entry.kk_mode_number() == 2


# ─── PhiFieldInterface ───────────────────────────────────────────────────────

def test_interface_initializes_at_fp():
    iface = PhiFieldInterface()
    state = iface.get_current_state()
    assert state.is_near_fixed_point() is True


def test_interface_record_small_debt():
    iface = PhiFieldInterface()
    entry = iface.record_phi_debt("M1.MetricAgent", "M1", kk_level=0, delta_phi=0.001)
    assert isinstance(entry, PhiDebtEntry)
    assert entry.delta_phi == pytest.approx(0.001)


def test_interface_no_hils_alert_small_debt():
    iface = PhiFieldInterface()
    iface.record_phi_debt("M1.A", "M1", 0, 0.001)
    tension = iface.aggregate_os_tension()
    assert tension["hils_alerts_raised"] == 0


def test_interface_hils_alert_large_debt():
    iface = PhiFieldInterface()
    # Large deviation to trigger alert (tension > 1%)
    iface.record_phi_debt("M7.B", "M7", 4, PHI0 * 0.5)
    tension = iface.aggregate_os_tension()
    assert tension["hils_alerts_raised"] >= 1


def test_interface_reset_to_fp():
    iface = PhiFieldInterface()
    iface.record_phi_debt("M1.A", "M1", 0, PHI0 * 0.5)
    iface.reset_to_fixed_point()
    assert iface.get_current_state().is_near_fixed_point() is True
    assert len(iface.hils_alerts()) == 0


def test_interface_debt_log():
    iface = PhiFieldInterface()
    iface.record_phi_debt("M2.A", "M2", 1, 0.01)
    iface.record_phi_debt("M3.B", "M3", 2, 0.02)
    assert len(iface.debt_log()) == 2


def test_interface_invalid_kk_level():
    iface = PhiFieldInterface()
    with pytest.raises(ValueError):
        iface.record_phi_debt("M1.A", "M1", kk_level=5, delta_phi=0.01)


# ─── Utility functions ───────────────────────────────────────────────────────

def test_kk_level_to_mode_0():
    assert kk_level_to_radion_mode(0) == 0


def test_kk_level_to_mode_4():
    assert kk_level_to_radion_mode(4) == 4


def test_kk_level_invalid():
    with pytest.raises(ValueError):
        kk_level_to_radion_mode(5)


def test_radion_tension_at_fixed_point():
    assert radion_tension(PHI0) == pytest.approx(0.0)


def test_radion_tension_positive():
    assert radion_tension(PHI0 + 1.0) > 0


def test_radion_tension_symmetric():
    assert radion_tension(PHI0 + 1.0) == pytest.approx(radion_tension(PHI0 - 1.0))


def test_phi_debt_to_energy_zero():
    assert phi_debt_to_energy(0.0) == pytest.approx(0.0)


def test_phi_debt_to_energy_positive():
    assert phi_debt_to_energy(1.0) > 0


# ─── Interface contract ──────────────────────────────────────────────────────

def test_interface_contract_components():
    components = INTERFACE_CONTRACT["components"]
    assert "PhiFieldState" in components
    assert "PhiFieldInterface" in components
    assert "PhiDebtEntry" in components


def test_interface_contract_kk_levels():
    kk_map = INTERFACE_CONTRACT["kk_level_mapping"]
    assert "level_0" in kk_map
    assert "level_4" in kk_map


# ─── Full report ─────────────────────────────────────────────────────────────

def test_pillar_report():
    report = pillar_report()
    assert report["pillar"] == 547
    assert report["infrastructure_pillar"] is True
    assert report["toe_score_delta"] == 0.0
