"""
LithosOS — Gradio PC UI
"""
from __future__ import annotations

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

    demo.launch(server_name=host, server_port=port)
