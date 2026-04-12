"""
Gradio chat UI for the Unitary Manifold RAG Bot.
Deploy to HuggingFace Spaces (Gradio SDK).
"""

from __future__ import annotations

import os

import gradio as gr

from bot import UnifiedBot

# ---------------------------------------------------------------------------
# Welcome message shown in the chat history on load
# ---------------------------------------------------------------------------
WELCOME = """👋 **Welcome to the Unitary Manifold Assistant!**

I'm an expert on ThomasCory Walker-Pearson's **5D Kaluza-Klein gauge-geometric framework** — a theory that derives the Second Law of Thermodynamics as a geometric identity.

**Key resources:**
- 📘 Repository: [github.com/wuzbak/Unitary-Manifold-](https://github.com/wuzbak/Unitary-Manifold-)
- 📄 Theory summary: `MCP_INGEST.md`
- 🔬 Plain-language overview: `WHAT_THIS_MEANS.md`

Enter your OpenAI API key in the sidebar to get started, or try an example question below."""

EXAMPLE_QUESTIONS = [
    "What is the core claim of the Unitary Manifold?",
    "What is α and how is it derived?",
    "What are the key predictions and how can they be falsified?",
    "How does the FTUM work?",
    "What gaps does the theory honestly acknowledge?",
]


# ---------------------------------------------------------------------------
# Chat function
# ---------------------------------------------------------------------------

def respond(
    message: str,
    history: list[tuple[str, str]],
    api_key: str,
):
    """Gradio chat function: returns (history, "")."""
    key = api_key.strip() or os.getenv("OPENAI_API_KEY", "")
    if not key:
        history = history + [
            (
                message,
                "⚠️ No OpenAI API key provided. Please enter your key in the "
                "**API Key** field on the left, or set the `OPENAI_API_KEY` "
                "environment variable.",
            )
        ]
        return history, ""

    bot = UnifiedBot(api_key=key)
    answer = bot.ask(message)
    history = history + [(message, answer)]
    return history, ""


# ---------------------------------------------------------------------------
# Build UI
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="Unitary Manifold Assistant",
    theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"),
) as demo:
    gr.Markdown(
        """# 🌌 Unitary Manifold Assistant
        Ask questions about ThomasCory Walker-Pearson's 5D gauge-geometric framework"""
    )

    with gr.Row():
        with gr.Column(scale=1, min_width=260):
            gr.Markdown("### Settings")
            api_key_box = gr.Textbox(
                label="OpenAI API Key",
                placeholder="sk-...",
                type="password",
                info="Your key is never stored. It is sent directly to OpenAI.",
            )
            gr.Markdown(
                "Don't have a key? Get one at "
                "[platform.openai.com](https://platform.openai.com/api-keys)."
            )
            gr.Markdown("---")
            gr.Markdown("### About")
            gr.Markdown(
                "**Theory**: Second Law of Thermodynamics as a geometric identity "
                "in a 5D Kaluza-Klein manifold.\n\n"
                "**Author**: ThomasCory Walker-Pearson (2026)\n\n"
                "**Repo**: [GitHub](https://github.com/wuzbak/Unitary-Manifold-)"
            )

        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                value=[(None, WELCOME)],
                label="Unitary Manifold Assistant",
                height=520,
                show_copy_button=True,
            )
            with gr.Row():
                msg_box = gr.Textbox(
                    placeholder="Ask a question about the theory, equations, Python API…",
                    label="",
                    scale=9,
                    container=False,
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)

            gr.Markdown("**Example questions:**")
            gr.Examples(
                examples=EXAMPLE_QUESTIONS,
                inputs=msg_box,
                label="",
            )

    # Wire up submit actions
    send_btn.click(
        respond,
        inputs=[msg_box, chatbot, api_key_box],
        outputs=[chatbot, msg_box],
    )
    msg_box.submit(
        respond,
        inputs=[msg_box, chatbot, api_key_box],
        outputs=[chatbot, msg_box],
    )

if __name__ == "__main__":
    demo.launch(show_error=True)
