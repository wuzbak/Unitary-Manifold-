# DelPhi — Multi-Modal Hypothesis Explorer

A five-channel hypothesis exploration engine for the Unitary Manifold project.

## Epistemic honesty disclaimer
- DelPhi does **not** present unverifiable claims as facts.
- Registered outputs should be read with explicit status labels such as HARDGATE, ADJACENT, or OPEN.
- Open observational tests and documented gaps remain visible in every serious interpretation.
- Human judgment stays in the loop; DelPhi is an exploration surface, not an authority.

## Channels
- **Tarot** — symbolic prompt scaffolding for reflective question framing
- **Runes** — symbolic contrast tool for alternative narrative framing
- **Astrology** — calendrical/archetypal prompt surface
- **Chinese Zodiac** — cyclical pattern prompt surface
- **Hypothesis Explorer** — epistemic channel registry for falsifiable UM claims

## Quick Start

```bash
# Install
pip install -r delphi/deploy/requirements.txt

# Seed DB & start server (port 7863)
uvicorn delphi.app.main:app --host 0.0.0.0 --port 7863
```

## API
- `POST /api/v1/reading` — Generate a reading
- `GET  /api/v1/horoscope/{sign}` — Daily horoscope
- `GET  /api/v1/zodiac/{year}` — Chinese zodiac
- `GET  /api/v1/search/tarot?q=...` — FTS5 card search
- `GET  /api/v1/health` — Health check

## Tests (99+)

```bash
python -m pytest delphi/tests/ -q
```

---
*Theory: ThomasCory Walker-Pearson. Code: GitHub Copilot (AI).*
