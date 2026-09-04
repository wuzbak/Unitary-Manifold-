# Apps & Spaces Finalization Matrix (v35.7)

Purpose: one reconciliation view across product registry, HF Spaces, public-site hub, and submission/docs surfaces.

## Canonical references

- Product registry: `12-AZ-IP/README.md`
- HF deployment index: `hf-spaces/README.md`
- Public app hub: `public-site/az-apps/index.html`
- Canonical status: `STATUS.md`, `9-INFRASTRUCTURE/um_live_status.json`

## Coverage matrix

| Surface | Current coverage | Notes |
|---|---|---|
| `12-AZ-IP/README.md` | Products 01–23 | Canonical registry source |
| `hf-spaces/README.md` | Portal + spaces + dataset | Deployment topology source |
| `public-site/az-apps/index.html` | Hub updated for 23-product framing + Merlin naming consistency | Includes Product 22 and Product 23 visibility |
| `public-site/az-apps/19-ox-navigator.html` | Updated as Merlin Navigator (OX-compatible) | Keeps compatibility-route wording |
| `public-site/az-apps/23-merlin-dm-assistant.html` | Added | Public-facing entry for Product 23 |
| `DOWNLOAD_GUIDE.md` | Updated to non-stale, status-linked workflow | Removed fixed legacy release naming |
| `DEPLOY.md` | Updated to canonical status-source wording + 23-product references | Reduced stale snapshot drift |
| `.zenodo.json` + `6-MONOGRAPH/zenodo/.zenodo.json` | Updated to v35.7 metadata framing | Align before next deposit |
| `docs/ARXIV_SUBMISSION_GUIDE.md` + `6-MONOGRAPH/zenodo/SUBMISSION_GUIDE.md` | Rewritten for canonical-sync workflow | Removes stale score/version framing |

## Open operational checks

1. Keep CI green after any registry-affecting file changes.
2. Re-run status-drift/staleness gates on documentation updates.
3. Keep public pages free of stale hardcoded version/test snapshots unless explicitly historical.
