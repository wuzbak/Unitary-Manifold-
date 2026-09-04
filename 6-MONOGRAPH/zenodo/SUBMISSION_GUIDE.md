# Zenodo Submission Guide
## The Unitary Manifold — Current-Version Update Workflow

Use this guide to publish a **new version** of the existing Zenodo record (`10.5281/zenodo.19584531`) without stale metadata drift.

---

## 1) Start from canonical status surfaces

Before uploading, verify these are aligned:

- `STATUS.md`
- `docs/mas_tracker.yml`
- `docs/CLAIM_MASTER_BOARD.md`
- `docs/TRUTH_LAYER.md`
- `docs/GATEKEEPER_SUMMARY.md`
- `docs/WAVE_CHANGELOG.md`
- `docs/SPRINT_PLAN.md`
- `9-INFRASTRUCTURE/um_live_status.json`

---

## 2) Create the upload

1. Go to `https://zenodo.org/record/19584531`
2. Click **New version**
3. Upload either:
   - full repository archive, or
   - manuscript + source packet with metadata files

Recommended archive command:

```bash
git archive --format=zip HEAD -o unitary-manifold-current.zip
```

---

## 3) Metadata files to keep synchronized

- `.zenodo.json`
- `6-MONOGRAPH/zenodo/.zenodo.json`
- `CITATION.cff`
- `9-INFRASTRUCTURE/schema.jsonld`

Do not publish if these disagree on version/status framing.

---

## 4) Required epistemic language

- State internal mathematical self-consistency and external-confirmation boundary plainly.
- Keep open lanes explicit.
- Keep falsifier language exact (LiteBIRD window + forbidden gap condition).
- Avoid inflated score language.

---

## 5) Publish

1. Save draft
2. Final metadata check
3. Publish

Zenodo’s concept DOI remains `10.5281/zenodo.19584531`; version DOI updates automatically.

---

## Useful links

- Record: `https://zenodo.org/record/19584531`
- Upload: `https://zenodo.org/uploads/new`
- GitHub integration: `https://zenodo.org/account/settings/github/`
