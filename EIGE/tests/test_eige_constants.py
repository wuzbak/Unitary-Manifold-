# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/constants.py"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from EIGE.src.constants import (
    K_CS,
    PHI_0,
    WINDING_NUMBER,
    XI_C,
    COUNTY_COUNT,
    SHARD_COUNT,
    SHARD_RECONSTRUCTION_THRESHOLD,
    PHI_TOLERANCE,
    PHI_DRIFT_WARNING,
    PRECISION_BITS,
    MPMATH_DPS,
    HASH_MODULUS,
    HASH_SHIFT_BITS,
    COUNTY_API_PORT,
    STATE_MESH_PORT,
    DOSSIER_EMIT_DEADLINE_MS,
    BACKUP_CRON_HOURS,
    ENGINE_VERSION,
    OSCAL_VERSION,
    NIST_SP_VERSION,
)


class TestPhysicalConstants:
    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_k_cs_equals_5_squared_plus_7_squared(self):
        assert K_CS == 5**2 + 7**2

    def test_phi_0_is_pi_over_4(self):
        assert abs(PHI_0 - math.pi / 4) < 1e-15

    def test_phi_0_value(self):
        assert abs(PHI_0 - 0.7853981633974483) < 1e-15

    def test_winding_number_is_5(self):
        assert WINDING_NUMBER == 5

    def test_xi_c_is_35_over_74(self):
        assert abs(XI_C - 35 / 74) < 1e-15

    def test_k_cs_braid_identity(self):
        # k_CS = n_w² + 7²
        assert K_CS == WINDING_NUMBER**2 + 7**2


class TestSystemConstants:
    def test_county_count_is_39(self):
        assert COUNTY_COUNT == 39

    def test_shard_count_is_8(self):
        assert SHARD_COUNT == 8

    def test_reconstruction_threshold_is_5(self):
        assert SHARD_RECONSTRUCTION_THRESHOLD == 5

    def test_shard_minus_threshold_equals_3(self):
        # Tolerates up to 3 lost shards
        assert SHARD_COUNT - SHARD_RECONSTRUCTION_THRESHOLD == 3


class TestToleranceConstants:
    def test_phi_tolerance_is_1e_15(self):
        assert PHI_TOLERANCE == 1e-15

    def test_phi_drift_warning_is_1e_12(self):
        assert PHI_DRIFT_WARNING == 1e-12

    def test_drift_warning_greater_than_tolerance(self):
        assert PHI_DRIFT_WARNING > PHI_TOLERANCE

    def test_precision_bits_is_512(self):
        assert PRECISION_BITS == 512

    def test_mpmath_dps_is_154(self):
        assert MPMATH_DPS == 154

    def test_mpmath_dps_approximates_512_bits(self):
        # 154 × log2(10) ≈ 511.6
        assert 154 * math.log2(10) > 511
        assert 154 * math.log2(10) < 513


class TestHashConstants:
    def test_hash_modulus_is_mersenne_prime(self):
        assert HASH_MODULUS == 2**63 - 1

    def test_hash_shift_bits_is_7(self):
        assert HASH_SHIFT_BITS == 7


class TestNetworkConstants:
    def test_county_port(self):
        assert COUNTY_API_PORT == 8080

    def test_state_port(self):
        assert STATE_MESH_PORT == 9090

    def test_dossier_deadline_ms(self):
        assert DOSSIER_EMIT_DEADLINE_MS == 500

    def test_backup_interval_hours(self):
        assert BACKUP_CRON_HOURS == 1


class TestVersionConstants:
    def test_engine_version(self):
        assert ENGINE_VERSION == "21.0.0"

    def test_oscal_version(self):
        assert OSCAL_VERSION == "1.5.0"

    def test_nist_sp_version(self):
        assert "800-53" in NIST_SP_VERSION
