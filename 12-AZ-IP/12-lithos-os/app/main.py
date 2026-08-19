"""
LithosOS — Main FastAPI Application
"""
from __future__ import annotations
import argparse
import sys

def create_app():
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        print("FastAPI not installed. Run: pip install 'fastapi[standard]'")
        sys.exit(1)

    from .config import get_config
    cfg = get_config()

    app = FastAPI(
        title="LithosOS",
        description="Mineral, gemstone, and metallurgy expert system.",
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

    from .api.routes import router
    app.include_router(router, prefix="/api/v1")

    @app.on_event("startup")
    def startup():
        from .db.schema import init_db
        from .db.seed import seed_database
        db = cfg.db_path
        first_run = not db.exists() or db.stat().st_size < 4096
        init_db(db)
        if first_run:
            seed_database(db, verbose=True)

    return app

app = create_app()

def main():
    parser = argparse.ArgumentParser(description="LithosOS — Mineral Expert System")
    parser.add_argument("--port", type=int, default=7861)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--ui", action="store_true")
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--ask", type=str)
    args = parser.parse_args()

    from .config import get_config
    cfg = get_config()

    if args.init:
        from .db.schema import init_db
        from .db.seed import seed_database
        init_db(cfg.db_path)
        seed_database(cfg.db_path)
        return

    if args.ask:
        from .bot.agents import LithosGovernor
        gov = LithosGovernor(api_key=cfg.openai_api_key)
        result = gov.route(args.ask)
        print(result.answer)
        return

    if args.ui:
        from .pc.gradio_ui import launch_ui
        launch_ui(args.host, args.port)
        return

    try:
        import uvicorn
        uvicorn.run("lithic.app.main:app", host=args.host, port=args.port, reload=False)
    except ImportError:
        print("uvicorn not installed. Run: pip install uvicorn")

if __name__ == "__main__":
    main()
