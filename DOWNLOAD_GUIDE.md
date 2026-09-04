# Downloading the Unitary Manifold Repository

Canonical status source (always current):  
`https://raw.githubusercontent.com/wuzbak/Unitary-Manifold-/main/9-INFRASTRUCTURE/um_live_status.json`

---

## Option 1 — Direct archive links (no account needed)

- ZIP: `https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip`
- Tarball: `https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.tar.gz`

```bash
curl -L https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip -o unitary-manifold-main.zip
unzip unitary-manifold-main.zip
```

---

## Option 2 — GitHub UI

1. Open `https://github.com/wuzbak/Unitary-Manifold-`
2. Click **Code**
3. Click **Download ZIP**

---

## Option 3 — Build Download Archive workflow

1. Open Actions → **Build Download Archive**
2. Click **Run workflow**
3. Download the generated artifact from the completed run

---

## Option 4 — Clone

```bash
git clone https://github.com/wuzbak/Unitary-Manifold-.git
cd Unitary-Manifold-
```

---

## Verify your copy

```bash
python -m pytest tests/ -q
python -m pytest recycling/ -q
python -m pytest "5-GOVERNANCE/Unitary Pentad/" -q
python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q
```

Use `STATUS.md` and `9-INFRASTRUCTURE/um_live_status.json` as the canonical state surfaces for expected totals.
