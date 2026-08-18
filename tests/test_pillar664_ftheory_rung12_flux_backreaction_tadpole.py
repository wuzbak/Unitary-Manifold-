import pytest

from src.core.pillar664_ftheory_rung12_flux_backreaction_tadpole_adjacent import (
    ADJACENT_TRACK,
    ALPHA_PRIME_ORDER,
    DELTA_N_D3_MAX_FRAC,
    G4_G4_INNER,
    G4_QUANTIZATION_ROBUST,
    N_D3_TADPOLE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    RUNG12_CERTIFICATE_STATUS,
    VERSION,
    flux_quantization_robustness,
    pillar_report,
    rung12_closure_certificate,
    tadpole_correction,
)


class TestConstants:
    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_NUMBER", PILLAR_NUMBER, 664),
            ("N_D3_TADPOLE", N_D3_TADPOLE, 75840),
            ("G4_G4_INNER", G4_G4_INNER, 1850),
            ("ALPHA_PRIME_ORDER", ALPHA_PRIME_ORDER, 3),
            ("DELTA_N_D3_MAX_FRAC", DELTA_N_D3_MAX_FRAC, 0.002),
        ],
    )
    def test_numeric_constants(self, name, actual, expected):
        assert actual == pytest.approx(expected, rel=1e-12), f"{name} mismatch"

    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_STATUS", PILLAR_STATUS, "RUNG12_COMPLETE_WITH_NAMED_RESIDUALS"),
            ("RUNG12_CERTIFICATE_STATUS", RUNG12_CERTIFICATE_STATUS, "RUNG12_COMPLETE_WITH_NAMED_RESIDUALS"),
            ("VERSION", VERSION, "v21.0"),
        ],
    )
    def test_string_constants(self, name, actual, expected):
        assert actual == expected, f"{name} mismatch"

    def test_boolean_constants(self):
        assert ADJACENT_TRACK is True
        assert G4_QUANTIZATION_ROBUST is True


class TestFunctions:
    def test_tadpole_correction(self):
        result = tadpole_correction()
        assert result["n_d3_nominal"] == 75840
        assert result["delta_n_d3_max_frac"] <= 0.002
        assert result["tadpole_stable"] is True

    def test_flux_quantization_robustness(self):
        result = flux_quantization_robustness()
        assert result["topological_protection"] is True
        assert result["continuous_correction_cannot_disturb"] is True
        assert result["rung10_consistency"] == "preserved"

    def test_rung12_closure_certificate(self):
        result = rung12_closure_certificate()
        assert result["status"] == RUNG12_CERTIFICATE_STATUS
        assert result["braid_k_cs_survives_to_full_np_level"] is True
        assert result["n_w_survives"] is True
        assert result["5d_metric_seed_preserved"] is True
        assert result["ftheory_dbp_completion_at_reference_cy4"] is True
        assert result["named_residuals"]


class TestReport:
    def test_pillar_report_basics(self):
        report = pillar_report()
        assert report["pillar"] == 664
        assert report["adjacent_track"] is True
        assert report["toe_score_delta"] == 0.0
        assert report["hardgate_score_delta"] == 0.0

    def test_pillar_report_sections(self):
        report = pillar_report()
        for key in (
            "tadpole_correction",
            "flux_quantization_robustness",
            "rung12_closure_certificate",
        ):
            assert key in report

