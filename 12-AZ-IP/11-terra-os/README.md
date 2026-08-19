# TerraOS

**Soil and Water Expert System** — a FastAPI-based RAG application for soil science, water quality, and land remediation.

## Quickstart

```bash
pip install -r terra/requirements.txt
python -m uvicorn terra.app.main:create_app --factory --port 8001
```

## Tests

```bash
python3 -m pytest terra/tests/ -q
```

## Architecture

- **TerraBot**: TF-IDF retrieval from soil/water documentation
- **TerraGovernor**: 5-agent router (SoilAnalyst, WaterChemist, AgronomistAdvisor, EcologyGuide, RemediationOfficer)
- **FastAPI**: REST API with soil analysis, water analysis, amendments, remediation
- **SQLite + FTS5**: Soil profiles + water samples full-text search

## Agents

| Agent | Specialty |
|-------|-----------|
| SoilAnalyst | Texture, structure, nutrients, drainage |
| WaterChemist | pH, TDS, nitrates, potability |
| AgronomistAdvisor | Crops, amendments, sustainable farming |
| EcologyGuide | Ecosystem services, biodiversity, watershed |
| RemediationOfficer | Contamination, cleanup protocols |

## API Endpoints

- `GET /api/v1/` — Health check
- `POST /api/v1/ask` — Expert Q&A
- `POST /api/v1/analyze/soil` — Soil analysis
- `POST /api/v1/analyze/water` — Water analysis
- `GET /api/v1/profile/{id}` — Soil profile detail
- `GET /api/v1/amendments` — Amendment library
- `POST /api/v1/remediation` — Remediation advice
- `POST /api/v1/search` — Full-text search
