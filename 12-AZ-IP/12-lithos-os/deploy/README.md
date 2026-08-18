# LithosOS — Deployment

## Quick Start

```bash
cd lithic/deploy
python install.py
```

## Options

- `--no-launch` — install only, don't start server
- `--offline` — skip optional downloads
- `--check` — check requirements only
- `--android` — Android/Termux mode

## Manual

```bash
pip install -r requirements.txt
python -m lithic.app.main --port 7861
```
