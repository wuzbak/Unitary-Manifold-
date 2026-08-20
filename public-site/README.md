# public-site

Public webspace for AxiomZero Technologies & Consulting, SPC — UBI 606 239 876.

Current sync target: **v22.10**  
Public status snapshot: **56,772 passing tests · 976 Lean4 theorems · 0 failed**

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
