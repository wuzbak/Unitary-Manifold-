# Compactification — standalone kernel and repository maps

The standalone `kernel.py` preserves a small, executable calculation surface
originally assembled in August 2026. It is **not** a reconstruction of the
entire monorepo, nor a current proof certificate for its physics. The historical
figures and claim labels in `ledger.json` are retained for provenance, with
their snapshot date and limitations made explicit.

For current scientific status, start with [`STATUS.md`](../STATUS.md),
[`docs/TRUTH_LAYER.md`](../docs/TRUTH_LAYER.md) (especially the foundation
reassessment), [`FALLIBILITY.md`](../FALLIBILITY.md), and
[`docs/CLAIM_MASTER_BOARD.md`](../docs/CLAIM_MASTER_BOARD.md). The conditional
metric parameterization does not establish photon origin or
action-to-evolution equivalence. A passing kernel test asserts only that the
standalone implementation behaves as tested.

## Navigation

| File | Meaning |
| --- | --- |
| `kernel.py` | Standalone calculations; requires NumPy, SciPy/SymPy optional |
| `axioms.py` | Historical axiom and gap registry, with updated metric boundary |
| `kernel_test.py` | Standalone regression assertions |
| `ledger.json` | Dated snapshot of calculations; **not** a current claim ledger |
| `kernel_map.json` | Machine-readable entrypoints, boundaries, canonical anchors and catalogue pointers |
| `monorepo_map.json` | Machine-readable file inventory for the **whole tracked repository** |
| `build_maps.py` | Rebuild and staleness-check both maps using Git and the Python standard library |

The monorepo map includes every tracked entry, including symlinks (and new,
non-ignored entries at generation time). Each entry has a repo-relative path, top-level folder, kind and
navigation lane. It groups **all** `12-AZ-IP/` products (01–25), shared IP
assets and every file in the PsiCat Literature `Books/` and `Articles/`
directories. These are navigational inventories, not attestations of product
readiness, editorial quality, scientific validity, or a cross-link inferred
from article titles. Binary contents are *not* copied into the compact kernel.
The authoritative product descriptions live in
[`12-AZ-IP/README.md`](../12-AZ-IP/README.md); the editorial catalogue lives in
[`7-OUTREACH/A Z PsiCat Literature/README.md`](../7-OUTREACH/A%20Z%20PsiCat%20Literature/README.md).
See [`docs/navigation/REPOSITORY_MAP.md`](../docs/navigation/REPOSITORY_MAP.md)
for a human-oriented map.

```bash
python3 COMPACTIFICATION/build_maps.py
python3 COMPACTIFICATION/build_maps.py --check
python3 COMPACTIFICATION/kernel_test.py
python3 -m pytest COMPACTIFICATION/test_maps.py -q
```

Run these commands from the repository root. The map generator is independent
of NumPy and works offline in a Git checkout. Regenerate both JSON maps after
adding, deleting or moving tracked files. `--check` exits nonzero on a stale
map. The compact physics calculations require NumPy; their original result
labels must not be promoted to current physics claims without re-evaluation
against the canonical sources above.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
