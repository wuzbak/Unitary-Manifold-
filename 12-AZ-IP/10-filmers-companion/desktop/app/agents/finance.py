"""
FilmersCompanion — Finance Officer Agent
"""
from __future__ import annotations

from .base import BaseAgent


class FinanceOfficer(BaseAgent):
    """Production finance calculations: budgets, ROI, burn rate, DOOD."""

    def build_budget(self, total: float, custom_pcts: dict | None = None) -> dict:
        """
        Build a budget breakdown.
        Applies Axiom Omega defaults, overrides with custom_pcts, normalises to 100%.
        Returns {category: {pct, amount}}.
        """
        from ..kb.film_kb import BUDGET_ALLOCATION_DEFAULTS

        # Start with defaults
        pcts: dict[str, float] = {k: v["pct"] for k, v in BUDGET_ALLOCATION_DEFAULTS.items()}

        # Apply custom overrides
        if custom_pcts:
            for cat, pct in custom_pcts.items():
                pcts[cat] = float(pct)

        # Normalise to 100%
        total_pct = sum(pcts.values())
        if total_pct > 0:
            pcts = {k: (v / total_pct) * 100.0 for k, v in pcts.items()}

        return {
            cat: {
                "pct": round(pct, 4),
                "amount": round(total * pct / 100.0, 2),
            }
            for cat, pct in pcts.items()
        }

    def calc_roi(
        self,
        total_budget: float,
        projected_revenue: float,
        distribution_pct: float = 0.7,
    ) -> dict:
        """
        Calculate ROI for a film.
        gross_revenue = projected_revenue × distribution_pct  (filmmaker's share)
        net_profit    = gross_revenue - total_budget
        roi_pct       = net_profit / total_budget × 100
        breakeven_multiple = projected_revenue / total_budget
        """
        gross_revenue = projected_revenue * distribution_pct
        net_profit = gross_revenue - total_budget
        roi_pct = (net_profit / total_budget * 100.0) if total_budget > 0 else 0.0
        breakeven_multiple = (projected_revenue / total_budget) if total_budget > 0 else 0.0
        return {
            "total_budget": total_budget,
            "projected_revenue": projected_revenue,
            "distribution_pct": distribution_pct,
            "gross_revenue": round(gross_revenue, 2),
            "net_revenue": round(gross_revenue, 2),  # alias for compatibility
            "net_profit": round(net_profit, 2),
            "roi_pct": round(roi_pct, 4),
            "breakeven_multiple": round(breakeven_multiple, 4),
        }

    def calc_dood(self, shoot_days: int, total_budget: float) -> dict:
        """
        Calculate Day Out Of Days cost summary.
        Returns {dood_per_day, total_budget, shoot_days}.
        """
        if shoot_days <= 0:
            return {"dood_per_day": 0.0, "total_budget": total_budget, "shoot_days": shoot_days}
        dood_per_day = total_budget / shoot_days
        return {
            "dood_per_day": round(dood_per_day, 2),
            "total_budget": total_budget,
            "shoot_days": shoot_days,
        }

    def calc_burn_rate(self, budget_lines: list[dict]) -> dict:
        """
        Calculate current burn rate.
        Returns {total_budgeted, total_actual, pct_used, days_remaining_at_rate}.
        """
        if not budget_lines:
            return {
                "total_budgeted": 0.0,
                "total_actual": 0.0,
                "pct_used": 0.0,
                "days_remaining_at_rate": None,
            }

        total_budgeted = sum(float(b.get("budgeted", 0)) for b in budget_lines)
        total_actual = sum(float(b.get("actual", 0)) for b in budget_lines)
        pct_used = (total_actual / total_budgeted * 100.0) if total_budgeted > 0 else 0.0

        # Days remaining estimate (assume 30-day shoot as context)
        # This is a planning estimate; real use would track calendar
        remaining = total_budgeted - total_actual
        daily_rate = total_actual / 30.0 if total_actual > 0 else None
        days_remaining = (remaining / daily_rate) if daily_rate and daily_rate > 0 else None

        return {
            "total_budgeted": round(total_budgeted, 2),
            "total_actual": round(total_actual, 2),
            "pct_used": round(pct_used, 4),
            "burn_rate_pct": round(pct_used, 4),
            "days_remaining_at_rate": round(days_remaining, 1) if days_remaining is not None else None,
        }

    def budget_alert(self, budget_lines: list[dict], threshold: float = 0.8) -> list[dict]:
        """
        Return categories exceeding the spend threshold.
        threshold=0.8 means 80% of budgeted spent.
        """
        alerts = []
        for line in budget_lines:
            budgeted = float(line.get("budgeted", 0))
            actual = float(line.get("actual", 0))
            if budgeted <= 0:
                continue
            pct = actual / budgeted
            if pct >= threshold:
                alerts.append({
                    "category": line.get("category", "unknown"),
                    "budgeted": budgeted,
                    "actual": actual,
                    "pct_used": round(pct * 100, 2),
                    "over_threshold": True,
                })
        return alerts
