"""TerraOS — Gradio UI (requires gradio package)."""
from __future__ import annotations


def launch_ui(share: bool = False, server_port: int = 7861) -> None:
    try:
        import gradio as gr
    except ImportError:
        print("Install gradio: pip install gradio")
        return

    from terra.app.bot.agents import TerraGovernor

    governor = TerraGovernor()

    def respond(question: str, history: list) -> str:
        result = governor.respond(question)
        return result.answer

    demo = gr.ChatInterface(
        fn=respond,
        title="TerraOS — Soil & Water Expert",
        description="Ask about soil types, pH, water quality, amendments, or remediation.",
    )
    demo.launch(share=share, server_port=server_port)
