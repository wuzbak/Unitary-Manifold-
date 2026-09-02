"""
FilmersCompanion — Production Master Agent
============================================
Cross-module orchestrator that runs all health checks.
"""
from __future__ import annotations

from pathlib import Path

from .base import BaseAgent


class ProductionMasterAgent(BaseAgent):
    """Runs all cross-module checks and answers production questions."""

    def check_all(self, db_path: Path, project_id: str) -> dict:
        """Run all cross-module checks. Returns health summary dict."""
        from ..production_suite.service import FilmProductionSuiteService

        dashboard = FilmProductionSuiteService(db_path).producer_dashboard(project_id)
        budget_alerts = dashboard["finance"]["alerts"]
        unconfirmed = dashboard["locations"]["unconfirmed"]
        turnaround_violations = dashboard["schedule"]["turnaround_risks"]
        total_issues = len(budget_alerts) + len(unconfirmed) + len(turnaround_violations)
        status = dashboard["status"]

        return {
            "project_id": project_id,
            "turnaround_violations": turnaround_violations,
            "budget_alerts": budget_alerts,
            "unconfirmed_locations": unconfirmed,
            "total_issues": total_issues,
            "status": status,
        }

    def resolve_production(self, question: str, db_path: Path, project_id: str) -> str:
        """Answer a production question using KB + live DB state."""
        from ..kb.film_kb import search_kb
        from ..production_suite.service import FilmProductionSuiteService

        # Try KB first
        kb_results = search_kb(question.lower())
        context = ""
        if kb_results:
            context = "Knowledge Base:\n" + "\n".join(
                f"- {r['content']}" for r in kb_results[:2]
            )

        # Add live DB context
        try:
            dashboard = FilmProductionSuiteService(db_path).producer_dashboard(project_id)
            summary = dashboard["summary"]
            context += (
                f"\n\nLive DB: {summary['scenes']} scenes, {summary['shoot_days']} shoot day(s), "
                f"{summary['pending_approvals']} pending approval(s), "
                f"budget burn {summary['budget_burn_pct']:.2f}%."
            )
            if dashboard["alerts"]:
                context += "\nAlerts:\n" + "\n".join(f"- {alert}" for alert in dashboard["alerts"][:5])
        except Exception:
            pass

        return self.resolve(question, context)
