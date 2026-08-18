import pytest

from src.core.pillar662_ftheory_rung11_matter_curve_yukawa_weierstrass_adjacent import (
    ADJACENT_TRACK,
    B5_CURVE_DEFORMATION_CLASS,
    BRAID_TOPOLOGICAL_INVARIANT_PRESERVED,
    G_KK_LIMIT,
    MATTER_CURVE_GENUS_WEIERSTRASS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    YUKAWA_NONVANISHING,
    kk_point_localization,
    matter_curve_adjunction,
    pillar_report,
    yukawa_overlap_integral,
)


class TestConstants:
    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_NUMBER", PILLAR_NUMBER, 662),
            ("MATTER_CURVE_GENUS_WEIERSTRASS", MATTER_CURVE_GENUS_WEIERSTRASS, 38),
            ("G_KK_LIMIT", G_KK_LIMIT, 0),
        ],
    )
    def test_numeric_constants(self, name, actual, expected):
        assert actual == expected, f"{name} mismatch"

    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_STATUS", PILLAR_STATUS, "RUNG11_YUKAWA_WEIERSTRASS_CERTIFIED"),
            ("VERSION", VERSION, "v21.0"),
            ("B5_CURVE_DEFORMATION_CLASS", B5_CURVE_DEFORMATION_CLASS, "H2_S_Z"),
        ],
    )
    def test_string_constants(self, name, actual, expected):
        assert actual == expected, f"{name} mismatch"

    def test_boolean_constants(self):
        assert ADJACENT_TRACK is True
        assert YUKAWA_NONVANISHING is True
        assert BRAID_TOPOLOGICAL_INVARIANT_PRESERVED is True


class TestFunctions:
    def test_matter_curve_adjunction(self):
        result = matter_curve_adjunction()
        assert result["genus"] == 38
        assert "Σ₁₀" in result["adjunction_formula"]
        assert "same genus 38" in result["rung10_consistency"]

    def test_kk_point_localization(self):
        result = kk_point_localization()
        assert result["g_kk_limit"] == 0
        assert result["mechanism_valid"] is True
        assert result["b5_deformation_class"] == "H2_S_Z"
        assert result["braid_compatible"] is True

    def test_yukawa_overlap_integral(self):
        result = yukawa_overlap_integral()
        assert result["nonvanishing"] is True
        assert result["e6_enhancement_point"] == "top_quark_Yukawa_locus"
        assert "string software" in result["honest_residual"]


class TestReport:
    def test_pillar_report_basics(self):
        report = pillar_report()
        assert report["pillar"] == 662
        assert report["adjacent_track"] is True
        assert report["toe_score_delta"] == 0.0
        assert report["hardgate_score_delta"] == 0.0

    def test_pillar_report_contains_sections(self):
        report = pillar_report()
        for key in (
            "matter_curve_adjunction",
            "kk_point_localization",
            "yukawa_overlap_integral",
        ):
            assert key in report

