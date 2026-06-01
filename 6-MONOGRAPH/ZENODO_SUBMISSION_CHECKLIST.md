# Zenodo & arXiv Submission Checklist — v15.1

This checklist is synchronized to the current repository state and separates machine-completed packaging from human-account actions.

---

## ✅ Completed in repository

- [x] Preregistration registry exported: `10-UM-SOS/registry/predictions.json`
- [x] Derivation DAG export generated: `10-UM-SOS/graph/dag.json`
- [x] One-page decision-window API exposed: `10-UM-SOS/backend/app.py`
- [x] Current manuscript chapter set expanded in `manuscript/`
- [x] Full baseline regression captured in-session: 45,505 passed · 22 skipped · 12 deselected

---

## PART A — Zenodo publication (human account action)

1. Log in to Zenodo and create new upload.
2. Upload:
   - `6-MONOGRAPH/THEBOOKV9a (1).pdf`
   - `submission/falsification_report.md`
   - `submission/one_page_summary.md`
   - `10-UM-SOS/registry/predictions.json`
   - `10-UM-SOS/graph/dag.json`
3. Set publication type to **Preprint**.
4. Use current release metadata and publish.
5. Record DOI in `CITATION.cff` and `README.md`.

---

## PART B — arXiv submission (human account action)

1. Build submission archive:
   ```bash
   bash arxiv/build_submission.sh
   ```
2. Upload generated tarball at https://arxiv.org/submit.
3. Verify title/abstract/author fields match v15.1 documents.
4. Submit and record arXiv ID in repository metadata.

---

## PART C — Post-publication sync

- [ ] Add DOI + arXiv badges in `README.md`
- [ ] Update `CITATION.cff` identifiers
- [ ] Add release note to `STATUS.md` and `docs/WAVE_CHANGELOG.md`
- [ ] Publish outreach announcement in `7-OUTREACH/substack/posts/`
