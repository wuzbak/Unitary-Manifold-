"""
TerraOS — FastAPI Application Factory
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI


def _startup(app: FastAPI) -> None:
    from terra.app.config import get_config
    from terra.app.db.schema import init_db
    from terra.app.db.seed import seed_database
    cfg = get_config()
    init_db(cfg.db_path)
    seed_database(cfg.db_path, verbose=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _startup(app)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="TerraOS",
        description="Soil and water expert system powered by TF-IDF RAG",
        version="0.1.0",
        lifespan=lifespan,
    )
    from terra.app.api.routes import router
    app.include_router(router, prefix="/api/v1")
    return app


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="TerraOS API server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    uvicorn.run("terra.app.main:create_app", host=args.host, port=args.port, reload=args.reload, factory=True)
