# ⬛ LithosOS — Mineral & Gemstone Identifier

**Folder:** `12-AZ-IP/12-lithos-os/`  
**Product:** LithosOS — Mineral and Gemstone Identifier  
**Version:** v1.0  
**Company:** AxiomZero Technologies  
**Status:** Active — functional Gradio desktop application  
**Port:** `http://localhost:7861`

---

## What LithosOS Is

LithosOS is a specialized mineral classification and gemstone diagnostic application. It runs a
dedicated Gradio PC UI and is deployed as part of a cohesive "crust diagnostic loop" alongside
**TerraOS** (soil/water) to form the AxiomZero Earth Science suite.

The application provides:
- **Mineral identification** from description, crystal system, and physical properties
- **Gemstone grading** (color, clarity, cut, carat estimates)
- **Formation context** (igneous, metamorphic, sedimentary origins)
- **Geographic occurrence** mapping based on the Unitary Manifold geological model

---

## Quick Start

```bash
pip install -r requirements.txt
python -m lithic.app.main
# → opens at http://localhost:7861
```

---

## Architecture

```
12-lithos-os/
├── README.md
├── __init__.py
├── requirements.txt         ← pip dependencies
├── app/
│   ├── __init__.py
│   ├── main.py              ← Gradio entry point
│   ├── config.py            ← constants and model paths
│   ├── android/             ← Android companion app
│   ├── api/                 ← REST API layer (FastAPI)
│   ├── bot/                 ← TerraBot TF-IDF retrieval core
│   ├── db/                  ← SQLite mineral catalog
│   ├── models/              ← domain model classes
│   ├── pc/                  ← PC desktop UI modules
│   └── sync/                ← TerraOS sync bridge
├── deploy/
│   ├── install.py           ← automated installer
│   ├── install.sh           ← shell installer
│   └── requirements.txt     ← deploy-only requirements
├── docs/
│   └── ...                  ← user guide and API docs
└── tests/
    ├── __init__.py
    ├── test_api.py
    ├── test_bot.py
    ├── test_db.py
    ├── test_installer.py
    └── test_mineral_guides.py
```

---

## Dependencies

See `requirements.txt`. Core dependencies:
- `gradio` — UI framework
- `fastapi` + `uvicorn` — REST API
- `sqlite3` — mineral database (stdlib)
- `scikit-learn` — TF-IDF retrieval for TerraBot
- `pillow` — image processing for visual identification

---

## Integration with TerraOS

LithosOS shares the `TerraBot` retrieval engine and the Android companion with `11-terra-os`.
Both are part of the AxiomZero Earth Science diagnostic loop.

---

## Co-authorship

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
