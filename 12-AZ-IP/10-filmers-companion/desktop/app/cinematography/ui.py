"""Cinematography Gradio UI tab."""
from __future__ import annotations


def build_cinematography_tab():
    """Build the Cinematography Gradio tab."""
    try:
        import gradio as gr
    except ImportError:
        return None

    from ..agents.cinematography import CinematographyAdvisor
    advisor = CinematographyAdvisor()

    with gr.Tab("🎥 Cinematography") as tab:
        gr.Markdown("## Cinematography Advisor")

        with gr.Row():
            with gr.Column():
                synopsis_input = gr.Textbox(
                    label="Scene Synopsis",
                    placeholder="Describe the scene...",
                    lines=3,
                )
                scene_type_input = gr.Dropdown(
                    choices=["drama", "action", "comedy", "thriller", "documentary"],
                    label="Scene Type",
                    value="drama",
                )
                suggest_btn = gr.Button("Suggest Coverage", variant="primary")
                coverage_output = gr.JSON(label="Coverage Suggestions")
                suggest_btn.click(
                    fn=lambda s, t: advisor.suggest_coverage(s, t),
                    inputs=[synopsis_input, scene_type_input],
                    outputs=coverage_output,
                )

        with gr.Row():
            with gr.Column():
                distance_input = gr.Number(label="Subject Distance (ft)", value=10)
                power_input = gr.Number(label="Fixture Power (W)", value=1000)
                lighting_btn = gr.Button("Calculate Lighting")
                lighting_output = gr.JSON(label="Lighting Results")
                lighting_btn.click(
                    fn=lambda d, p: advisor.calc_lighting(d, p),
                    inputs=[distance_input, power_input],
                    outputs=lighting_output,
                )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Shot List Validator")
                shot_list_input = gr.Textbox(
                    label="Shot Coverage Types (comma-separated)",
                    placeholder="master, MS, CU, OTS",
                )
                validate_btn = gr.Button("Validate Shot List")
                validate_output = gr.JSON(label="Validation Result")

                def _validate(types_str: str):
                    shots = [
                        {"coverage_type": t.strip()}
                        for t in types_str.split(",")
                        if t.strip()
                    ]
                    return advisor.validate_shot_list(shots)

                validate_btn.click(
                    fn=_validate,
                    inputs=shot_list_input,
                    outputs=validate_output,
                )

    return tab
