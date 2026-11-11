from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.um_sos_api import create_app as create_core_app
from um_sos.engine.preregistration_store import PreregistrationStore


class PreregistrationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=8, max_length=200)
    authors: List[str]
    hypothesis: str = Field(..., min_length=20, max_length=5000)
    methods: str = Field(..., min_length=20, max_length=10000)
    primary_outcomes: List[str]
    falsification_criteria: str = Field(..., min_length=20, max_length=5000)
    planned_start_date: Optional[date] = None
    related_prediction_id: Optional[str] = Field(default=None, max_length=100)

    @field_validator("title", "hypothesis", "methods", "falsification_criteria")
    @classmethod
    def reject_blank_text(cls, value):
        if not value.strip():
            raise ValueError("field must not be blank")
        return value.strip()

    @field_validator("authors", "primary_outcomes")
    @classmethod
    def reject_blank_items(cls, value):
        if not value or any(not item.strip() for item in value):
            raise ValueError("list must contain non-blank values")
        if len(value) > 10:
            raise ValueError("list must contain no more than 10 values")
        if any(len(item.strip()) > 300 for item in value):
            raise ValueError("list values must be at most 300 characters")
        return [item.strip() for item in value]


def create_app(db_path: Optional[Path] = None) -> FastAPI:
    app = create_core_app()
    store = PreregistrationStore(db_path)
    product_root = Path(__file__).resolve().parents[1]

    @app.get("/", include_in_schema=False)
    def explorer():
        return RedirectResponse("/frontend/")

    @app.post("/api/v1/preregistered/local", status_code=201)
    def add_local_preregistration(payload: PreregistrationInput):
        return store.add(payload.model_dump(mode="json"))

    @app.get("/api/v1/preregistered/local")
    def list_local_preregistrations(limit: int = Query(default=100, ge=1, le=200)):
        records = store.list(limit)
        return {"count": len(records), "records": records}

    for folder in ("frontend", "graph", "registry"):
        app.mount(f"/{folder}", StaticFiles(directory=product_root / folder, html=True), name=folder)

    return app


app = create_app()
