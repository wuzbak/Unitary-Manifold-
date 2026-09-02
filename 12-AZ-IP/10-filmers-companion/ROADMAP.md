# ROADMAP.md — FilmersCompanion

## v1.0 — MVP ✅

- [x] 4 production modules: Cinematography, Locations, Finance, AD Suite
- [x] FastAPI + Gradio desktop app (port 7864)
- [x] 8-table SQLite schema with deterministic seed data
- [x] 19-entry knowledge base (Axiom Omega Principles + film production)
- [x] Agent resolver chain: Remote → Ollama → Static KB
- [x] 93 passing tests (6 test files)
- [x] Android MVP: Kotlin/Compose/Hilt/Room, 5 screens
- [x] Full API docs at /docs

## v2.0 — Unified Production Suite ✅ (Current)

- [x] Producer / UPM unified dashboard with status, alerts, approvals, and at-risk department tracking
- [x] Script Studio with screenplay import, revision metadata, character extraction, and scene parsing
- [x] Breakdown engine spanning cast, camera, G&E, sound, art, wardrobe, hair/makeup, locations, VFX, editorial/post, legal/payroll, and marketing
- [x] Schedule days, strips, DOOD reporting, one-liners, and turnaround risk detection
- [x] Post / delivery tracking for assets, reviews, and deliverables
- [x] Expanded production data model and seed project covering the end-to-end flow
- [x] 105 passing desktop tests (7 test files)

## v2.1 — Interchange, Export, and Reporting

- [ ] PDF call sheet and storyboard export
- [ ] Budget export to CSV/Excel
- [ ] SQLite FTS5 search across scripts, tasks, notes, and assets
- [ ] FDX import/export and richer interchange
- [ ] Investor / studio summary reports and daily production report packets

## v2.2 — Collaboration, Permissions, and Sync

- [ ] Real-time collaboration via WebSockets
- [ ] Role-based access (Producer, UPM, 1st AD, DP, Department Head)
- [ ] Optional cloud sync with offline-first conflict handling
- [ ] Android sync to desktop API
- [ ] Mobile alerts for call times, approvals, and blockers

## v2.3 — Advanced Planning Intelligence

- [ ] AI script breakdown from PDF/FDX
- [ ] Weather / permit API overlays for exterior planning
- [ ] Scenario scheduling and contingency simulations
- [ ] Richer producer forecasting for burn, overages, and pickup risk

## Stretch Goals

- [ ] OpenTimelineIO / OpenAssetIO / OpenColorIO integration surfaces
- [ ] Blender / previs / techvis hooks
- [ ] Permit API integration (select US cities)
- [ ] Voice interface (production assistant)
- [ ] LiteBIRD falsification tracker integration (Unitary Manifold)

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
