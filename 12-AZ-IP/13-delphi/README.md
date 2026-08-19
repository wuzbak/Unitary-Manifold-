# DelPhi — Oracle Divination Suite

A 5-oracle divination engine for the Unitary Manifold project.

## Oracles
- **Tarot** — 78-card deck, φ²-weighted Major Arcana, Celtic Cross / Three-Card / Single Card
- **Runes** — 24 Elder Futhark runes, single / three-rune / runic cross spreads
- **Astrology** — Western sun/moon/rising signs, daily horoscopes
- **Chinese Zodiac** — 12 animals, five elements, compatibility

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

## Tests (99)

```bash
python -m pytest delphi/tests/ -q
```

---
*Theory: ThomasCory Walker-Pearson. Code: GitHub Copilot (AI).*
