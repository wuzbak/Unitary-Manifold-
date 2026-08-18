"""
LithosOS — Pydantic API Models
"""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    agent: Optional[str] = None
    context: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    agents_used: list[str]
    question: str

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)

class SearchResponse(BaseModel):
    results: list[dict[str, Any]]
    total: int
    query: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    offline_mode: bool
    db_specimen_count: int

class IdentifyRequest(BaseModel):
    image_base64: Optional[str] = None
    description: Optional[str] = None

class SpecimenCandidateResponse(BaseModel):
    name: str
    common_names: list[str]
    confidence: float
    confidence_label: str
    mineral_class: str
    description: str
    source: str

class IdentifyResponse(BaseModel):
    candidates: list[SpecimenCandidateResponse]
    summary: str
    description_analysis: Optional[str] = None

class SpecimenResponse(BaseModel):
    id: int
    name: str
    common_names: list[str]
    mineral_class: str
    crystal_system: str
    mohs_hardness: float
    composition: str
    description: str
    luster: str
    streak: str
    minerals: list[dict[str, Any]]
    gemstones: list[dict[str, Any]]
    metals: list[dict[str, Any]]
    hazards: list[dict[str, Any]]
    market_data: list[dict[str, Any]]

class SyncRequest(BaseModel):
    since: str = Field("2000-01-01T00:00:00Z")
    tables: list[str] = Field(default_factory=list)

class SyncStatusResponse(BaseModel):
    last_sync: str
    records_updated: int
    records_deleted: int
    errors: list[str]
    completed: bool
