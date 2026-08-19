"""Finance Gradio UI tab."""
from __future__ import annotations


def build_finance_tab():
    """Build the Finance Gradio tab."""
    try:
        import gradio as gr
    except ImportError:
        return None

    with gr.Tab("💰 Finance") as tab:
        gr.Markdown("## Production Finance")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Budget Builder")
                total_budget_input = gr.Number(label="Total Budget ($)", value=1_000_000)
                build_btn = gr.Button("Build Budget", variant="primary")
                budget_output = gr.JSON(label="Budget Breakdown")

                def _build(total: float):
                    from ..agents.finance import FinanceOfficer
                    officer = FinanceOfficer()
                    return officer.build_budget(total)

                build_btn.click(fn=_build, inputs=total_budget_input, outputs=budget_output)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### ROI Calculator")
                roi_budget_input = gr.Number(label="Total Budget ($)", value=1_000_000)
                roi_revenue_input = gr.Number(label="Projected Revenue ($)", value=3_000_000)
                roi_dist_input = gr.Slider(label="Distribution %", minimum=0.1, maximum=1.0, value=0.7)
                roi_btn = gr.Button("Calculate ROI")
                roi_output = gr.JSON(label="ROI Results")

                def _roi(budget: float, revenue: float, dist: float):
                    from ..agents.finance import FinanceOfficer
                    officer = FinanceOfficer()
                    return officer.calc_roi(budget, revenue, dist)

                roi_btn.click(
                    fn=_roi,
                    inputs=[roi_budget_input, roi_revenue_input, roi_dist_input],
                    outputs=roi_output,
                )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Burn Rate & Alerts")
                burn_project_input = gr.Textbox(label="Project ID", value="omega-001")
                burn_btn = gr.Button("Check Burn Rate")
                burn_output = gr.JSON(label="Burn Rate")
                alert_output = gr.JSON(label="Budget Alerts (>80%)")

                def _burn(pid: str):
                    from ..db.schema import get_conn
                    from ..config import get_config
                    from ..agents.finance import FinanceOfficer
                    cfg = get_config()
                    with get_conn(cfg.db_path) as conn:
                        rows = conn.execute(
                            "SELECT * FROM budget_lines WHERE project_id=?", (pid,)
                        ).fetchall()
                    lines = [dict(r) for r in rows]
                    officer = FinanceOfficer()
                    return officer.calc_burn_rate(lines), officer.budget_alert(lines)

                burn_btn.click(fn=_burn, inputs=burn_project_input, outputs=[burn_output, alert_output])

    return tab
