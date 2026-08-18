"""AD Suite Gradio UI tab."""
from __future__ import annotations


def build_ad_suite_tab():
    """Build the AD Suite Gradio tab."""
    try:
        import gradio as gr
    except ImportError:
        return None

    with gr.Tab("📋 AD Suite") as tab:
        gr.Markdown("## Assistant Director Suite")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Turnaround Check")
                wrap_input = gr.Textbox(label="Wrap Time (HH:MM)", value="22:00")
                call_input = gr.Textbox(label="Next Call Time (HH:MM)", value="07:00")
                turnaround_btn = gr.Button("Check Turnaround", variant="primary")
                turnaround_output = gr.JSON(label="Turnaround Result")

                def _check_turnaround(wrap: str, call: str):
                    from ..agents.ad_suite import ADChief
                    ad = ADChief()
                    return ad.check_turnaround(wrap, call)

                turnaround_btn.click(
                    fn=_check_turnaround,
                    inputs=[wrap_input, call_input],
                    outputs=turnaround_output,
                )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Call Sheet Generator")
                cs_project_input = gr.Textbox(label="Project ID", value="omega-001")
                cs_date_input = gr.Textbox(label="Shoot Date", value="2026-06-15")
                cs_btn = gr.Button("Generate Call Sheet")
                cs_output = gr.Textbox(label="Call Sheet", lines=20)

                def _gen_call_sheet(pid: str, date: str):
                    from ..db.schema import get_conn
                    from ..config import get_config
                    from ..agents.ad_suite import ADChief
                    cfg = get_config()
                    with get_conn(cfg.db_path) as conn:
                        scenes = [dict(r) for r in conn.execute(
                            "SELECT * FROM scenes WHERE project_id=? AND shoot_date=?",
                            (pid, date)
                        ).fetchall()]
                        loc_row = conn.execute(
                            "SELECT * FROM locations WHERE project_id=? LIMIT 1", (pid,)
                        ).fetchone()
                    location = dict(loc_row) if loc_row else {}
                    if not scenes:
                        scenes = [{"scene_number": "?", "int_ext": "?", "day_night": "?",
                                   "synopsis": "No scenes for this date.", "page_count": 0}]
                    ad = ADChief()
                    return ad.generate_call_sheet(scenes, location, date)

                cs_btn.click(fn=_gen_call_sheet, inputs=[cs_project_input, cs_date_input], outputs=cs_output)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### One-Liner Scene List")
                ol_project_input = gr.Textbox(label="Project ID", value="omega-001")
                ol_btn = gr.Button("Generate One-Liner")
                ol_output = gr.Textbox(label="One-Liner", lines=15)

                def _one_liner(pid: str):
                    from ..db.schema import get_conn
                    from ..config import get_config
                    from ..agents.ad_suite import ADChief
                    cfg = get_config()
                    with get_conn(cfg.db_path) as conn:
                        scenes = [dict(r) for r in conn.execute(
                            "SELECT * FROM scenes WHERE project_id=?", (pid,)
                        ).fetchall()]
                    ad = ADChief()
                    return ad.generate_one_liner(scenes)

                ol_btn.click(fn=_one_liner, inputs=ol_project_input, outputs=ol_output)

    return tab
