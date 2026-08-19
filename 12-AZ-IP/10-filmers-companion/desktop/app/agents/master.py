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
        from ..db.schema import get_conn
        from .finance import FinanceOfficer
        from .locations import LocationManager
        from .ad_suite import ADChief

        finance = FinanceOfficer(config=self.config)
        loc_mgr = LocationManager(config=self.config)

        # Load data
        with get_conn(db_path) as conn:
            scenes = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM scenes WHERE project_id=?", (project_id,)
                ).fetchall()
            ]
            locations = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM locations WHERE project_id=?", (project_id,)
                ).fetchall()
            ]
            budget_lines = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM budget_lines WHERE project_id=?", (project_id,)
                ).fetchall()
            ]
            call_sheets = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM call_sheets WHERE project_id=?", (project_id,)
                ).fetchall()
            ]

        # Budget alerts
        budget_alerts = finance.budget_alert(budget_lines)

        # Unconfirmed locations
        unconfirmed = loc_mgr.check_unconfirmed(scenes, locations)

        # Turnaround violations (check consecutive call sheets)
        turnaround_violations = []
        ad = ADChief(config=self.config)
        sorted_sheets = sorted(call_sheets, key=lambda s: s.get("shoot_date", ""))
        for i in range(len(sorted_sheets) - 1):
            current = sorted_sheets[i]
            next_sheet = sorted_sheets[i + 1]
            # Assume 22:00 wrap, check against general_call
            wrap = "22:00"
            call = next_sheet.get("general_call", "07:00") or "07:00"
            result = ad.check_turnaround(wrap, call)
            if result["violation"]:
                turnaround_violations.append({
                    "from_date": current.get("shoot_date"),
                    "to_date": next_sheet.get("shoot_date"),
                    "gap_hours": result["gap_hours"],
                })

        total_issues = len(budget_alerts) + len(unconfirmed) + len(turnaround_violations)
        status = "GREEN" if total_issues == 0 else ("YELLOW" if total_issues < 3 else "RED")

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

        # Try KB first
        kb_results = search_kb(question.lower())
        context = ""
        if kb_results:
            context = "Knowledge Base:\n" + "\n".join(
                f"- {r['content']}" for r in kb_results[:2]
            )

        # Add live DB context
        try:
            from ..db.schema import get_conn
            with get_conn(db_path) as conn:
                scene_count = conn.execute(
                    "SELECT COUNT(*) FROM scenes WHERE project_id=?", (project_id,)
                ).fetchone()[0]
                context += f"\n\nLive DB: {scene_count} scenes in project {project_id}."
        except Exception:
            pass

        return self.resolve(question, context)
