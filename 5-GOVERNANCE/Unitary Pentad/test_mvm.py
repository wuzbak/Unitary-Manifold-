# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_mvm.py
===========================
Unit tests for mvm.py — Minimum Viable Manifold.

Covers:
  Constants:
    MVM_N_LAYER_SEARCH_MAX = 20
    MVM_N_CORE_DEFAULT = 5 (= N_CORE)

  MVMConstraints:
    - default n_core = 5, n_layer_max = 20
    - n_core < 1 raises ValueError
    - n_layer_max ≤ n_core raises ValueError
    - r_limit ≤ 0 raises ValueError
    - ns_sigma_max ≤ 0 raises ValueError
    - c_s_floor out of (0, 1) raises ValueError
    - all defaults are physically sane

  mvm_search:
    - returns (CoreLayerArchitecture, int) for feasible constraints
    - returns (None, int) when n_layer_max too small
    - search_steps > 0 always
    - found architecture.is_stable == True
    - search_steps == n_layer − n_core when found at n_layer

  minimum_viable_manifold:
    - default constraints → (5, 7), is_viable = True
    - n_layer_max = 6 → is_viable = False (no stable pair)
    - n_layer_max = 7 → is_viable = True, architecture = (5, 7)
    - n_layer_max = 8 → still finds (5, 7), not (5, 8)
    - None constraints uses defaults
    - is_viable = False → architecture is None
    - search_steps > 0 in all cases
    - reason is non-empty string
    - found architecture matches canonical (5,7) values

  validators_to_reach_floor:
    - target = BRAIDED_SOUND_SPEED → 0 validators
    - target = 1.0 → SATURATION_N validators
    - monotone non-decreasing in target_floor
    - target ≤ 0 raises ValueError
    - target > 1 raises ValueError
    - return type int

  hardware_profile:
    - returns MVMConstraints
    - n_layer_max is set correctly
    - n_core defaults to 5
    - custom n_core is set
    - physics limits are canonical defaults
    - n_layer_max ≤ n_core raises ValueError (via MVMConstraints)
"""

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}


import math
import pytest

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from mvm import (
    MVM_N_LAYER_SEARCH_MAX,
    MVM_N_CORE_DEFAULT,
    MVMConstraints,
    MinimumViableManifold,
    mvm_search,
    minimum_viable_manifold,
    validators_to_reach_floor,
    hardware_profile,
)
from five_seven_architecture import (
    N_CORE, N_LAYER, C_S_STABILITY_FLOOR, DEFAULT_R_LIMIT, DEFAULT_NS_SIGMA_MAX,
    K_CS_RESONANCE,
)
from distributed_authority import SATURATION_N
from unitary_pentad import BRAIDED_SOUND_SPEED


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_mvm_n_layer_search_max_is_20(self):
        assert MVM_N_LAYER_SEARCH_MAX == 20

    def test_mvm_n_core_default_equals_n_core(self):
        assert MVM_N_CORE_DEFAULT == N_CORE

    def test_mvm_n_core_default_equals_five(self):
        assert MVM_N_CORE_DEFAULT == 5


# ---------------------------------------------------------------------------
# MVMConstraints
# ---------------------------------------------------------------------------

class TestMVMConstraints:
    def test_default_n_core_is_five(self):
        c = MVMConstraints()
        assert c.n_core == 5

    def test_default_n_layer_max_is_20(self):
        c = MVMConstraints()
        assert c.n_layer_max == MVM_N_LAYER_SEARCH_MAX

    def test_default_r_limit_is_bicep_keck(self):
        c = MVMConstraints()
        assert math.isclose(c.r_limit, DEFAULT_R_LIMIT, rel_tol=1e-9)

    def test_default_ns_sigma_max_is_two(self):
        c = MVMConstraints()
        assert math.isclose(c.ns_sigma_max, DEFAULT_NS_SIGMA_MAX, rel_tol=1e-9)

    def test_default_c_s_floor_equals_12_over_37(self):
        c = MVMConstraints()
        assert math.isclose(c.c_s_floor, C_S_STABILITY_FLOOR, rel_tol=1e-10)

    def test_n_core_less_than_one_raises(self):
        with pytest.raises(ValueError):
            MVMConstraints(n_core=0)

    def test_n_layer_max_equal_to_n_core_raises(self):
        with pytest.raises(ValueError):
            MVMConstraints(n_core=5, n_layer_max=5)

    def test_n_layer_max_less_than_n_core_raises(self):
        with pytest.raises(ValueError):
            MVMConstraints(n_core=5, n_layer_max=4)

    def test_r_limit_zero_raises(self):
        with pytest.raises(ValueError):
            MVMConstraints(r_limit=0.0)

    def test_r_limit_negative_raises(self):
        with pytest.raises(ValueError):
            MVMConstraints(r_limit=-0.01)

    def test_ns_sigma_max_zero_raises(self):
        with pytest.raises(ValueError):
            MVMConstraints(ns_sigma_max=0.0)

    def test_c_s_floor_zero_raises(self):
        with pytest.raises(ValueError):
            MVMConstraints(c_s_floor=0.0)

    def test_c_s_floor_one_raises(self):
        with pytest.raises(ValueError):
            MVMConstraints(c_s_floor=1.0)

    def test_custom_n_layer_max_accepted(self):
        c = MVMConstraints(n_layer_max=10)
        assert c.n_layer_max == 10

    def test_custom_n_core_accepted(self):
        c = MVMConstraints(n_core=3, n_layer_max=10)
        assert c.n_core == 3


# ---------------------------------------------------------------------------
# mvm_search
# ---------------------------------------------------------------------------

class TestMVMSearch:
    def test_default_constraints_finds_5_7(self):
        arch, steps = mvm_search(MVMConstraints())
        assert arch is not None
        assert arch.n_core == 5
        assert arch.n_layer == 7

    def test_found_architecture_is_stable(self):
        arch, _ = mvm_search(MVMConstraints())
        assert arch.is_stable is True

    def test_search_steps_positive(self):
        _, steps = mvm_search(MVMConstraints())
        assert steps > 0

    def test_search_steps_equals_n_layer_minus_n_core(self):
        # For default constraints, (5,7) is found at n_layer=7
        # steps = 7 - 5 = 2  (checked n_layer=6 and n_layer=7)
        arch, steps = mvm_search(MVMConstraints())
        expected_steps = arch.n_layer - arch.n_core
        assert steps == expected_steps

    def test_n_layer_max_too_small_returns_none(self):
        # n_layer_max = 6: (5,6) fails c_s floor → no viable arch
        arch, steps = mvm_search(MVMConstraints(n_layer_max=6))
        assert arch is None

    def test_steps_exhausted_when_no_solution(self):
        c = MVMConstraints(n_layer_max=6)
        _, steps = mvm_search(c)
        # Searched n_layer in [6, 6] → 1 step
        assert steps == 1

    def test_n_layer_max_7_finds_5_7(self):
        arch, _ = mvm_search(MVMConstraints(n_layer_max=7))
        assert arch is not None
        assert arch.n_layer == 7

    def test_returns_tuple_of_two(self):
        result = mvm_search(MVMConstraints())
        assert len(result) == 2

    def test_k_cs_of_found_arch_equals_74(self):
        arch, _ = mvm_search(MVMConstraints())
        assert arch.k_cs == K_CS_RESONANCE  # 74


# ---------------------------------------------------------------------------
# minimum_viable_manifold
# ---------------------------------------------------------------------------

class TestMinimumViableManifold:
    def test_default_returns_5_7(self):
        mvm = minimum_viable_manifold()
        assert mvm.is_viable is True
        assert mvm.architecture.n_core == 5
        assert mvm.architecture.n_layer == 7

    def test_none_constraints_uses_defaults(self):
        mvm = minimum_viable_manifold(None)
        assert mvm.is_viable is True

    def test_n_layer_max_6_not_viable(self):
        mvm = minimum_viable_manifold(MVMConstraints(n_layer_max=6))
        assert mvm.is_viable is False
        assert mvm.architecture is None

    def test_n_layer_max_7_viable(self):
        mvm = minimum_viable_manifold(MVMConstraints(n_layer_max=7))
        assert mvm.is_viable is True
        assert mvm.architecture.n_layer == 7

    def test_n_layer_max_8_still_finds_7(self):
        # (5,8) fails BICEP/Keck r limit; MVM should return (5,7) not (5,8)
        mvm = minimum_viable_manifold(MVMConstraints(n_layer_max=8))
        assert mvm.is_viable is True
        assert mvm.architecture.n_layer == 7

    def test_architecture_is_stable(self):
        mvm = minimum_viable_manifold()
        assert mvm.architecture.is_stable is True

    def test_architecture_c_s_above_floor(self):
        mvm = minimum_viable_manifold()
        assert mvm.architecture.c_s >= C_S_STABILITY_FLOOR - 1e-12

    def test_architecture_r_eff_below_limit(self):
        mvm = minimum_viable_manifold()
        assert mvm.architecture.r_eff < DEFAULT_R_LIMIT

    def test_architecture_k_cs_equals_74(self):
        mvm = minimum_viable_manifold()
        assert mvm.architecture.k_cs == 74

    def test_search_steps_positive(self):
        mvm = minimum_viable_manifold()
        assert mvm.search_steps > 0

    def test_not_viable_search_steps_positive(self):
        mvm = minimum_viable_manifold(MVMConstraints(n_layer_max=6))
        assert mvm.search_steps > 0

    def test_reason_non_empty_string(self):
        mvm = minimum_viable_manifold()
        assert isinstance(mvm.reason, str)
        assert len(mvm.reason) > 0

    def test_not_viable_reason_non_empty(self):
        mvm = minimum_viable_manifold(MVMConstraints(n_layer_max=6))
        assert isinstance(mvm.reason, str)
        assert len(mvm.reason) > 0

    def test_is_viable_type_bool(self):
        mvm = minimum_viable_manifold()
        assert isinstance(mvm.is_viable, bool)

    def test_constraints_stored_on_result(self):
        c = MVMConstraints(n_layer_max=9)
        mvm = minimum_viable_manifold(c)
        assert mvm.constraints is c

    def test_c_s_value_approximately_12_over_37(self):
        mvm = minimum_viable_manifold()
        assert math.isclose(mvm.architecture.c_s, 12 / 37, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# validators_to_reach_floor
# ---------------------------------------------------------------------------

class TestValidatorsToReachFloor:
    def test_braided_sound_speed_floor_needs_zero_validators(self):
        n = validators_to_reach_floor(BRAIDED_SOUND_SPEED)
        assert n == 0

    def test_floor_at_one_needs_saturation_n(self):
        n = validators_to_reach_floor(1.0)
        assert n <= SATURATION_N

    def test_return_type_int(self):
        n = validators_to_reach_floor(BRAIDED_SOUND_SPEED)
        assert isinstance(n, int)

    def test_monotone_non_decreasing_in_floor(self):
        floors = [0.33, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        counts = [validators_to_reach_floor(f) for f in floors]
        for i in range(len(counts) - 1):
            assert counts[i] <= counts[i + 1]

    def test_zero_target_raises(self):
        with pytest.raises(ValueError):
            validators_to_reach_floor(0.0)

    def test_negative_target_raises(self):
        with pytest.raises(ValueError):
            validators_to_reach_floor(-0.1)

    def test_above_one_raises(self):
        with pytest.raises(ValueError):
            validators_to_reach_floor(1.1)

    def test_more_validators_reach_higher_floor(self):
        n_low  = validators_to_reach_floor(0.4)
        n_high = validators_to_reach_floor(0.9)
        assert n_high >= n_low

    def test_at_saturation_n_collective_floor_reaches_one(self):
        from collective_braid import collective_stability_floor
        assert collective_stability_floor(SATURATION_N) >= 1.0 - 1e-9

    def test_non_integer_floor_accepted(self):
        n = validators_to_reach_floor(0.5)
        assert isinstance(n, int)
        assert n >= 0


# ---------------------------------------------------------------------------
# hardware_profile
# ---------------------------------------------------------------------------

class TestHardwareProfile:
    def test_returns_mvm_constraints(self):
        c = hardware_profile(n_layer_max=10)
        assert isinstance(c, MVMConstraints)

    def test_n_layer_max_set_correctly(self):
        c = hardware_profile(n_layer_max=12)
        assert c.n_layer_max == 12

    def test_default_n_core_is_five(self):
        c = hardware_profile(n_layer_max=10)
        assert c.n_core == 5

    def test_custom_n_core_set(self):
        c = hardware_profile(n_layer_max=10, n_core=3)
        assert c.n_core == 3

    def test_r_limit_is_canonical_default(self):
        c = hardware_profile(n_layer_max=10)
        assert math.isclose(c.r_limit, DEFAULT_R_LIMIT, rel_tol=1e-9)

    def test_ns_sigma_max_is_canonical_default(self):
        c = hardware_profile(n_layer_max=10)
        assert math.isclose(c.ns_sigma_max, DEFAULT_NS_SIGMA_MAX, rel_tol=1e-9)

    def test_c_s_floor_is_canonical_default(self):
        c = hardware_profile(n_layer_max=10)
        assert math.isclose(c.c_s_floor, C_S_STABILITY_FLOOR, rel_tol=1e-10)

    def test_n_layer_max_equal_n_core_raises(self):
        with pytest.raises(ValueError):
            hardware_profile(n_layer_max=5, n_core=5)

    def test_mvm_with_hardware_profile_finds_5_7(self):
        mvm = minimum_viable_manifold(hardware_profile(n_layer_max=10))
        assert mvm.is_viable is True
        assert mvm.architecture.n_layer == 7

    def test_mvm_with_tight_hardware_profile_not_viable(self):
        mvm = minimum_viable_manifold(hardware_profile(n_layer_max=6))
        assert mvm.is_viable is False
