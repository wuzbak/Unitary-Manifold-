import pytest

from src.core.pillar663_ftheory_rung12_alpha_prime_np_corrections_adjacent import (
    ADJACENT_TRACK,
    BBHL_RESIDUAL,
    DELTA_G_MAX_FRAC,
    K_CS,
    NP_CORRECTION_STATUS,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    RHO_BRAID,
    VERSION,
    VOL_S_MIN,
    W_NP_AMPLITUDE,
    W_NP_EXPONENT_ARG,
    W_NP_SUPPRESSION,
    braid_invariant_stability,
    flux_backreaction,
    honest_residual,
    nonperturbative_superpotential,
    pillar_report,
)


class TestConstants:
    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_NUMBER", PILLAR_NUMBER, 663),
            ("K_CS", K_CS, 74),
            ("N_W", N_W, 5),
            ("RHO_BRAID", RHO_BRAID, 5 / 74),
            ("W_NP_AMPLITUDE", W_NP_AMPLITUDE, 1.0),
            ("DELTA_G_MAX_FRAC", DELTA_G_MAX_FRAC, 0.008),
        ],
    )
    def test_numeric_constants(self, name, actual, expected):
        assert actual == pytest.approx(expected, rel=1e-12), f"{name} mismatch"

    def test_volume_minimum(self):
        assert VOL_S_MIN == pytest.approx(3.7497811303, abs=0.01)

    def test_exponent_and_suppression_ranges(self):
        assert W_NP_EXPONENT_ARG > 0
        assert 0.5 < W_NP_SUPPRESSION < 1.0
        assert W_NP_SUPPRESSION > 0

    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_STATUS", PILLAR_STATUS, "RUNG12_ALPHA_PRIME_NP_CORRECTIONS_BOUNDED"),
            ("VERSION", VERSION, "v21.0"),
            ("NP_CORRECTION_STATUS", NP_CORRECTION_STATUS, "NAMED_NP_CORRECTION"),
            ("BBHL_RESIDUAL", BBHL_RESIDUAL, "RUNG12_BBHL_OPEN"),
        ],
    )
    def test_string_constants(self, name, actual, expected):
        assert actual == expected, f"{name} mismatch"


class TestFunctions:
    def test_nonperturbative_superpotential(self):
        result = nonperturbative_superpotential()
        assert result["amplitude_A"] == 1.0
        assert result["suppression_factor"] == pytest.approx(W_NP_SUPPRESSION)
        assert result["w_np_over_w_tree"] == pytest.approx(W_NP_SUPPRESSION)
        assert result["status"] == "NAMED_NP_CORRECTION"

    def test_flux_backreaction(self):
        result = flux_backreaction()
        assert result["delta_g_max_frac"] < 0.01
        assert result["k_cs_topological_immune"] is True
        assert result["n_w_topological_immune"] is True
        assert result["metric_correction_bounded"] is True

    def test_braid_invariant_stability(self):
        result = braid_invariant_stability()
        assert result["k_cs_stable"] is True
        assert result["n_w_stable"] is True
        assert result["bbhl_residual"] == BBHL_RESIDUAL

    def test_honest_residual(self):
        result = honest_residual()
        assert result["residual"] == "RUNG12_BBHL_OPEN"
        assert "bbhl" in result["note"].lower()


class TestReport:
    def test_pillar_report_basics(self):
        report = pillar_report()
        assert report["pillar"] == 663
        assert report["adjacent_track"] is True
        assert report["toe_score_delta"] == 0.0
        assert report["hardgate_score_delta"] == 0.0

    def test_pillar_report_sections(self):
        report = pillar_report()
        for key in (
            "nonperturbative_superpotential",
            "flux_backreaction",
            "braid_invariant_stability",
            "honest_residual",
        ):
            assert key in report

