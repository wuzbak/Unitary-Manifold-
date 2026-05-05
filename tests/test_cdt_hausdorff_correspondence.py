# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 179 — CDT Hausdorff Correspondence."""
import pytest
from src.core.cdt_hausdorff_correspondence import (
    CDT_HAUSDORFF_UV, CDT_HAUSDORFF_UV_ERROR, CDT_HAUSDORFF_UV_ERROR_2SIGMA,
    CDT_HAUSDORFF_IR, N_W, K_CS, PLANCK_LENGTH_M, LISA_LAUNCH_YEAR,
    um_hausdorff_uv, um_hausdorff_ir, cdt_uv_consistency_check,
    hausdorff_interpolation, um_causal_foliation, irreversibility_correspondence,
    cdt_um_hausdorff_audit, pillar177_summary,
)

class TestConstants:
    def test_cdt_uv(self): assert CDT_HAUSDORFF_UV == pytest.approx(1.80, rel=1e-6)
    def test_cdt_1sigma(self): assert CDT_HAUSDORFF_UV_ERROR == pytest.approx(0.25, rel=1e-6)
    def test_2sigma_is_2x(self): assert CDT_HAUSDORFF_UV_ERROR_2SIGMA == pytest.approx(2*CDT_HAUSDORFF_UV_ERROR, rel=1e-9)
    def test_cdt_ir(self): assert CDT_HAUSDORFF_IR == pytest.approx(4.0, rel=1e-6)
    def test_lisa_year(self): assert LISA_LAUNCH_YEAR == 2034

class TestHausdorffDimensions:
    def test_uv_value(self): assert um_hausdorff_uv() == pytest.approx(2.0+N_W/K_CS, rel=1e-9)
    def test_ir_value(self): assert um_hausdorff_ir() == pytest.approx(4.0-N_W/K_CS, rel=1e-9)
    def test_sum_uv_ir(self): assert um_hausdorff_uv()+um_hausdorff_ir() == pytest.approx(6.0, rel=1e-9)
    def test_uv_gt_2(self): assert um_hausdorff_uv() > 2.0
    def test_ir_lt_4(self): assert um_hausdorff_ir() < 4.0

class TestConsistencyCheck:
    def test_is_true(self): assert cdt_uv_consistency_check() is True
    def test_diff_within_2sigma(self): assert abs(um_hausdorff_uv()-CDT_HAUSDORFF_UV) < CDT_HAUSDORFF_UV_ERROR_2SIGMA

class TestInterpolation:
    def test_at_zero(self): assert hausdorff_interpolation(0.0) == pytest.approx(um_hausdorff_uv(), rel=1e-9)
    def test_at_60(self): assert hausdorff_interpolation(60.0) == pytest.approx(um_hausdorff_ir(), rel=1e-9)
    def test_clamped_below(self): assert hausdorff_interpolation(-10.0) == pytest.approx(um_hausdorff_uv(), rel=1e-9)
    def test_clamped_above(self): assert hausdorff_interpolation(100.0) == pytest.approx(um_hausdorff_ir(), rel=1e-9)
    def test_monotone(self): assert hausdorff_interpolation(10.0) < hausdorff_interpolation(20.0)

class TestCausalFoliation:
    def setup_method(self): self.r = um_causal_foliation()
    def test_status(self): assert self.r["status"] == "EQUIVALENT_CAUSAL_STRUCTURE"
    def test_has_equivalence(self): assert isinstance(self.r["equivalence"], str)

class TestIrreversibility:
    def setup_method(self): self.r = irreversibility_correspondence()
    def test_agreement(self): assert self.r["agreement"] is True
    def test_status(self): assert self.r["status"] == "FUNDAMENTAL_ARROW_OF_TIME"

class TestHausdorffAudit:
    def setup_method(self): self.r = cdt_um_hausdorff_audit()
    def test_consistent(self): assert self.r["consistent_2sigma"] is True
    def test_status(self): assert self.r["status"] == "CONSISTENT_WITHIN_2SIGMA"
    def test_lisa_year(self): assert self.r["lisa_year"] == LISA_LAUNCH_YEAR

class TestPillar177Summary:
    def test_returns_string(self): assert isinstance(pillar177_summary(), str)
    def test_contains_177(self): assert "177" in pillar177_summary()
    def test_contains_status(self): assert "CONSISTENT_WITHIN_2SIGMA" in pillar177_summary()
