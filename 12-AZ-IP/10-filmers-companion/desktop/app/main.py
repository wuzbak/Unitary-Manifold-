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
            "AI-powered end-to-end film production suite — script, breakdown, "
            "scheduling, departments, finance, dailies, and producer oversight."
        ),
        version="2.0.0",
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
    from .production_suite.router import router as suite_router

    app.include_router(cine_router, prefix="/api")
    app.include_router(loc_router, prefix="/api")
    app.include_router(fin_router, prefix="/api")
    app.include_router(ad_router, prefix="/api")
    app.include_router(suite_router, prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "filmers-companion", "version": "2.0.0"}

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
        from .production_suite.service import FilmProductionSuiteService

        with gr.Blocks(title="FilmersCompanion", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🎬 FilmersCompanion\n*AI-powered end-to-end production suite for development, prep, shooting, post, and delivery*")
            with gr.Tabs():
                with gr.Tab("🧭 Producer / UPM Dashboard"):
                    dashboard_project_input = gr.Textbox(label="Project ID", value="omega-001")
                    dashboard_btn = gr.Button("Refresh Dashboard", variant="primary")
                    dashboard_output = gr.JSON(label="Dashboard")
                    dashboard_brief = gr.Textbox(label="UPM Brief", lines=8)

                    def _dashboard(pid: str):
                        from .config import get_config

                        service = FilmProductionSuiteService(get_config().db_path)
                        data = service.producer_dashboard(pid)
                        return data, data.get("upm_brief", "")

                    dashboard_btn.click(
                        fn=_dashboard,
                        inputs=[dashboard_project_input],
                        outputs=[dashboard_output, dashboard_brief],
                    )

                with gr.Tab("✍️ Script Studio"):
                    script_project_input = gr.Textbox(label="Project ID", value="omega-dev-001")
                    script_title_input = gr.Textbox(label="Script Title", value="NEW OMEGA FEATURE")
                    script_revision_input = gr.Textbox(label="Revision Name", value="White Draft")
                    script_color_input = gr.Dropdown(
                        ["White", "Blue", "Pink", "Yellow", "Green", "Goldenrod"],
                        value="White",
                        label="Revision Color",
                    )
                    script_content_input = gr.Textbox(
                        label="Plain-Text Screenplay",
                        lines=14,
                        value=(
                            "INT. SAFE HOUSE - NIGHT\n"
                            "NOVA studies the monitor wall while MIRA assembles the disguise kit.\n\n"
                            "EXT. BACK ALLEY - NIGHT\n"
                            "NOVA and MIRA move toward a waiting car as a DRONE circles overhead.\n\n"
                            "INT. PRESS ROOM - DAY\n"
                            "ELIAS prepares the press conference while crew reset the podium."
                        ),
                    )
                    script_import_btn = gr.Button("Import Script + Build Prep Artifacts", variant="primary")
                    script_import_output = gr.JSON(label="Import Summary")
                    script_overview_output = gr.JSON(label="Script Overview")

                    def _import_script(project_id: str, title: str, revision_name: str, revision_color: str, content: str):
                        from .config import get_config

                        service = FilmProductionSuiteService(get_config().db_path)
                        summary = service.import_script_text(
                            project_id=project_id,
                            title=title,
                            content=content,
                            revision_name=revision_name,
                            revision_color=revision_color,
                            replace_existing=True,
                        )
                        return summary, service.script_overview(project_id)

                    script_import_btn.click(
                        fn=_import_script,
                        inputs=[
                            script_project_input,
                            script_title_input,
                            script_revision_input,
                            script_color_input,
                            script_content_input,
                        ],
                        outputs=[script_import_output, script_overview_output],
                    )

                with gr.Tab("🧩 Breakdown + Departments"):
                    breakdown_project_input = gr.Textbox(label="Project ID", value="omega-001")
                    department_input = gr.Dropdown(
                        [
                            "Producing", "UPM / Production", "1st AD", "Script Supervisor",
                            "Camera", "G&E", "Sound", "Art", "Wardrobe", "Hair/Makeup",
                            "Locations", "Transport", "Stunts/SPFX", "VFX",
                            "Editorial/Post", "Legal/Payroll", "Distribution/Marketing",
                        ],
                        value="VFX",
                        label="Department",
                    )
                    breakdown_btn = gr.Button("Refresh Breakdown + Department Board", variant="primary")
                    breakdown_output = gr.JSON(label="Breakdown Summary")
                    department_output = gr.JSON(label="Department Board")

                    def _breakdown(project_id: str, department: str):
                        from .config import get_config

                        service = FilmProductionSuiteService(get_config().db_path)
                        return service.breakdown_summary(project_id), service.department_board(project_id, department)

                    breakdown_btn.click(
                        fn=_breakdown,
                        inputs=[breakdown_project_input, department_input],
                        outputs=[breakdown_output, department_output],
                    )

                with gr.Tab("📅 Scheduling + DOOD"):
                    schedule_project_input = gr.Textbox(label="Project ID", value="omega-001")
                    schedule_btn = gr.Button("Refresh Scheduling", variant="primary")
                    schedule_output = gr.JSON(label="Schedule Overview")
                    dood_output = gr.JSON(label="DOOD")

                    def _schedule(project_id: str):
                        from .config import get_config

                        service = FilmProductionSuiteService(get_config().db_path)
                        return service.schedule_overview(project_id), service.dood_report(project_id)

                    schedule_btn.click(
                        fn=_schedule,
                        inputs=[schedule_project_input],
                        outputs=[schedule_output, dood_output],
                    )

                with gr.Tab("🎞️ Post + Delivery"):
                    post_project_input = gr.Textbox(label="Project ID", value="omega-001")
                    post_btn = gr.Button("Refresh Post / Delivery", variant="primary")
                    post_output = gr.JSON(label="Post Overview")
                    approvals_output = gr.JSON(label="Approvals Queue")

                    def _post(project_id: str):
                        from .config import get_config

                        service = FilmProductionSuiteService(get_config().db_path)
                        return service.post_overview(project_id), service.list_approvals(project_id)

                    post_btn.click(
                        fn=_post,
                        inputs=[post_project_input],
                        outputs=[post_output, approvals_output],
                    )

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
