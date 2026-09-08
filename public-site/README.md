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
