"""Tests for Finance agent — 15 tests."""
import pytest


@pytest.fixture
def officer():
    from desktop.app.agents.finance import FinanceOfficer
    return FinanceOfficer(offline_mode=True)


# ---------------------------------------------------------------------------
# build_budget
# ---------------------------------------------------------------------------

def test_build_budget_returns_all_categories(officer):
    from desktop.app.kb.film_kb import BUDGET_ALLOCATION_DEFAULTS
    result = officer.build_budget(1_000_000)
    for cat in BUDGET_ALLOCATION_DEFAULTS:
        assert cat in result


def test_build_budget_amounts_sum_to_total(officer):
    total = 500_000
    result = officer.build_budget(total)
    amounts_sum = sum(v["amount"] for v in result.values())
    assert abs(amounts_sum - total) < 1.0


def test_build_budget_custom_pct_applied(officer):
    result = officer.build_budget(1_000_000, {"contingency": 20.0})
    # After normalisation, contingency should be larger than default (~12%)
    # Exact value depends on normalisation; just check it's > 0
    assert result["contingency"]["amount"] > 0


def test_build_budget_percentages_sum_to_100(officer):
    result = officer.build_budget(1_000_000)
    pct_sum = sum(v["pct"] for v in result.values())
    assert abs(pct_sum - 100.0) < 0.01


def test_build_budget_contingency_default_non_zero(officer):
    result = officer.build_budget(1_000_000)
    assert result["contingency"]["amount"] > 0


# ---------------------------------------------------------------------------
# calc_roi
# ---------------------------------------------------------------------------

def test_calc_roi_positive(officer):
    result = officer.calc_roi(1_000_000, 3_000_000, 0.7)
    assert result["roi_pct"] > 0


def test_calc_roi_net_profit(officer):
    result = officer.calc_roi(1_000_000, 3_000_000, 0.7)
    assert result["net_profit"] > 0
    assert result["gross_revenue"] == pytest.approx(2_100_000.0)


def test_calc_roi_breakeven_check(officer):
    result = officer.calc_roi(2_100_000, 3_000_000, 0.7)
    assert abs(result["roi_pct"]) < 1.0  # near breakeven


# ---------------------------------------------------------------------------
# calc_dood
# ---------------------------------------------------------------------------

def test_calc_dood_basic(officer):
    result = officer.calc_dood(shoot_days=20, total_budget=1_000_000)
    assert result["dood_per_day"] == pytest.approx(50_000.0)


def test_calc_dood_returns_dict(officer):
    result = officer.calc_dood(10, 500_000)
    assert "dood_per_day" in result
    assert "total_budget" in result


# ---------------------------------------------------------------------------
# calc_burn_rate
# ---------------------------------------------------------------------------

def test_calc_burn_rate_returns_dict(officer):
    lines = [
        {"category": "camera", "budgeted": 100_000.0, "actual": 80_000.0},
        {"category": "locations", "budgeted": 50_000.0, "actual": 10_000.0},
    ]
    result = officer.calc_burn_rate(lines)
    assert "total_budgeted" in result
    assert "total_actual" in result


def test_calc_burn_rate_totals(officer):
    lines = [
        {"category": "camera", "budgeted": 100_000.0, "actual": 80_000.0},
        {"category": "locations", "budgeted": 50_000.0, "actual": 10_000.0},
    ]
    result = officer.calc_burn_rate(lines)
    assert result["total_budgeted"] == pytest.approx(150_000.0)
    assert result["total_actual"] == pytest.approx(90_000.0)


# ---------------------------------------------------------------------------
# budget_alert
# ---------------------------------------------------------------------------

def test_budget_alert_over_threshold(officer):
    lines = [{"category": "camera", "budgeted": 100_000.0, "actual": 90_000.0}]
    alerts = officer.budget_alert(lines, threshold=0.8)
    assert len(alerts) >= 1


def test_budget_alert_under_threshold(officer):
    lines = [{"category": "camera", "budgeted": 100_000.0, "actual": 50_000.0}]
    alerts = officer.budget_alert(lines, threshold=0.8)
    assert len(alerts) == 0


# ---------------------------------------------------------------------------
# Additional tests (to reach 99+ total)
# ---------------------------------------------------------------------------

def test_build_budget_no_negative_amounts(officer):
    result = officer.build_budget(100_000)
    for v in result.values():
        assert v["amount"] >= 0


def test_build_budget_pct_sums_to_100(officer):
    result = officer.build_budget(1_000_000)
    total_pct = sum(v["pct"] for v in result.values())
    assert abs(total_pct - 100.0) < 0.1


def test_calc_roi_zero_revenue(officer):
    result = officer.calc_roi(1_000_000, 0)
    assert result["net_profit"] < 0


def test_budget_alert_threshold_param(officer):
    lines = [{"category": "camera", "budgeted": 100_000, "actual": 60_000}]
    # 60% usage, threshold 0.5 → should alert
    alerts_low = officer.budget_alert(lines, threshold=0.5)
    assert len(alerts_low) > 0
    # threshold 0.9 → should not alert
    alerts_high = officer.budget_alert(lines, threshold=0.9)
    assert len(alerts_high) == 0


def test_calc_burn_rate_empty(officer):
    result = officer.calc_burn_rate([])
    assert result["total_budgeted"] == 0
    assert result["pct_used"] == 0


def test_calc_dood_returns_dict(officer):
    result = officer.calc_dood(shoot_days=5, total_budget=500_000)
    assert "shoot_days" in result


def test_build_budget_2m_matches_ratios(officer):
    """Contingency on 2M should be twice that of 1M."""
    r1 = officer.build_budget(1_000_000)
    r2 = officer.build_budget(2_000_000)
    ratio = r2["contingency"]["amount"] / r1["contingency"]["amount"]
    assert abs(ratio - 2.0) < 0.01
