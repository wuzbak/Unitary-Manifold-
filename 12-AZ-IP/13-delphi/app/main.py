"""
DelPhi — FastAPI Application Factory + Gradio UI
"""
from __future__ import annotations

import logging
from datetime import date as _date

import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from delphi.app.api.routes import router
from delphi.app.config import get_config
from delphi.app.db.schema import init_db
from delphi.app.db.seed import seed_database
from delphi.app.oracle.astrology import build_astrology_reading
from delphi.app.oracle.chinese_zodiac import build_chinese_zodiac_reading
from delphi.app.oracle.runes import build_rune_reading
from delphi.app.oracle.tarot import build_reading as build_tarot_reading

log = logging.getLogger(__name__)


def _tarot_ui(spread: str, question: str) -> str:
    spread_map = {"Celtic Cross": "celtic_cross", "Three Card": "three_card", "Single Card": "single_card"}
    r = build_tarot_reading(
        question=question,
        spread_type=spread_map.get(spread, "three_card"),
    )
    lines = [f"# 🔮 Tarot Reading — {spread}", f"**Synthesis:** {r['synthesis']}", ""]
    for card in r.get("cards", []):
        lines.append(f"**{card['position_name']}**: {card['card_name']} — {card['keywords']}")
    return "\n".join(lines)


def _rune_ui(spread: str, question: str) -> str:
    spread_map = {"Single": "single", "Three Rune": "three_rune", "Runic Cross": "runic_cross"}
    r = build_rune_reading(
        question=question,
        spread_type=spread_map.get(spread, "three_rune"),
    )
    lines = [f"# ᚠ Rune Reading — {spread}", f"**Synthesis:** {r['synthesis']}", ""]
    for cast in r.get("cast", []):
        rune = cast.get("rune", {})
        pos = cast.get("position", {})
        rev = " *(reversed)*" if rune.get("is_reversed") else ""
        sym = rune.get("symbol", "")
        lines.append(f"**{pos.get('name', '')}**: {sym} {rune.get('name', '')}{rev} — {rune.get('active_meaning', '')}")
    return "\n".join(lines)


def _astrology_ui(birth_date: str, birth_time: str, question: str) -> str:
    r = build_astrology_reading(
        birth_date_str=birth_date or "1990-01-01",
        birth_time_str=birth_time or None,
    )
    sun = r.get("sun_sign", {})
    moon = r.get("moon_sign", {})
    rising = r.get("rising_sign", {})
    lines = [
        "# ♈ Astrology Reading",
        f"**Sun Sign:** {sun.get('name', '')} | **Moon:** {moon.get('name', '')} | "
        f"**Rising:** {rising.get('name', '')}",
        f"**Horoscope:** {r.get('daily_horoscope', '')}",
        f"**Summary:** {r.get('natal_summary', '')}",
    ]
    return "\n".join(lines)


def _zodiac_ui(year_str: str, question: str) -> str:
    try:
        year = int(year_str)
    except ValueError:
        return "⚠️ Please enter a valid year (e.g. 1990)."
    r = build_chinese_zodiac_reading(birth_year=year)
    lines = [
        f"# 🐉 Chinese Zodiac — Year of the {r.get('animal', '')}",
        f"**Element:** {r.get('element')} | **Yin/Yang:** {r.get('yin_yang')}",
        f"**Summary:** {r.get('summary', '')}",
    ]
    return "\n".join(lines)


def build_gradio_app() -> gr.Blocks:
    with gr.Blocks(title="DelPhi Oracle", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🔮 DelPhi — Oracle Divination Suite")
        gr.Markdown("*A 5-oracle divination engine powered by the Unitary Manifold.*")

        with gr.Tab("Tarot"):
            spread_dd = gr.Dropdown(
                ["Celtic Cross", "Three Card", "Single Card"],
                value="Three Card", label="Spread"
            )
            q_tarot = gr.Textbox(label="Your Question", placeholder="What guidance do you seek?")
            btn_tarot = gr.Button("Draw Cards 🃏")
            out_tarot = gr.Markdown()
            btn_tarot.click(_tarot_ui, inputs=[spread_dd, q_tarot], outputs=out_tarot)

        with gr.Tab("Runes"):
            rune_spread = gr.Dropdown(
                ["Single", "Three Rune", "Runic Cross"],
                value="Three Rune", label="Spread"
            )
            q_rune = gr.Textbox(label="Your Question")
            btn_rune = gr.Button("Cast Runes ᚠ")
            out_rune = gr.Markdown()
            btn_rune.click(_rune_ui, inputs=[rune_spread, q_rune], outputs=out_rune)

        with gr.Tab("Astrology"):
            bd = gr.Textbox(label="Birth Date (YYYY-MM-DD)", placeholder="1990-06-15")
            bt = gr.Textbox(label="Birth Time (HH:MM, optional)", placeholder="14:30")
            q_astro = gr.Textbox(label="Your Question")
            btn_astro = gr.Button("Get Reading ♈")
            out_astro = gr.Markdown()
            btn_astro.click(_astrology_ui, inputs=[bd, bt, q_astro], outputs=out_astro)

        with gr.Tab("Chinese Zodiac"):
            yr = gr.Textbox(label="Birth Year", placeholder="1990")
            q_zodiac = gr.Textbox(label="Your Question")
            btn_zodiac = gr.Button("Consult Oracle 🐉")
            out_zodiac = gr.Markdown()
            btn_zodiac.click(_zodiac_ui, inputs=[yr, q_zodiac], outputs=out_zodiac)

    return demo


def create_app() -> FastAPI:
    cfg = get_config()
    logging.basicConfig(level=logging.INFO)

    app = FastAPI(
        title="DelPhi Oracle API",
        description="5-oracle divination engine: Tarot, Runes, Astrology, Chinese Zodiac.",
        version=cfg.version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup_event() -> None:
        log.info("DelPhi startup — initialising database…")
        init_db()
        seed_database()
        log.info("DelPhi ready on port %s", cfg.port)

    gradio_app = build_gradio_app()
    app = gr.mount_gradio_app(app, gradio_app, path="/")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    cfg = get_config()
    uvicorn.run("delphi.app.main:app", host="0.0.0.0", port=cfg.port, reload=False)


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
