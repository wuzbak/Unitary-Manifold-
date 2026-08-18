"""TerraOS API Pydantic models."""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)


class AskResponse(BaseModel):
    agent: str
    answer: str
    context_chunks: list[str] = []
    confidence: float = 0.8


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=20, ge=1, le=100)


class SearchResult(BaseModel):
    id: int
    name: str
    profile_type: str
    description: Optional[str] = None


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str = "terra-os"
    version: str = "0.1.0"
    db_profile_count: int = 0


class SoilAnalysisRequest(BaseModel):
    ph: Optional[float] = None
    organic_matter_pct: Optional[float] = None
    sand_pct: Optional[float] = None
    silt_pct: Optional[float] = None
    clay_pct: Optional[float] = None
    cec: Optional[float] = None
    notes: Optional[str] = None


class WaterAnalysisRequest(BaseModel):
    ph: Optional[float] = None
    tds_ppm: Optional[float] = None
    hardness_ppm: Optional[float] = None
    nitrate_ppm: Optional[float] = None
    dissolved_o2_ppm: Optional[float] = None
    notes: Optional[str] = None


class AnalysisResponse(BaseModel):
    analysis_type: str
    summary: str
    issues: list[str] = []
    recommendations: list[str] = []
    score: float = 0.0


class ProfileResponse(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str] = None
    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    texture: Optional[str] = None
    organic_matter_pct: Optional[float] = None
    cec: Optional[float] = None
    native_region: Optional[str] = None
    drainage: Optional[str] = None


class AmendmentResponse(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str] = None
    application_rate: Optional[str] = None
    ph_effect: Optional[str] = None


class SyncRequest(BaseModel):
    table: str
    since_ts: Optional[str] = None
    batch_size: int = Field(default=50, ge=1, le=500)


class SyncResponse(BaseModel):
    table: str
    records_synced: int
    status: str = "ok"


class RemediationRequest(BaseModel):
    contaminant_name: str = Field(..., min_length=1)
    concentration_ppm: Optional[float] = None
    medium: str = Field(default="soil")
    budget_range: Optional[str] = None


class RemediationResponse(BaseModel):
    contaminant: str
    recommended_methods: list[dict[str, Any]] = []
    urgency: str = "moderate"
    notes: str = ""
