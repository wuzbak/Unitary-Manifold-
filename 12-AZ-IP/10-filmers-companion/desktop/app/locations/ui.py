"""Locations Gradio UI tab."""
from __future__ import annotations


def build_locations_tab():
    """Build the Locations Gradio tab."""
    try:
        import gradio as gr
    except ImportError:
        return None

    with gr.Tab("📍 Locations") as tab:
        gr.Markdown("## Location Manager")

        with gr.Row():
            project_id_input = gr.Textbox(label="Project ID", value="omega-001")
            load_btn = gr.Button("Load Locations", variant="primary")

        locations_output = gr.JSON(label="Locations")

        def _load(pid: str):
            from ..db.schema import get_conn
            from ..config import get_config
            cfg = get_config()
            with get_conn(cfg.db_path) as conn:
                rows = conn.execute(
                    "SELECT * FROM locations WHERE project_id=?", (pid,)
                ).fetchall()
            return [dict(r) for r in rows]

        load_btn.click(fn=_load, inputs=project_id_input, outputs=locations_output)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Scout Report")
                loc_id_input = gr.Textbox(label="Location ID")
                scout_btn = gr.Button("Generate Scout Report")
                scout_output = gr.Textbox(label="Scout Report", lines=15)

                def _scout(lid: str):
                    from ..db.schema import get_conn
                    from ..config import get_config
                    from ..agents.locations import LocationManager
                    cfg = get_config()
                    with get_conn(cfg.db_path) as conn:
                        row = conn.execute(
                            "SELECT * FROM locations WHERE id=?", (lid,)
                        ).fetchone()
                    if not row:
                        return "Location not found."
                    mgr = LocationManager()
                    return mgr.generate_scout_report(dict(row))

                scout_btn.click(fn=_scout, inputs=loc_id_input, outputs=scout_output)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Permit Status Check")
                permit_project_input = gr.Textbox(label="Project ID", value="omega-001")
                permit_btn = gr.Button("Check Unconfirmed Locations")
                permit_output = gr.JSON(label="Unconfirmed Locations")

                def _permit_check(pid: str):
                    from ..db.schema import get_conn
                    from ..config import get_config
                    from ..agents.locations import LocationManager
                    cfg = get_config()
                    with get_conn(cfg.db_path) as conn:
                        scenes = [dict(r) for r in conn.execute(
                            "SELECT * FROM scenes WHERE project_id=?", (pid,)
                        ).fetchall()]
                        locs = [dict(r) for r in conn.execute(
                            "SELECT * FROM locations WHERE project_id=?", (pid,)
                        ).fetchall()]
                    mgr = LocationManager()
                    return mgr.check_unconfirmed(scenes, locs)

                permit_btn.click(fn=_permit_check, inputs=permit_project_input, outputs=permit_output)

    return tab
