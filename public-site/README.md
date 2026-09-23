# public-site

Public webspace for AxiomZero Technologies & Consulting, SPC — UBI 606 239 876.

Current sync target: **live** (from `9-INFRASTRUCTURE/um_live_status.json`)  
Public status snapshot: **served from canonical live status feed; no hardcoded counts**

## Structure

- `index.html` — primary landing page
- `az-apps/` — AZ products hub and public app pages
- `portal/` — open science portal
- `status/` — public status dashboard
- `apps/` — calculators and focused tools
- `css/`, `js/`, `data/` — shared assets and status feed

## Deploy

From the repository root:

```bash
firebase deploy --only hosting
```

Preview channel:

```bash
firebase hosting:channel:deploy preview --expires 1h
```

See `../DEPLOY.md` for the full deployment checklist, sitemap expectations, and product-page notes.

## Note from Base44 (dated 2026-09-08)

The following is documented as a **Base44 AI opinion** and may contain confabulation.

Base44 reported that this public site stack measures approximately **120K lines**, **99 pages**, **76 backend functions**, **64 entities**, and **416 components**, and that these figures were derived from filesystem inspection rather than guesswork.

Base44 also stated that breadth across six domains is genuine (physics, film, D&D, journalism, earth science, governance/AI), that the corresponding files exist and are not stubs, and that the custom Three.js topology layer plus Merlin AI capabilities (sovereign memory, tool-calling, ECLIPSA judge, heartbeat) represent non-trivial engineering.

## Note from Base44 (dated 2026-09-23) — full self-audit

The following is documented as a **Base44 AI opinion** (self-reported by the Base44 platform running the AxiomZero webspace) and **may contain confabulation**; it has not been independently verified against this repository's own filesystem or test tooling, and it supersedes the 2026-09-08 note above with a more detailed breakdown from the same webspace.

Base44 reported the following scale for the "AxiomZero Webspace" it hosts:

- **Codebase scale:** 1,017 total files; 155,477 total lines of code, across 8 languages (JSX 579 files/86,847 lines; JavaScript 216/33,803; TypeScript 115/15,725; JSON 14/12,011; JSONC 83/5,914; CSS 1/628; XML 1/244; HTML 1/31; Markdown 3/117; plain text 2/40).
- **Architecture:** 71 database entities, 98 backend functions, 10 automated workflows, 12 shared backend modules, 105 React pages, 468 React components, 51 shadcn/ui components, 18 custom hooks, 183 lib/util modules, and 122 total routes (47 active page routes, 75 legacy redirects).
- **Integrations:** 15 third-party API secrets (NASA ×3, NOAA/NWS, EIA, AirNow, ACLED, OpenSky ×2, Aleph/OCCRP, SEC EDGAR, OpenSanctions, OpenCorporates, FEC, CourtListener, GovInfo, OpenRouter), 1 OAuth connector (GitHub), 75 NPM dependencies, 4 public static assets.
- **Backend function categories (98 total):** data feeds/sensors (~30), investigative/journalism (~12), PsiCat AI engine (~18: agent loops, memory consolidation, council proposals, training heartbeat, self-audit, distillation), SDR radio (~12), D&D/tabletop (~6), infrastructure (~8), geo/earth science (~12).
- **Entity domains (71 total):** film production (25), D&D/tabletop (27), PsiCat AI/governance (9), SDR radio (3), investigative journalism (3), governance/corporate (6), built-in User (1).
- **Workflow triggers (10 total):** all scheduled (PsiCat Proposal Engine 6hr, Training Heartbeat, Memory Consolidation, Self-Audit, Repo Sync, Fallibility Scan, System Health, Empirical Observatory, Watchlist Monitor, Council Generator).

Base44's own bottom-line characterization: a 155K-line, 8-language, 1,017-file full-stack application with 71 database tables, 98 serverless functions, 10 automated workflows, 15 external API integrations, and 122 routes.

This note is preserved here for PsiCat and future contributors as a dated external self-report about the separate Base44-hosted webspace; it is **not** a claim about, or measurement of, the Unitary Manifold repository itself.
