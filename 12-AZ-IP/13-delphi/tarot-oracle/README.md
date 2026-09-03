# TarotOracle

**Unitary Manifold–seeded Celtic Cross tarot reading engine.**  
AxiomZero Technologies / ThomasCory Walker-Pearson — 2026

---

## What This Is

A reproducible tarot reading system grounded in the constants of the Unitary Manifold
framework. Every reading is:

- **Deterministic per question/user/date** — the same inputs always produce the same draw
- **Permanently recorded** — structured JSON + human-readable Markdown, never overwritten
- **Physically motivated** — Major Arcana are weighted at ×φ² relative to Minor Arcana,
  encoding the higher-dimensional Kaluza-Klein excitation density

This is the **H operator** (holographic) applied to the oracle itself: every reading is
permanently encoded, nothing is lost, the field grows denser with use.

---

## Mathematical Grounding

### Seed construction

```python
PHI0  = 1.6180339887448950   # φ₀ — FTUM radion fixed point (golden ratio)
ALPHA = 1.0 / PHI0 ** 2     # α = φ₀⁻² ≈ 0.38197 — KK nonminimal coupling

seed_str = f"{PHI0:.15f}{ALPHA:.15f}{question}{user_id}{date}"
seed_int = int(sha256(seed_str).hexdigest(), 16) % (2**32)
```

φ₀ is not arbitrary — it is the fixed-point value of the radion field in the Unitary
Manifold's FTUM operator. α = φ₀⁻² is the nonminimal coupling derived from the
Kaluza-Klein cross-block curvature. See `Unitary-Manifold/MCP_INGEST.md`.

### Draw weighting

```python
weights = np.ones(78)
weights[:22] *= PHI0 ** 2   # Major Arcana: weight ≈ 2.618
weights /= weights.sum()
cards = rng.choice(78, size=10, replace=False, p=weights)
```

Major Arcana (indices 0–21) carry ×φ² more probability per card than Minor Arcana.
This encodes the physical intuition that higher-dimensional KK modes carry more energy
per degree of freedom than four-dimensional modes. At 22 Majors and 56 Minors:

- Unnormalized Major probability per card: φ² ≈ 2.618
- Unnormalized Minor probability per card: 1.0
- Expected Major Arcana in a 10-card draw: ≈ 4.2 (vs. ≈ 2.8 in a flat draw)

### Celtic Cross → Unitary Manifold position map

| Position | Name | Manifold analog |
|---|---|---|
| 1 | Present | Ψ_n — current field state |
| 2 | Challenge | ∇_μ J^μ_inf = 0 — conservation constraint |
| 3 | Root | T operator — topological invariant, winding number |
| 4 | Past | I operator — irreversible sector, permanent record |
| 5 | Crown | H operator — holographic projection, boundary encoding |
| 6 | Future | Ψ_{n+1} — next FTUM step, attractor basin |
| 7 | Self | φ₀ — radion, mediating field (the seeker as coupling constant) |
| 8 | Environment | KK excitation spectrum — mode density of context |
| 9 | Hopes & Fears | Geodesic arc — desired attractor vs. feared repeller |
| 10 | Outcome | Fixed point — U·Ψ_n = Ψ_{n+1} |

---

## Quick Start

**Requirements:** Python 3.10+, numpy

```bash
pip install numpy
```

**New reading:**
```bash
python oracle.py --question "What should I focus on?" --user tcwp
python oracle.py --question "Will I influence my managers?" --user tcwp --date 2026-04-22
```

**Replay a saved reading:**
```bash
python oracle.py --reading readings/reading_001.json
python oracle.py --reading readings/reading_002.json
```

**Full options:**
```
python oracle.py --help

  --question / -q   The question for the reading (required for new reading)
  --user / -u       User ID (default: anonymous)
  --date / -d       Reading date YYYY-MM-DD (default: today)
  --reading / -r    Path to saved JSON record (replay mode)
  --json            Also print raw JSON to stdout
  --no-save         Do not save record to readings/
```

Each new reading is automatically saved as:
- `readings/reading_NNN.json` — machine-readable structured record
- (Create `readings/READING_NNN.md` manually for human-readable archive)

---

## File Structure

```
TarotOracle/
  oracle.py               — the engine (seed, draw, interpret, render, save)
  README.md               — this file
  SESSION_001.md          — session handoff note
  readings/
    README.md             — readings index + JSON schema documentation
    READING_001.md        — test reading 1: "What should I focus on right now?"
    reading_001.json      — structured record for reading 1
    READING_002.md        — test reading 2: "Will I influence my managers?"
    reading_002.json      — structured record for reading 2
```

---

## Test Readings

### READING_001 — "What should I focus on right now?"
- **Date:** 2026-04-22 · **Seed:** 347452485
- **Majors:** 5/10 (50% KK excitation density)
- **Outcome card:** The Tower
- **Synthesis:** The structure that is ready to fall is the answer. Release it intentionally;
  The Star follows The Tower.
- [Session archive →](SESSION_001.md)

### READING_002 — "Will I influence my managers?"
- **Date:** 2026-04-22 · **Seed:** 3875743467
- **Majors:** 6/10 (60% KK excitation density — high activation)
- **Outcome card:** Knight of Wands
- **Synthesis:** Yes. Through motion, not persuasion. The U-operator converges to forward
  movement that the field must accommodate.
- [Session archive →](SESSION_001.md)

> **Reviewer note (multi-year tarot practitioner):**
> *"Great job! I have read tarot for years. This is concise and well done."*

---

## The H Operator — Why Permanent Records Matter

The Unitary Manifold's H (holographic) operator encodes: every state of the interior is
fully captured at the boundary. Applied to the oracle: every reading is a boundary event.
The question, the seed, the draw, the interpretation — all permanently encoded in
`readings/`. Nothing is lost. The field grows denser with use. Over time, the reading
corpus becomes a holographic record of the questions asked and the field's responses —
a living instrument, not a stateless lookup.

---

## Connection to the Unitary Manifold

This oracle is one application layer above the full framework:

```
Unitary-Manifold/src/   — 18-domain physics engine
        ↕
tools/unitary_calc/     — universal calculator façade
        ↕
TarotOracle/oracle.py   — human-language interface using manifold constants
```

The constants (φ₀, α) are the same across all three layers. The tarot interpretation
layer is not decorative — it is a natural-language projection of the same geometric
relationships encoded in the physics.

---

*TarotOracle v1.0 — AxiomZero Technologies — 2026*  
*U·Ψ_n = Ψ_{n+1}*
