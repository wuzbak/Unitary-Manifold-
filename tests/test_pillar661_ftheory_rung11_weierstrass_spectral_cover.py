import pytest

from src.core.pillar661_ftheory_rung11_weierstrass_spectral_cover_adjacent import (
    ADJACENT_TRACK,
    E6_ENHANCEMENT_POINT,
    K_CS,
    MONODROMY_TWIST_RHO,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SPECTRAL_COVER_DEGREE,
    VERSION,
    WEIERSTRASS_ALPHA_PRIME_RESIDUAL,
    discriminant_locus,
    global_sections_weierstrass,
    honest_residual,
    pillar_report,
    spectral_cover_polynomial,
)


class TestConstants:
    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_NUMBER", PILLAR_NUMBER, 661),
            ("N_W", N_W, 5),
            ("K_CS", K_CS, 74),
            ("SPECTRAL_COVER_DEGREE", SPECTRAL_COVER_DEGREE, 5),
            ("MONODROMY_TWIST_RHO", MONODROMY_TWIST_RHO, 5 / 74),
        ],
    )
    def test_numeric_constants(self, name, actual, expected):
        assert actual == pytest.approx(expected, rel=1e-12), f"{name} mismatch"

    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_STATUS", PILLAR_STATUS, "RUNG11_WEIERSTRASS_SPECTRAL_COVER_GENERALISED"),
            ("VERSION", VERSION, "v21.0"),
            ("E6_ENHANCEMENT_POINT", E6_ENHANCEMENT_POINT, "top_quark_Yukawa_locus"),
            ("WEIERSTRASS_ALPHA_PRIME_RESIDUAL", WEIERSTRASS_ALPHA_PRIME_RESIDUAL, "OFF_SHELL_ALPHA_PRIME_CUBIC_OPEN"),
        ],
    )
    def test_string_constants(self, name, actual, expected):
        assert actual == expected, f"{name} mismatch"

    def test_flags(self):
        assert ADJACENT_TRACK is True
        assert "Weierstrass Spectral Cover" in PILLAR_TITLE


class TestFunctions:
    def test_discriminant_dict_has_required_keys(self):
        result = discriminant_locus()
        for key in (
            "discriminant_formula",
            "e6_enhancement_survives",
            "monodromy_twist",
            "spectral_cover_degree",
            "honest_residual",
        ):
            assert key in result

    def test_e6_survives(self):
        result = discriminant_locus()
        assert result["e6_enhancement_survives"] is True
        assert result["e6_enhancement_point"] == E6_ENHANCEMENT_POINT

    def test_global_sections_positive_for_all_k(self):
        result = global_sections_weierstrass()
        assert result["positive_for_all_k"] is True
        for k in (2, 3, 4, 5):
            assert result["h0_values"][k] > 0

    def test_global_sections_consistent_with_rung10(self):
        result = global_sections_weierstrass()
        assert result["rung10_consistency"] == "CONSISTENT"
        assert "positivity" in result["comparison_rung10"]

    def test_spectral_cover_degree_five(self):
        result = spectral_cover_polynomial()
        assert result["degree"] == 5
        assert len(result["coefficients_symbolic"]) == 6

    def test_braid_monodromy_compatible(self):
        result = spectral_cover_polynomial()
        assert result["su5_breaking_consistent"] is True
        assert result["braid_monodromy_compatible"] is True

    def test_honest_residual_mentions_alpha_prime(self):
        result = honest_residual()
        assert "ALPHA_PRIME" in result["residual"]
        assert "alpha-prime" in result["note"].lower()


class TestReport:
    def test_pillar_report_structure(self):
        report = pillar_report()
        assert report["pillar"] == 661
        assert report["adjacent_track"] is True
        assert report["toe_score_delta"] == 0.0
        assert report["hardgate_score_delta"] == 0.0

    def test_pillar_report_sections(self):
        report = pillar_report()
        for key in (
            "discriminant_locus",
            "global_sections_weierstrass",
            "spectral_cover_polynomial",
            "honest_residual",
        ):
            assert key in report

