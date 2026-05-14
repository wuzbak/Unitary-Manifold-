# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_fh_curved.py
========================
Tests for src/quantum/fh_curved.py — curved-space Fermi–Hubbard scaffolding
(adjacent engineering lane, non-hardgate).
"""
from __future__ import annotations

import math

import pytest

from src.quantum.fh_curved import (
    KK_BRAIDED_SOUND_SPEED,
    KK_RADION_COUPLING,
    KK_WINDING_NUMBER,
    CURVED_TRACK_LABEL,
    CurvedFermiHubbardLattice,
    CurvedSpaceFHSpec,
    KKCurvedGeometrySpec,
    RadionField,
    build_fermi_hubbard_curved,
    build_radion_field_kk_natural,
    build_radion_field_sinusoidal,
    build_radion_field_uniform,
    curved_adjacency_report,
    curved_hopping_coefficient,
    kk_curved_spec,
    radion_hopping_factor,
    separation_guard,
)
from src.quantum.fh_lattice import (
    build_fermi_hubbard_braid_kk,
    build_fermi_hubbard_chain,
)


# ===========================================================================
# Module-level constants
# ===========================================================================


def test_kk_radion_coupling_value() -> None:
    # λ = c_s / n_w = (12/37) / 5 = 12/185
    assert KK_RADION_COUPLING == pytest.approx(12.0 / 185.0, rel=1e-12)


def test_kk_braided_sound_speed() -> None:
    assert KK_BRAIDED_SOUND_SPEED == pytest.approx(12.0 / 37.0, rel=1e-12)


def test_kk_winding_number() -> None:
    assert KK_WINDING_NUMBER == 5


def test_curved_track_label_non_empty() -> None:
    assert len(CURVED_TRACK_LABEL) > 0
    assert "NOT" in CURVED_TRACK_LABEL


# ===========================================================================
# RadionField
# ===========================================================================


def test_radion_field_n_sites() -> None:
    rf = build_radion_field_uniform(4)
    assert rf.n_sites == 4


def test_radion_field_uniform_values() -> None:
    rf = build_radion_field_uniform(3, phi0=0.5)
    assert all(v == pytest.approx(0.5, abs=1e-12) for v in rf.values)


def test_radion_field_profile_label() -> None:
    rf = build_radion_field_uniform(3)
    assert rf.profile == "uniform"


def test_radion_field_coupling_default() -> None:
    rf = build_radion_field_uniform(3)
    assert rf.coupling == pytest.approx(KK_RADION_COUPLING, rel=1e-12)


def test_radion_field_too_small_raises() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        RadionField(values=(0.0,), profile="uniform")


def test_radion_field_negative_coupling_raises() -> None:
    with pytest.raises(ValueError, match="coupling λ"):
        RadionField(values=(0.0, 1.0), profile="uniform", coupling=-1.0)


def test_radion_field_phi_min_max() -> None:
    rf = build_radion_field_sinusoidal(6, amplitude=0.1)
    assert rf.phi_min <= rf.phi_max


def test_radion_field_phi_spread_uniform_zero() -> None:
    rf = build_radion_field_uniform(4, phi0=1.0)
    assert rf.phi_spread == pytest.approx(0.0, abs=1e-12)


# ===========================================================================
# build_radion_field_sinusoidal
# ===========================================================================


def test_sinusoidal_field_length() -> None:
    rf = build_radion_field_sinusoidal(8)
    assert rf.n_sites == 8


def test_sinusoidal_field_amplitude_bounds() -> None:
    A = 0.1
    rf = build_radion_field_sinusoidal(8, amplitude=A)
    for v in rf.values:
        assert abs(v) <= A + 1e-12


def test_sinusoidal_field_profile_label() -> None:
    rf = build_radion_field_sinusoidal(4)
    assert rf.profile == "sinusoidal"


def test_sinusoidal_field_phase_shifts_values() -> None:
    rf0 = build_radion_field_sinusoidal(4, amplitude=0.1, phase=0.0)
    rf1 = build_radion_field_sinusoidal(4, amplitude=0.1, phase=math.pi / 2.0)
    assert list(rf0.values) != list(rf1.values)


# ===========================================================================
# KKCurvedGeometrySpec
# ===========================================================================


def test_kk_curved_spec_defaults() -> None:
    spec = KKCurvedGeometrySpec()
    assert spec.n1 == 5
    assert spec.n2 == 7
    assert spec.k_cs == 74


def test_kk_curved_spec_coupling() -> None:
    spec = KKCurvedGeometrySpec()
    assert spec.coupling == pytest.approx(KK_RADION_COUPLING, rel=1e-12)


def test_kk_curved_spec_flat_limit_false() -> None:
    spec = KKCurvedGeometrySpec(radion_amplitude=0.1)
    assert not spec.flat_limit


def test_kk_curved_spec_flat_limit_true() -> None:
    spec = KKCurvedGeometrySpec(radion_amplitude=0.0)
    assert spec.flat_limit


def test_kk_curved_spec_wrong_k_cs_raises() -> None:
    with pytest.raises(ValueError, match="k_cs must equal"):
        KKCurvedGeometrySpec(n1=5, n2=7, k_cs=100)


def test_kk_curved_spec_negative_amplitude_raises() -> None:
    with pytest.raises(ValueError, match="radion_amplitude"):
        KKCurvedGeometrySpec(radion_amplitude=-0.1)


# ===========================================================================
# build_radion_field_kk_natural
# ===========================================================================


def test_kk_natural_field_length() -> None:
    spec = KKCurvedGeometrySpec()
    rf = build_radion_field_kk_natural(spec)
    assert rf.n_sites == spec.n_sites


def test_kk_natural_field_profile_label() -> None:
    spec = KKCurvedGeometrySpec()
    rf = build_radion_field_kk_natural(spec)
    assert rf.profile == "kk_natural"


def test_kk_natural_field_flat_limit_all_zero() -> None:
    spec = KKCurvedGeometrySpec(radion_amplitude=0.0)
    rf = build_radion_field_kk_natural(spec)
    for v in rf.values:
        assert abs(v) < 1e-12


def test_kk_natural_field_non_uniform_for_nonzero_amplitude() -> None:
    spec = KKCurvedGeometrySpec(radion_amplitude=0.1)
    rf = build_radion_field_kk_natural(spec)
    assert rf.phi_spread > 0


# ===========================================================================
# radion_hopping_factor
# ===========================================================================


def test_hopping_factor_same_site_phi_is_one() -> None:
    f = radion_hopping_factor(phi_i=0.5, phi_j=0.5, coupling=0.1)
    assert f == pytest.approx(1.0, abs=1e-12)


def test_hopping_factor_zero_coupling_is_one() -> None:
    f = radion_hopping_factor(phi_i=0.0, phi_j=1.0, coupling=0.0)
    assert f == pytest.approx(1.0, abs=1e-12)


def test_hopping_factor_suppression() -> None:
    f = radion_hopping_factor(phi_i=0.0, phi_j=1.0, coupling=1.0)
    assert f == pytest.approx(math.exp(-1.0), rel=1e-12)


def test_hopping_factor_in_0_1() -> None:
    for dphi in (0.0, 0.1, 0.5, 1.0, 2.0):
        f = radion_hopping_factor(0.0, dphi, coupling=KK_RADION_COUPLING)
        assert 0.0 < f <= 1.0


def test_hopping_factor_negative_coupling_raises() -> None:
    with pytest.raises(ValueError, match="coupling λ"):
        radion_hopping_factor(0.0, 1.0, coupling=-1.0)


# ===========================================================================
# curved_hopping_coefficient
# ===========================================================================


def test_curved_hopping_flat_limit() -> None:
    t_ij = curved_hopping_coefficient(1.0, 0.0, 0.0, KK_RADION_COUPLING)
    assert t_ij == pytest.approx(1.0, abs=1e-12)


def test_curved_hopping_suppressed() -> None:
    t_ij = curved_hopping_coefficient(1.0, 0.0, 1.0, 1.0)
    assert t_ij == pytest.approx(math.exp(-1.0), rel=1e-12)


def test_curved_hopping_scales_with_t0() -> None:
    t1 = curved_hopping_coefficient(1.0, 0.0, 0.5, 0.1)
    t2 = curved_hopping_coefficient(2.0, 0.0, 0.5, 0.1)
    assert t2 == pytest.approx(2.0 * t1, rel=1e-12)


def test_curved_hopping_negative_t0_raises() -> None:
    with pytest.raises(ValueError, match="base_t"):
        curved_hopping_coefficient(-1.0, 0.0, 0.0, 0.1)


# ===========================================================================
# CurvedSpaceFHSpec validation
# ===========================================================================


def test_curved_spec_site_mismatch_raises() -> None:
    base = build_fermi_hubbard_chain(4, 1.0, 4.0)
    rf = build_radion_field_uniform(5)  # wrong n_sites
    with pytest.raises(ValueError, match="sites"):
        CurvedSpaceFHSpec(base_lattice=base, radion=rf)


def test_curved_spec_sites_match() -> None:
    base = build_fermi_hubbard_chain(4, 1.0, 4.0)
    rf = build_radion_field_uniform(4)
    spec = CurvedSpaceFHSpec(base_lattice=base, radion=rf)
    assert spec.n_sites == 4


# ===========================================================================
# CurvedFermiHubbardLattice (duck-typing interface)
# ===========================================================================


def _make_curved_chain(n_sites: int = 4, amplitude: float = 0.1) -> CurvedFermiHubbardLattice:
    base = build_fermi_hubbard_chain(n_sites, 1.0, 4.0)
    rf = build_radion_field_sinusoidal(n_sites, amplitude=amplitude)
    spec = CurvedSpaceFHSpec(base_lattice=base, radion=rf)
    return build_fermi_hubbard_curved(spec)


def test_curved_fh_lattice_n_sites() -> None:
    m = _make_curved_chain(4)
    assert m.n_sites == 4


def test_curved_fh_lattice_n_modes() -> None:
    m = _make_curved_chain(4)
    assert m.n_modes == 8


def test_curved_fh_lattice_fermionic_terms_non_empty() -> None:
    m = _make_curved_chain(4)
    terms = m.fermionic_terms()
    assert len(terms) > 0


def test_curved_fh_lattice_flat_limit_matches_flat() -> None:
    """In the flat limit (uniform φ), fermionic terms should equal the flat model."""
    from src.quantum.fermi_hubbard import build_fermi_hubbard_1d

    flat_model = build_fermi_hubbard_1d(2, 1.0, 4.0)
    base = build_fermi_hubbard_chain(2, 1.0, 4.0)
    rf = build_radion_field_uniform(2, phi0=0.0)  # zero spread → f=1
    spec = CurvedSpaceFHSpec(base_lattice=base, radion=rf)
    curved = build_fermi_hubbard_curved(spec)

    flat_terms = sorted(flat_model.fermionic_terms(), key=lambda t: (t.operators, t.coefficient.real))
    curved_terms = sorted(curved.fermionic_terms(), key=lambda t: (t.operators, t.coefficient.real))

    # Same number of terms
    assert len(flat_terms) == len(curved_terms)
    # Same coefficients
    for ft, ct in zip(flat_terms, curved_terms):
        assert ct.coefficient == pytest.approx(ft.coefficient, abs=1e-10)


def test_curved_fh_lattice_hopping_suppressed_by_radion() -> None:
    """Non-uniform radion field should suppress at least one hopping bond."""
    m_flat = _make_curved_chain(4, amplitude=0.0)
    m_curved = _make_curved_chain(4, amplitude=1.0)

    # Collect hopping coefficient magnitudes
    def get_hopping_mags(model: CurvedFermiHubbardLattice) -> list[float]:
        return sorted(set(model.effective_hopping(i, j) for i, j in model.hopping_edges()))

    mags_flat = get_hopping_mags(m_flat)
    mags_curved = get_hopping_mags(m_curved)

    # All flat hoppings equal base_t=1.0
    for h in mags_flat:
        assert h == pytest.approx(1.0, abs=1e-12)
    # At least one curved hopping is suppressed
    assert min(mags_curved) < 1.0 - 1e-6


def test_curved_fh_lattice_mode_index() -> None:
    m = _make_curved_chain(3)
    assert m.mode_index(0, 0) == 0
    assert m.mode_index(2, 1) == 5


def test_curved_fh_lattice_hopping_t_property() -> None:
    m = _make_curved_chain(2)
    assert m.hopping_t == pytest.approx(1.0)


def test_curved_fh_lattice_interaction_u_property() -> None:
    m = _make_curved_chain(2)
    assert m.interaction_u == pytest.approx(4.0)


# ===========================================================================
# kk_curved_spec convenience constructor
# ===========================================================================


def test_kk_curved_spec_n_sites() -> None:
    spec = kk_curved_spec()
    assert spec.n_sites == 12


def test_kk_curved_spec_radion_profile() -> None:
    spec = kk_curved_spec()
    assert spec.radion.profile == "kk_natural"


def test_kk_curved_spec_notes_adjacent_track() -> None:
    spec = kk_curved_spec()
    assert "ADJACENT TRACK" in spec.notes


def test_kk_curved_spec_flat_limit() -> None:
    spec = kk_curved_spec(radion_amplitude=0.0)
    for v in spec.radion.values:
        assert abs(v) < 1e-12


# ===========================================================================
# separation_guard
# ===========================================================================


def test_separation_guard_returns_dict() -> None:
    sg = separation_guard()
    assert isinstance(sg, dict)


def test_separation_guard_toe_score_none() -> None:
    sg = separation_guard()
    assert sg["toe_score_impact"] == "NONE"


def test_separation_guard_hardgate_false() -> None:
    sg = separation_guard()
    assert sg["hardgate"] == "FALSE"


def test_separation_guard_physics_claim_none() -> None:
    sg = separation_guard()
    assert sg["physics_claim"] == "NONE"


def test_separation_guard_message_non_empty() -> None:
    sg = separation_guard()
    assert len(sg["message"]) > 50


# ===========================================================================
# curved_adjacency_report
# ===========================================================================


def test_curved_adjacency_report_keys() -> None:
    m = _make_curved_chain(4)
    r = curved_adjacency_report(m)
    for key in ("geometry", "n_sites", "n_modes", "radion_profile", "radion_coupling",
                "phi_spread", "flat_limit", "status", "separation_guard"):
        assert key in r


def test_curved_adjacency_report_status() -> None:
    m = _make_curved_chain(4)
    r = curved_adjacency_report(m)
    assert "ADJACENT_TRACK" in r["status"]


def test_curved_adjacency_report_flat_limit_false_for_sinusoidal() -> None:
    m = _make_curved_chain(4, amplitude=0.1)
    r = curved_adjacency_report(m)
    assert r["flat_limit"] is False


def test_curved_adjacency_report_flat_limit_true_for_uniform() -> None:
    base = build_fermi_hubbard_chain(4, 1.0, 0.0)
    rf = build_radion_field_uniform(4, phi0=0.0)
    spec = CurvedSpaceFHSpec(base_lattice=base, radion=rf)
    m = build_fermi_hubbard_curved(spec)
    r = curved_adjacency_report(m)
    assert r["flat_limit"] is True
