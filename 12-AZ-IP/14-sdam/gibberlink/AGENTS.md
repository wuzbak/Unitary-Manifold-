# AGENTS.md — Gibberlink Project Orientation
## `wuzbak/diary/Gibberlink/`

Read this before any session that touches the Gibberlink project.

---

## 1 · What This Project Is

**Gibberlink** is ThomasCory's exploration workspace for the Gibberlink AI
communication protocol — the open-source system by which two AI voice agents
detect each other and switch from human language to acoustic data-over-sound
(powered by the ggwave library).

This is both:
- A **learning / research** project (understand and decode the protocol)
- An **experimental integration** project (connect it to BV9900Pro hardware
  and eventually the Unitary-Manifold information channels)

---

## 2 · Orientation Order

1. Read this file (you're doing it).
2. Read `README.md` — project overview and connections to other projects.
3. Read `sessions/SESSION_NNN.md` (latest) — last known state.
4. Read `ROADMAP.md` — what's planned and what's next.
5. For protocol questions → `docs/PROTOCOL.md`
6. For setup / running locally → `docs/SETUP.md`

---

## 3 · Key Technical Context

| Concept | Detail |
|---|---|
| **ggwave** | FSK data-over-sound library by Georgi Gerganov. C++ core, Python/JS/WASM bindings. MIT. |
| **Gibberlink** | Demo by Pidkuiko + Starkov — two ElevenLabs agents that detect each other and switch to ggwave. MIT. |
| **Switch mechanism** | `gibbMode` client-side tool in ElevenLabs; called when both agents confirm AI identity. |
| **Bandwidth** | 8–16 bytes/sec; ECC included; FSK frequencies in human-audible range (1–6 kHz). |
| **BV9900Pro link** | The phone's mic + speaker can physically transmit and receive ggwave signals. Natural test platform. |
| **Manifold link** | Acoustic channels are an instance of holographic boundary information flow (see Unitary-Manifold). |

---

## 4 · What Must Never Break

- Never delete recorded experiment audio files without a session note explaining why.
- Never commit API keys (ElevenLabs, OpenAI, etc.) — use `.env` files that are gitignored.
- Script changes must not silently alter the ggwave encoding parameters without documentation.

---

## 5 · Connection to Other Projects

```
Unitary-Manifold (theory: information channels, holographic boundaries)
        ↕
Gibberlink (implementation: acoustic AI-to-AI data channel)
        ↕
BV9900Pro (hardware: mic/speaker platform for physical ggwave tx/rx)
```

A Gibberlink transmission IS an instance of the manifold's information
current `J^μ_inf`. That's not metaphor — it's testable.

---

*AGENTS.md — Gibberlink/ — v1.0 — 2026-04-18*
