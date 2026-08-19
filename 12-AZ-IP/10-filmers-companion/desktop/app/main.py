"""
FilmersCompanion — Main FastAPI Application Entry Point
========================================================
Run:
  python -m desktop.app.main               # FastAPI server on :7864
  python -m desktop.app.main --port 8080   # custom port
  python -m desktop.app.main --ui          # Gradio UI
  python -m desktop.app.main --init        # initialise DB only
  python -m desktop.app.main --ask "..."   # ask a question
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# FastAPI app factory
# ---------------------------------------------------------------------------

def create_app():
    """Create and configure the FastAPI application."""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        print("FastAPI not installed. Run: pip install 'fastapi[standard]'")
        sys.exit(1)

    from .config import get_config

    cfg = get_config()

    app = FastAPI(
        title="FilmersCompanion",
        description=(
            "AI-powered film production suite — cinematography, locations, "
            "finance, and AD tools for independent filmmakers."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include module routers
    from .cinematography.router import router as cine_router
    from .locations.router import router as loc_router
    from .finance.router import router as fin_router
    from .ad_suite.router import router as ad_router

    app.include_router(cine_router, prefix="/api")
    app.include_router(loc_router, prefix="/api")
    app.include_router(fin_router, prefix="/api")
    app.include_router(ad_router, prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "filmers-companion", "version": "1.0.0"}

    # Startup: init DB + seed if first run
    @app.on_event("startup")
    def startup():
        from .db.schema import init_db
        from .db.seed import seed_database
        db = cfg.db_path
        first_run = not db.exists() or db.stat().st_size < 4096
        init_db(db)
        if first_run:
            print(f"[FilmersCompanion] Seeding database at {db} ...")
            seed_database(db, verbose=True)
        else:
            print(f"[FilmersCompanion] Database ready: {db}")

    # Mount Gradio UI at /ui
    try:
        import gradio as gr
        from .cinematography.ui import build_cinematography_tab
        from .locations.ui import build_locations_tab
        from .finance.ui import build_finance_tab
        from .ad_suite.ui import build_ad_suite_tab

        with gr.Blocks(title="FilmersCompanion", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🎬 FilmersCompanion\n*AI-powered production suite for independent filmmakers*")
            with gr.Tabs():
                build_cinematography_tab()
                build_locations_tab()
                build_finance_tab()
                build_ad_suite_tab()

                with gr.Tab("🤖 Production Master"):
                    gr.Markdown("## Production Master Agent")
                    master_project_input = gr.Textbox(label="Project ID", value="omega-001")
                    master_question_input = gr.Textbox(
                        label="Ask the Production Master",
                        placeholder="What are my current budget alerts?",
                    )
                    master_btn = gr.Button("Run Health Check + Ask", variant="primary")
                    master_health_output = gr.JSON(label="Health Check")
                    master_answer_output = gr.Textbox(label="Answer", lines=5)

                    def _master(pid: str, question: str):
                        from .agents.master import ProductionMasterAgent
                        from .config import get_config
                        cfg2 = get_config()
                        agent = ProductionMasterAgent()
                        health = agent.check_all(cfg2.db_path, pid)
                        answer = agent.resolve_production(question, cfg2.db_path, pid) if question.strip() else ""
                        return health, answer

                    master_btn.click(
                        fn=_master,
                        inputs=[master_project_input, master_question_input],
                        outputs=[master_health_output, master_answer_output],
                    )

        from gradio.routes import mount_gradio_app
        app = mount_gradio_app(app, demo, path="/ui")
        print("[FilmersCompanion] Gradio UI mounted at /ui")
    except ImportError:
        print("[FilmersCompanion] Gradio not installed — UI disabled")

    return app


# Expose for uvicorn
app = create_app()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="FilmersCompanion — AI Film Production Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m desktop.app.main\n"
            "  python -m desktop.app.main --port 8080\n"
            "  python -m desktop.app.main --ui\n"
            "  python -m desktop.app.main --init\n"
            '  python -m desktop.app.main --ask "What is turnaround?"\n'
        ),
    )
    parser.add_argument("--port", type=int, default=7864)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--ui", action="store_true", help="Launch Gradio UI")
    parser.add_argument("--init", action="store_true", help="Initialise DB and exit")
    parser.add_argument("--ask", metavar="QUESTION", help="Ask a single question (CLI mode)")
    args = parser.parse_args()

    from .config import get_config
    cfg = get_config()

    if args.init:
        from .db.schema import init_db
        from .db.seed import seed_database
        init_db(cfg.db_path)
        seed_database(cfg.db_path, verbose=True)
        print("[FilmersCompanion] Database initialised.")
        return

    if args.ask:
        from .agents.master import ProductionMasterAgent
        agent = ProductionMasterAgent()
        answer = agent.resolve_production(args.ask, cfg.db_path, "omega-001")
        print(answer)
        return

    try:
        import uvicorn
    except ImportError:
        print("uvicorn not installed. Run: pip install uvicorn")
        sys.exit(1)

    print(f"[FilmersCompanion] Starting on http://{args.host}:{args.port}")
    print(f"[FilmersCompanion] API docs: http://localhost:{args.port}/docs")
    print(f"[FilmersCompanion] Gradio UI: http://localhost:{args.port}/ui")
    uvicorn.run(
        "desktop.app.main:app",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
