# Zenodo metadata update — v22.9

Updated on 2026-08-20 to match `STATUS.md` v22.9.

Changed files:
- `CITATION.cff`
- `.zenodo.json`
- `6-MONOGRAPH/zenodo/.zenodo.json`

Applied updates:
- Version/date set to `v22.9` / `2026-08-20`
- Test status updated to `~56,747 passed · 47 skipped · 12 deselected · 0 failed`
- Lean4 theorem count updated to `976`
- Pillar metadata updated to `208 hardgated core pillars`, `784 total pillar slots`, `next slot 785`
- Removed legacy score language and replaced it with plain epistemic status
- Kept concept DOI unchanged: `10.5281/zenodo.19584531`
- Updated organization affiliation to `AxiomZero Technologies & Consulting, SPC — UBI 606 239 876`

Manual Zenodo upload steps:
1. Open the Zenodo record that uses concept DOI `10.5281/zenodo.19584531`.
2. Create a new version draft in the Zenodo web UI.
3. Upload the repository snapshot for `v22.9`.
4. Copy the updated metadata from `CITATION.cff` and `.zenodo.json` into the Zenodo form as needed.
5. Verify the description keeps the honest epistemic framing and the primary falsifier: LiteBIRD `β ∈ {0.273°, 0.331°}` (~2032).
6. Publish the new Zenodo version manually.
