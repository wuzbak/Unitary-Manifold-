import pytest

from src.core.pillar665_ftheory_dbp_rungs_1_12_combined_certificate_adjacent import (
    ADJACENT_TRACK,
    CL_MIN,
    COMBINED_STATUS,
    FULL_DBP_CLOSURE,
    HONEST_RESIDUALS,
    K_CS,
    N_D3_TADPOLE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    RUNGS_COMPLETED,
    RUNGS_TOTAL,
    VERSION,
    combined_certificate,
    five_d_seed_consistency,
    pillar_report,
    rung_ladder_summary,
    substack_287_draft,
)


class TestConstants:
    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_NUMBER", PILLAR_NUMBER, 665),
            ("RUNGS_COMPLETED", RUNGS_COMPLETED, 12),
            ("RUNGS_TOTAL", RUNGS_TOTAL, 12),
            ("CL_MIN", CL_MIN, 0.917),
            ("K_CS", K_CS, 74),
            ("N_D3_TADPOLE", N_D3_TADPOLE, 75840),
        ],
    )
    def test_numeric_constants(self, name, actual, expected):
        assert actual == pytest.approx(expected, rel=1e-12), f"{name} mismatch"

    @pytest.mark.parametrize(
        ("name", "actual", "expected"),
        [
            ("PILLAR_STATUS", PILLAR_STATUS, "FTHEORY_DBP_RUNGS_1_12_COMBINED_CERTIFICATE_ADJACENT"),
            ("COMBINED_STATUS", COMBINED_STATUS, "RUNGS_1_12_COMPLETE_AT_REFERENCE_CY4"),
            ("VERSION", VERSION, "v21.0"),
        ],
    )
    def test_string_constants(self, name, actual, expected):
        assert actual == expected, f"{name} mismatch"

    def test_boolean_and_residual_constants(self):
        assert ADJACENT_TRACK is True
        assert FULL_DBP_CLOSURE is True
        assert HONEST_RESIDUALS


class TestFunctions:
    def test_combined_certificate(self):
        result = combined_certificate()
        assert result["rungs_completed"] == 12
        assert result["rungs_total"] == 12
        assert result["fraction_complete"] == 1.0
        assert result["full_dbp_closure"] is True
        assert result["honest_residuals"]

    def test_rung_ladder_summary(self):
        result = rung_ladder_summary()
        assert result["completed"] == 12
        assert result["remaining"] == 0
        assert result["remaining_open"] == []
        assert result["full_closure"] is True

    def test_five_d_seed_consistency(self):
        result = five_d_seed_consistency()
        assert result["five_d_metric_seed_preserved"] is True
        assert result["k_cs"] == 74
        assert result["k_cs_preserved"] is True

    def test_substack_287_draft(self):
        result = substack_287_draft()
        assert result["number"] == 287
        assert result["title"] == "F-theory DBP Ladder Complete — 12/12 Rungs at Reference CY4"


class TestReport:
    def test_pillar_report_basics(self):
        report = pillar_report()
        assert report["pillar"] == 665
        assert report["adjacent_track"] is True
        assert report["toe_score_delta"] == 0.0
        assert report["hardgate_score_delta"] == 0.0

    def test_pillar_report_sections(self):
        report = pillar_report()
        for key in (
            "combined_certificate",
            "rung_ladder_summary",
            "five_d_seed_consistency",
            "substack_287_draft",
        ):
            assert key in report
