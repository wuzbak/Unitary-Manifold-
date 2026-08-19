# ROADMAP.md — FilmersCompanion

## v1.0 — MVP ✅ (Current)

- [x] 4 production modules: Cinematography, Locations, Finance, AD Suite
- [x] FastAPI + Gradio desktop app (port 7864)
- [x] 8-table SQLite schema with deterministic seed data
- [x] 19-entry knowledge base (Axiom Omega Principles + film production)
- [x] Agent resolver chain: Remote → Ollama → Static KB
- [x] 93 passing tests (6 test files)
- [x] Android MVP: Kotlin/Compose/Hilt/Room, 5 screens
- [x] Full API docs at /docs

## v1.1 — Export & Search (Q3 2026)

- [ ] PDF call sheet generation (WeasyPrint or reportlab)
- [ ] SQLite FTS5 full-text search across all tables
- [ ] Export budget to CSV/Excel
- [ ] Shot list PDF with thumbnail placeholders
- [ ] Android: network layer (Retrofit → desktop API)

## v1.2 — Multi-Project (Q4 2026)

- [ ] Multi-project support (project switcher in UI)
- [ ] Project import/export (ZIP archive)
- [ ] Crew management table (contact sheet)
- [ ] Script breakdown import (CSV/FDX)
- [ ] Android: offline-first sync with desktop

## v1.3 — Scheduling (Q1 2027)

- [ ] Strip board / shooting schedule builder
- [ ] Day-of-days calendar view
- [ ] Conflict detection (location/cast double-booking)
- [ ] Production report generator (daily, weekly)
- [ ] Android: push notifications for call time reminders

## v2.0 — Streaming & Collaboration (Q2 2027)

- [ ] Ollama streaming responses in Gradio
- [ ] Real-time collaboration via WebSockets
- [ ] Role-based access (1st AD, DP, Producer)
- [ ] Cloud sync (optional) with SQLite over HTTPS
- [ ] Offline Android with full sync

## Stretch Goals

- [ ] AI script breakdown from PDF/FDX
- [ ] Weather API integration for exterior shots
- [ ] Permit API integration (select US cities)
- [ ] Voice interface (production assistant)
- [ ] LiteBIRD falsification tracker integration (Unitary Manifold)

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
