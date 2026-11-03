"""
LithosOS — Gradio PC UI
"""
from __future__ import annotations

def run_seismicity_query(lat, lon, radius_km, days, min_mag, refresh=False, adapter=None):
    """UI handler: returns (markdown_report, result_dict). Never raises on bad input."""
    from ..sync.usgs_seismicity import (
        SeismicityQuery, SeismicityQueryError, USGSSeismicityAdapter, format_report_markdown,
    )
    if adapter is None:
        from ..config import get_config
        cfg = get_config()
        adapter = USGSSeismicityAdapter(
            db_path=cfg.db_path,
            timeout_s=cfg.seismicity_timeout_s,
            stale_after_s=cfg.seismicity_stale_after_s,
            offline=cfg.offline_mode,
        )
    try:
        q = SeismicityQuery(float(lat), float(lon), float(radius_km), int(days), float(min_mag))
        result = adapter.get_seismicity(q, refresh=bool(refresh))
    except (SeismicityQueryError, TypeError, ValueError) as exc:
        return f"**Invalid query:** {exc}", {}
    return format_report_markdown(result), result.as_dict()


def launch_ui(host: str = "0.0.0.0", port: int = 7861):
    try:
        import gradio as gr
    except ImportError:
        print("Gradio not installed. Run: pip install gradio")
        return

    from ..bot.agents import LithosGovernor
    from ..config import get_config
    cfg = get_config()
    gov = LithosGovernor(api_key=cfg.openai_api_key)

    def seismicity_fn(lat, lon, radius_km, days, min_mag, refresh):
        return run_seismicity_query(lat, lon, radius_km, days, min_mag, refresh)

    def chat_fn(message, history):
        result = gov.route(message)
        return result.answer

    with gr.Blocks(title="LithosOS") as demo:
        gr.Markdown("# 🪨 LithosOS — Mineral & Gemstone Expert")
        with gr.Tab("Ask LithosOS"):
            gr.ChatInterface(chat_fn)
        with gr.Tab("Specimen Search"):
            with gr.Row():
                query = gr.Textbox(label="Search specimens")
                btn = gr.Button("Search")
            results = gr.JSON(label="Results")
            def search_fn(q):
                from ..db.schema import get_conn, search_specimens
                with get_conn(cfg.db_path) as conn:
                    return search_specimens(conn, q)
            btn.click(search_fn, inputs=[query], outputs=[results])
        with gr.Tab("Field Seismicity (USGS, measured)"):
            gr.Markdown(
                "Measured earthquakes near a site from the USGS ComCat catalogue. "
                "Every result shows its data status (live / cached / stale / unavailable) and source time."
            )
            with gr.Row():
                lat_in = gr.Number(label="Latitude", value=38.79)
                lon_in = gr.Number(label="Longitude", value=-122.76)
                radius_in = gr.Number(label="Radius (km)", value=50)
                days_in = gr.Number(label="Days", value=30, precision=0)
                mag_in = gr.Number(label="Min magnitude", value=1.0)
                refresh_in = gr.Checkbox(label="Force refresh", value=False)
            seis_btn = gr.Button("Fetch measured seismicity")
            seis_md = gr.Markdown()
            seis_json = gr.JSON(label="Events + provenance")
            seis_btn.click(
                seismicity_fn,
                inputs=[lat_in, lon_in, radius_in, days_in, mag_in, refresh_in],
                outputs=[seis_md, seis_json],
            )

    demo.launch(server_name=host, server_port=port)
