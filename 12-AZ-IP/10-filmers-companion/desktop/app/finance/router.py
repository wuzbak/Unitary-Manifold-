"""Finance router."""
from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/{project_id}/budget-lines")
def list_budget_lines(project_id: str):
    """List all budget lines for a project."""
    from ...config import get_config
    from ...db.schema import get_conn
    cfg = get_config()
    with get_conn(cfg.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM budget_lines WHERE project_id=?", (project_id,)
        ).fetchall()
    return {"budget_lines": [dict(r) for r in rows]}


@router.post("/build-budget")
def build_budget(body: dict):
    """Build a budget breakdown from total and optional custom percentages."""
    from ...agents.finance import FinanceOfficer
    officer = FinanceOfficer()
    total = float(body.get("total", 1_000_000))
    custom = body.get("custom_pcts", {})
    result = officer.build_budget(total, custom)
    return {"budget": result, "total": total}


@router.post("/calc-roi")
def calc_roi(body: dict):
    """Calculate ROI for a project."""
    from ...agents.finance import FinanceOfficer
    officer = FinanceOfficer()
    result = officer.calc_roi(
        total_budget=float(body.get("total_budget", 1_000_000)),
        projected_revenue=float(body.get("projected_revenue", 3_000_000)),
        distribution_pct=float(body.get("distribution_pct", 0.7)),
    )
    return result


@router.get("/{project_id}/burn-rate")
def burn_rate(project_id: str):
    """Calculate current burn rate for a project."""
    from ...config import get_config
    from ...db.schema import get_conn
    from ...agents.finance import FinanceOfficer
    cfg = get_config()
    with get_conn(cfg.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM budget_lines WHERE project_id=?", (project_id,)
        ).fetchall()
    lines = [dict(r) for r in rows]
    officer = FinanceOfficer()
    return officer.calc_burn_rate(lines)


@router.get("/{project_id}/alerts")
def budget_alerts(project_id: str, threshold: float = 0.8):
    """Return budget categories exceeding threshold."""
    from ...config import get_config
    from ...db.schema import get_conn
    from ...agents.finance import FinanceOfficer
    cfg = get_config()
    with get_conn(cfg.db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM budget_lines WHERE project_id=?", (project_id,)
        ).fetchall()
    lines = [dict(r) for r in rows]
    officer = FinanceOfficer()
    return {"alerts": officer.budget_alert(lines, threshold)}
