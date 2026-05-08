# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
test_sixd_yukawa_hierarchy_6d.py — Tests for WS-VII: Yukawa Hierarchy from
6D Wavefunction Overlaps.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import pytest

from src.sixd.yukawa_hierarchy_6d import (
    C_L_BOTTOM,
    C_L_ELECTRON,
    C_L_TAU,
    C_L_TOP,
    K_CS,
    PI_KR,
    Y_B_PDG,
    Y_E_PDG,
    Y_T_NORM,
    Y_T_PDG,
    Y_TAU_PDG,
    f_overlap,
    yukawa_hierarchy_table,
    yukawa_hierarchy_ws_vii_report,
    yukawa_prediction,
)


class TestConstants:
    def test_pi_kr(self):
        assert PI_KR == 37.0

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_l_top(self):
        assert C_L_TOP == 0.0

    def test_c_l_bottom_between_top_electron(self):
        assert C_L_TOP < C_L_BOTTOM < C_L_ELECTRON

    def test_c_l_tau_between_bottom_electron(self):
        assert C_L_BOTTOM < C_L_TAU < C_L_ELECTRON

    def test_y_t_pdg(self):
        assert Y_T_PDG == pytest.approx(0.935, rel=1e-6)

    def test_y_b_pdg(self):
        assert Y_B_PDG == pytest.approx(0.024, rel=1e-6)

    def test_y_tau_pdg(self):
        assert Y_TAU_PDG == pytest.approx(0.0102, rel=1e-6)

    def test_y_e_pdg(self):
        assert Y_E_PDG == pytest.approx(2.9e-6, rel=1e-6)

    def test_y_t_norm(self):
        assert Y_T_NORM == pytest.approx(1.0, rel=1e-6)

    def test_hierarchy_pdg_ordering(self):
        assert Y_T_PDG > Y_B_PDG > Y_TAU_PDG > Y_E_PDG


class TestFOverlap:
    def test_returns_float(self):
        assert isinstance(f_overlap(0.0), float)

    def test_non_negative(self):
        for c in [-0.5, -0.2, 0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]:
            assert f_overlap(c) >= 0.0

    def test_ir_localized_large(self):
        # c_L < 0.5 is IR localized → large overlap; c_L > 0.5 is UV → small
        f_ir = f_overlap(0.0)   # c_L=0 is IR localized → large
        f_uv = f_overlap(0.6)   # c_L=0.6 → UV localized → small
        assert f_ir >= f_uv

    def test_uv_localized_suppressed(self):
        # Deep UV localization (c_L >> 0.5) gives strong suppression vs IR
        f_uv = f_overlap(0.9, pi_kr=37.0)
        f_ir = f_overlap(0.0, pi_kr=37.0)
        assert f_uv < f_ir

    def test_boundary_c_l_half(self):
        # c_L = 0.5: should return the flat-space value 1/sqrt(2 pi_kr)
        val = f_overlap(0.5, pi_kr=37.0)
        expected = 1.0 / math.sqrt(2.0 * 37.0)
        assert val == pytest.approx(expected, rel=1e-5)

    def test_finite_for_extreme_uv(self):
        # c_L = 2.0: deep UV localization should give finite (small) value
        val = f_overlap(2.0, pi_kr=37.0)
        assert math.isfinite(val)
        assert val >= 0

    def test_finite_for_extreme_ir(self):
        # c_L = -1.0: deep IR localization
        val = f_overlap(-1.0, pi_kr=37.0)
        assert math.isfinite(val)
        assert val >= 0

    def test_monotone_uv_suppression(self):
        # For c_L > 0.5, increasing c_L → more UV → smaller overlap
        vals = [f_overlap(c, pi_kr=37.0) for c in [0.5, 0.6, 0.7, 0.8]]
        for i in range(len(vals) - 1):
            assert vals[i] >= vals[i + 1]
class TestYukawaPrediction:
    def test_top_normalised_to_one(self):
        ratio = yukawa_prediction(C_L_TOP, c_L_ref=C_L_TOP)
        assert ratio == pytest.approx(1.0, rel=1e-9)

    def test_returns_float(self):
        assert isinstance(yukawa_prediction(0.4), float)

    def test_non_negative(self):
        for c in [0.0, 0.3, 0.5, 0.7]:
            assert yukawa_prediction(c) >= 0.0

    def test_hierarchy_ordering(self):
        # y(top) > y(bottom) > y(tau) > y(electron) for IR→UV c_L ordering
        y_t = yukawa_prediction(C_L_TOP)
        y_b = yukawa_prediction(C_L_BOTTOM)
        y_tau = yukawa_prediction(C_L_TAU)
        y_e = yukawa_prediction(C_L_ELECTRON)
        assert y_t >= y_b >= y_tau >= y_e


class TestYukawaHierarchyTable:
    @pytest.fixture
    def table(self):
        return yukawa_hierarchy_table()

    def test_returns_list(self, table):
        assert isinstance(table, list)

    def test_four_fermions(self, table):
        assert len(table) == 4

    def test_fermion_names(self, table):
        names = {r["fermion"] for r in table}
        assert names == {"top", "bottom", "tau", "electron"}

    def test_expected_keys_per_row(self, table):
        expected = {"fermion", "c_L", "y_pdg", "y_pred", "residual_pct", "status"}
        for row in table:
            assert expected.issubset(row.keys())

    def test_y_pred_finite_positive(self, table):
        for row in table:
            assert math.isfinite(row["y_pred"])
            assert row["y_pred"] > 0

    def test_residual_pct_finite(self, table):
        for row in table:
            assert math.isfinite(row["residual_pct"])

    def test_top_y_pred_order_one(self, table):
        top_row = next(r for r in table if r["fermion"] == "top")
        assert 0.5 <= top_row["y_pred"] <= 2.0

    def test_hierarchy_ordering_table(self, table):
        by_name = {r["fermion"]: r["y_pred"] for r in table}
        assert by_name["top"] >= by_name["bottom"]
        assert by_name["bottom"] >= by_name["tau"]
        assert by_name["tau"] >= by_name["electron"]

    def test_status_constrained(self, table):
        for row in table:
            assert row["status"] == "CONSTRAINED"

    def test_electron_strongly_suppressed(self, table):
        top_row = next(r for r in table if r["fermion"] == "top")
        e_row = next(r for r in table if r["fermion"] == "electron")
        ratio = top_row["y_pred"] / e_row["y_pred"]
        # 6D mechanism suppresses electron relative to top; ratio > 10 at C_L_ELECTRON=0.6
        assert ratio > 10


class TestWsViiReport:
    @pytest.fixture
    def report(self):
        return yukawa_hierarchy_ws_vii_report()

    def test_returns_dict(self, report):
        assert isinstance(report, dict)

    def test_expected_keys(self, report):
        expected = {
            "workstream",
            "title",
            "mechanism_summary",
            "pi_kr",
            "delta_c_l_needed",
            "y_ratio_top_electron_pdg",
            "y_ratio_top_electron_pred",
            "fermion_table",
            "prerequisites",
            "path_to_closure",
            "overall_status",
        }
        assert expected.issubset(report.keys())

    def test_workstream_label(self, report):
        assert report["workstream"] == "WS-VII"

    def test_pi_kr_matches(self, report):
        assert report["pi_kr"] == pytest.approx(PI_KR, rel=1e-6)

    def test_delta_c_l_needed_positive_small(self, report):
        # Should be between 0 and 1
        assert 0 < report["delta_c_l_needed"] < 1.0

    def test_delta_c_l_needed_reasonable(self, report):
        # ln(3.4e5) / (2*37) ≈ 0.172
        assert report["delta_c_l_needed"] == pytest.approx(0.172, abs=0.05)

    def test_y_ratio_pdg_large(self, report):
        assert report["y_ratio_top_electron_pdg"] > 1e5

    def test_y_ratio_pred_finite_positive(self, report):
        assert math.isfinite(report["y_ratio_top_electron_pred"])
        assert report["y_ratio_top_electron_pred"] > 0

    def test_fermion_table_is_list(self, report):
        assert isinstance(report["fermion_table"], list)

    def test_prerequisites_non_empty(self, report):
        assert len(report["prerequisites"]) > 0

    def test_overall_status_constrained(self, report):
        assert "CONSTRAINED" in report["overall_status"]

    def test_mechanism_summary_non_empty(self, report):
        assert len(report["mechanism_summary"]) > 20
