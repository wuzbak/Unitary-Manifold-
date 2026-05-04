# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_non_abelian_orbifold_emergence.py
=============================================
Pillar 148 — Tests for non_abelian_orbifold_emergence.py.

Tests cover:
  - kawamura_parity_from_n_w(): parity matrix from winding
  - su5_breaking_pattern(): SU(5)/Z₂ gauge boson spectrum
  - su5_zero_mode_count(): SM gauge boson counts
  - x_y_boson_mass(): heavy boson mass
  - proton_lifetime_estimate(): proton decay consistency
  - non_abelian_orbifold_closure(): full Pillar 148 report
  - pillar148_summary(): audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.non_abelian_orbifold_emergence import (
    N_W_CANONICAL,
    SU5_RANK,
    SU5_DIM,
    SM_GAUGE_BOSON_COUNT,
    XY_HEAVY_COUNT,
    M_PLANCK_GEV,
    M_PROTON_GEV,
    PROTON_LIFETIME_LIMIT_YR,
    ALPHA_GUT,
    M_GUT_GEV,
    kawamura_parity_from_n_w,
    su5_breaking_pattern,
    su5_zero_mode_count,
    x_y_boson_mass,
    proton_lifetime_estimate,
    non_abelian_orbifold_closure,
    pillar148_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_canonical_is_5(self):
        assert N_W_CANONICAL == 5

    def test_su5_rank_is_4(self):
        assert SU5_RANK == 4

    def test_su5_dim_is_24(self):
        assert SU5_DIM == 24

    def test_sm_gauge_boson_count_is_12(self):
        assert SM_GAUGE_BOSON_COUNT == 12

    def test_xy_heavy_count_is_12(self):
        assert XY_HEAVY_COUNT == 12

    def test_su5_dim_equals_sm_plus_xy(self):
        assert SU5_DIM == SM_GAUGE_BOSON_COUNT + XY_HEAVY_COUNT

    def test_m_planck_order(self):
        assert 1e18 < M_PLANCK_GEV < 1e20

    def test_m_proton_gev(self):
        assert abs(M_PROTON_GEV - 0.93827) < 0.001

    def test_proton_lifetime_limit(self):
        assert PROTON_LIFETIME_LIMIT_YR > 1e33

    def test_alpha_gut_inverse_24(self):
        assert abs(ALPHA_GUT - 1.0 / 24.3) < 0.001

    def test_m_gut_is_gev_scale(self):
        assert 1e15 < M_GUT_GEV < 1e17


# ---------------------------------------------------------------------------
# kawamura_parity_from_n_w
# ---------------------------------------------------------------------------

class TestKawamuraParityFromNw:
    def test_n_w_5_gives_3_plus_2_minus(self):
        p = kawamura_parity_from_n_w(5)
        assert p.count(1) == 3
        assert p.count(-1) == 2

    def test_n_w_5_diagonal(self):
        p = kawamura_parity_from_n_w(5)
        assert p == [1, 1, 1, -1, -1]

    def test_n_w_4_gives_2_plus_2_minus(self):
        p = kawamura_parity_from_n_w(4)
        assert p.count(1) == 2
        assert p.count(-1) == 2

    def test_n_w_6_gives_3_plus_3_minus(self):
        p = kawamura_parity_from_n_w(6)
        assert p.count(1) == 3
        assert p.count(-1) == 3

    def test_n_w_1_gives_1_plus_0_minus(self):
        p = kawamura_parity_from_n_w(1)
        assert p == [1]

    def test_length_equals_n_w(self):
        for nw in [1, 2, 3, 5, 7, 10]:
            assert len(kawamura_parity_from_n_w(nw)) == nw

    def test_all_entries_are_pm1(self):
        for nw in [3, 5, 7]:
            p = kawamura_parity_from_n_w(nw)
            for x in p:
                assert x in (1, -1)

    def test_positive_block_is_ceil_n_over_2(self):
        for nw in [3, 5, 7, 9]:
            p = kawamura_parity_from_n_w(nw)
            assert p.count(1) == math.ceil(nw / 2)

    def test_negative_block_is_floor_n_over_2(self):
        for nw in [3, 5, 7, 9]:
            p = kawamura_parity_from_n_w(nw)
            assert p.count(-1) == nw // 2

    def test_invalid_n_w_raises(self):
        with pytest.raises(ValueError):
            kawamura_parity_from_n_w(0)
        with pytest.raises(ValueError):
            kawamura_parity_from_n_w(-1)


# ---------------------------------------------------------------------------
# su5_breaking_pattern
# ---------------------------------------------------------------------------

class TestSu5BreakingPattern:
    @pytest.fixture
    def pattern_5(self):
        return su5_breaking_pattern(5)

    def test_is_sm_gauge_group(self, pattern_5):
        assert pattern_5["is_sm_gauge_group"] is True

    def test_correct_zero_mode_count(self, pattern_5):
        assert pattern_5["is_correct_zero_mode_count"] is True

    def test_n_zero_modes_is_12(self, pattern_5):
        assert pattern_5["n_zero_modes"] == 12

    def test_n_heavy_bosons_is_12(self, pattern_5):
        assert pattern_5["n_heavy_bosons"] == 12

    def test_su3_generators_is_8(self, pattern_5):
        assert pattern_5["n_su_plus_generators"] == 8  # 3²-1 = 8

    def test_su2_generators_is_3(self, pattern_5):
        assert pattern_5["n_su_minus_generators"] == 3  # 2²-1 = 3

    def test_u1_generators_is_1(self, pattern_5):
        assert pattern_5["n_u1_generators"] == 1

    def test_total_adds_up(self, pattern_5):
        total = (pattern_5["n_su_plus_generators"] +
                 pattern_5["n_su_minus_generators"] +
                 pattern_5["n_u1_generators"])
        assert total == pattern_5["n_zero_modes"]

    def test_zero_plus_heavy_equals_24(self, pattern_5):
        assert pattern_5["n_zero_modes"] + pattern_5["n_heavy_bosons"] == SU5_DIM

    def test_gauge_group_label(self, pattern_5):
        assert "SU(3)" in pattern_5["gauge_group_4d"]
        assert "SU(2)" in pattern_5["gauge_group_4d"]
        assert "U(1)" in pattern_5["gauge_group_4d"]

    def test_n_w_stored(self, pattern_5):
        assert pattern_5["n_w"] == 5

    def test_parity_diagonal_correct(self, pattern_5):
        assert pattern_5["parity_diagonal"] == [1, 1, 1, -1, -1]

    def test_derivation_is_string(self, pattern_5):
        assert isinstance(pattern_5["derivation"], str)

    def test_n_w_4_not_sm(self):
        # n_w=4: P=diag(+1,+1,-1,-1) → SU(2)×SU(2)×U(1) — not SM
        pattern = su5_breaking_pattern(4)
        # n_plus=2, n_minus=2 → SU(2)×SU(2)×U(1)
        assert not pattern["is_sm_gauge_group"]

    def test_invalid_n_w_raises(self):
        with pytest.raises(ValueError):
            su5_breaking_pattern(0)


# ---------------------------------------------------------------------------
# su5_zero_mode_count
# ---------------------------------------------------------------------------

class TestSu5ZeroModeCount:
    @pytest.fixture
    def counts(self):
        return su5_zero_mode_count()

    def test_su3_gluons_is_8(self, counts):
        assert counts["su3_gluons"] == 8

    def test_su2_bosons_is_3(self, counts):
        assert counts["su2_bosons"] == 3

    def test_u1_bosons_is_1(self, counts):
        assert counts["u1_bosons"] == 1

    def test_total_sm_is_12(self, counts):
        assert counts["total_sm"] == 12

    def test_heavy_xy_is_12(self, counts):
        assert counts["heavy_xy"] == 12

    def test_total_plus_heavy_is_24(self, counts):
        assert counts["total_sm"] + counts["heavy_xy"] == SU5_DIM


# ---------------------------------------------------------------------------
# x_y_boson_mass
# ---------------------------------------------------------------------------

class TestXYBosonMass:
    def test_returns_input_at_leading_order(self):
        """M_XY = M_KK at leading order."""
        m_kk = 1000.0
        assert abs(x_y_boson_mass(m_kk) - m_kk) < 1e-8

    def test_positive(self):
        assert x_y_boson_mass(1e3) > 0

    def test_gut_scale_gives_gut_mass(self):
        assert abs(x_y_boson_mass(M_GUT_GEV) - M_GUT_GEV) / M_GUT_GEV < 1e-8

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            x_y_boson_mass(0.0)
        with pytest.raises(ValueError):
            x_y_boson_mass(-100.0)


# ---------------------------------------------------------------------------
# proton_lifetime_estimate
# ---------------------------------------------------------------------------

class TestProtonLifetimeEstimate:
    @pytest.fixture
    def proton(self):
        return proton_lifetime_estimate()

    def test_tau_proton_positive(self, proton):
        assert proton["tau_proton_yr"] > 0

    def test_gut_scale_gives_consistent_lifetime(self, proton):
        """At M_GUT ~ 2×10¹⁶ GeV, proton lifetime should be ~ 10³⁴ yr."""
        assert proton["tau_proton_yr"] > 1e30

    def test_consistent_with_super_k(self, proton):
        """Conservative estimate should be consistent with Super-K."""
        assert proton["consistent"] is True

    def test_experimental_limit_stored(self, proton):
        assert abs(proton["experimental_limit_yr"] - PROTON_LIFETIME_LIMIT_YR) < 1e28

    def test_m_xy_equals_m_gut(self, proton):
        assert abs(proton["M_XY_gev"] - M_GUT_GEV) / M_GUT_GEV < 1e-8

    def test_status_is_string(self, proton):
        assert isinstance(proton["status"], str)

    def test_note_is_string(self, proton):
        assert isinstance(proton["note"], str)

    def test_tev_scale_gives_low_lifetime(self):
        """M_KK ~ 1 TeV → X/Y boson at 1 TeV → proton lifetime far too short."""
        proton_tev = proton_lifetime_estimate(m_kk_gev=1e3)
        assert not proton_tev["consistent"]

    def test_invalid_m_kk_raises(self):
        with pytest.raises(ValueError):
            proton_lifetime_estimate(m_kk_gev=0.0)
        with pytest.raises(ValueError):
            proton_lifetime_estimate(m_kk_gev=-1.0)

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError):
            proton_lifetime_estimate(alpha_gut=0.0)


# ---------------------------------------------------------------------------
# non_abelian_orbifold_closure
# ---------------------------------------------------------------------------

class TestNonAbelianOrbifoldClosure:
    @pytest.fixture
    def closure(self):
        return non_abelian_orbifold_closure()

    def test_pillar_is_148(self, closure):
        assert closure["pillar"] == 148

    def test_resolves_grand_synthesis_open(self, closure):
        assert closure["resolves_grand_synthesis_open"] is True

    def test_status_derived(self, closure):
        assert "DERIVED" in closure["status"]

    def test_chain_has_4_steps(self, closure):
        assert len(closure["chain"]) == 4

    def test_step_1_proved(self, closure):
        assert closure["chain"]["step_1"]["status"] == "PROVED"

    def test_step_2_proved(self, closure):
        assert closure["chain"]["step_2"]["status"] == "PROVED"

    def test_step_3_proved(self, closure):
        assert "PROVED" in closure["chain"]["step_3"]["status"]

    def test_step_4_proved(self, closure):
        assert "PROVED" in closure["chain"]["step_4"]["status"]

    def test_parity_matrix_correct(self, closure):
        assert closure["parity_matrix"] == [1, 1, 1, -1, -1]

    def test_breaking_pattern_is_sm(self, closure):
        assert closure["breaking_pattern"]["is_sm_gauge_group"] is True

    def test_zero_modes_count(self, closure):
        assert closure["zero_modes"]["total_sm"] == 12

    def test_heavy_bosons_count(self, closure):
        assert closure["zero_modes"]["heavy_xy"] == 12

    def test_open_problems_is_list(self, closure):
        assert isinstance(closure["open_problems"], list)
        assert len(closure["open_problems"]) >= 2

    def test_title_is_string(self, closure):
        assert isinstance(closure["title"], str)

    def test_n_w_is_5(self, closure):
        assert closure["n_w"] == 5


# ---------------------------------------------------------------------------
# pillar148_summary
# ---------------------------------------------------------------------------

class TestPillar148Summary:
    @pytest.fixture
    def p148(self):
        return pillar148_summary()

    def test_pillar_is_148(self, p148):
        assert p148["pillar"] == 148

    def test_status_contains_derived(self, p148):
        assert "DERIVED" in p148["status"]

    def test_su3_derived(self, p148):
        assert p148["su3_derived"] is True

    def test_su2_derived(self, p148):
        assert p148["su2_derived"] is True

    def test_u1_derived(self, p148):
        assert p148["u1_derived"] is True

    def test_total_zero_modes_12(self, p148):
        assert p148["total_zero_modes"] == 12

    def test_total_heavy_bosons_12(self, p148):
        assert p148["total_heavy_bosons"] == 12

    def test_chain_steps_proved_is_4(self, p148):
        assert p148["chain_steps_proved"] == 4

    def test_resolves_grand_synthesis(self, p148):
        assert p148["resolves_grand_synthesis_open"] is True

    def test_proton_decay_consistent(self, p148):
        assert p148["proton_decay_consistent"] is True

    def test_key_formula_mentions_su5(self, p148):
        assert "SU(5)" in p148["key_formula"]

    def test_update_for_grand_synthesis_mentions_derived(self, p148):
        assert "DERIVED" in p148["update_for_grand_synthesis"]

    def test_open_problems_list(self, p148):
        assert isinstance(p148["open_problems"], list)
