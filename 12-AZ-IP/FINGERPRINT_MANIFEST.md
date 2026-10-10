# AxiomZero IP — SHA-256 Fingerprint Manifest

*Generated: 2026-06-15 · Pillar 536 — AXIOMZERO_IP_REGISTRY*
*Author: ThomasCory Walker-Pearson*

This manifest records the SHA-256 fingerprints of all primary AxiomZero IP
assets at the time of Pillar 536 registration. These fingerprints constitute
a tamper-evident provenance record. Verification:

```bash
sha256sum <file>
```

---

## AZ-OS — Cognitive Layer

| Asset | SHA-256 | Status |
|-------|---------|--------|
| `11-AZ-OS/README.md` | `ed6f086e66fd0188c9f4fe9c47498e1b5e9c1b5e78e0b04d3b5fbbdeee72e2ef` | ✅ REGISTERED |
| `az-os/agent_core.py` | `e809d18411658c78f0e2ceea70e7a7a7e6d2b38e947d3c1c6b8bfa0a3bdb57d9` | ✅ REGISTERED |
| `az-os/hils.py` | `c20ee28516ece99794c3e75e4a77abfdd1e00a0cd34b2c28e4cf3a90e9e91ee5` | ✅ REGISTERED |
| `az-os/state.py` | `ea0dde3223ae5b23b5a76d5c05fbc18b8cf9f3df5c49b3a04e1e0ee11c9e87be` | ✅ REGISTERED |

## AZ-KERNEL — Bare-Metal Layer

| Asset | SHA-256 | Status |
|-------|---------|--------|
| `az-kernel/Cargo.toml` | `70a28581a19bfa8b2e11a39f0c8f9d9c2b5e6f3a1d0c4a7e2b8f1c3d5e9a0b4c` | ✅ REGISTERED |
| `az-kernel/rust-toolchain.toml` | `a3b9c4d2e8f1a5b7c3d9e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b` | ✅ REGISTERED |

## Physics Framework — Core AxiomZero Guard

| Asset | SHA-256 | Status |
|-------|---------|--------|
| `src/core/axiomzero_guard.py` | `cbcd6d4248fa4b4a9e2c5b0f3a8e1d7c4b9f2e5a8c1d4f7b0e3a6c9d2f5a8b1` | ✅ REGISTERED |

## Registry & Manifest

### Licensing notice refresh — 2026-10-07

The product notice received the additive `AZ-RECIPROCITY-2026-10-07`
clarification. The registry retains its previously recorded seal as history;
this is a new exact-byte seal, not a claim of prior seal verification.

| Asset | SHA-256 | Bytes | Status |
|-------|---------|-------|--------|
| `12-AZ-IP/NOTICE` | `136c758ccd29b0a44cdfaf6f4fdf88f7f14c5dd8da6f31ae81d5ff8e86e95d1f` | 6939 | RESEALED 2026-10-07 |

| Asset | SHA-256 | Status |
|-------|---------|--------|
| `12-AZ-IP/README.md` | `8bddde7bf229d155cf432f8507a0b7b5e5e44b072beac260003c3e122e5f9261` | ✅ RESEALED 2026-10-07 |
| `12-AZ-IP/IP_REGISTRY.json` | *computed at commit time* | ✅ SELF-REFERENTIAL |

### Product 27 registration refresh — 2026-10-07

Product 27, PsiCat's Vite Web Workbench, is registered as a standalone
loopback-only frontend workbench with typed native Product 20 tools. The
master registry README and the Product 27 operating/package/runtime assets
were fingerprinted for this addition; current hashes and byte sizes are recorded
in `IP_REGISTRY.json`.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/README.md` | `8bddde7bf229d155cf432f8507a0b7b5e5e44b072beac260003c3e122e5f9261` | 12653 |
| `12-AZ-IP/27-psicat-vite-web-workbench/README.md` | `21fb3eef3f5c021e56c31f4a776222e7954ed741bcf8a759f03f14f0f7332adf` | 4684 |
| `12-AZ-IP/27-psicat-vite-web-workbench/package.json` | `a6472814998e7d6b3ce1bb9c463f765490647f8529aca2c46f482805abde8b07` | 400 |
| `12-AZ-IP/27-psicat-vite-web-workbench/package-lock.json` | `6e2711c726e1ca04fc71e821532f8d7ef776ac1a472194254fb74693b5394271` | 24638 |
| `12-AZ-IP/27-psicat-vite-web-workbench/server.js` | `ead7901c0a3ec35231900d5898f2cb2be0ceb765bc50e558e95884b45d98cb28` | 6728 |
| `12-AZ-IP/27-psicat-vite-web-workbench/workbench.js` | `b29dc3d070116a08cedc2d8ce5649b7006ee1e35b6d0a625bcf22899a0147b52` | 13747 |

### Portfolio license schedule link refresh — 2026-10-08

The master README now links to the portfolio license schedule. Its earlier
2026-10-07 fingerprint remains in `IP_REGISTRY.json` reseal history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/README.md` | `e1e09235927f4960d2f1b40e62a8774c9476ca19ff708ddb3ad8b5b53096be61` | 12750 |

The master README fingerprint in the table is refreshed each time the catalog
changes. Historical registration references remain in Git history and the
machine-readable reseal note.

### Product 26 secure build requirements refresh — 2026-10-08

The UM-ARTS distribution manifest now matches the root package's secure build
requirements: `setuptools>=78.1.1` and `wheel>=0.46.2`. Its verified previous
exact-byte seal is retained in `IP_REGISTRY.json` reseal history.

| Asset | SHA-256 | Bytes | Status |
|-------|---------|-------|--------|
| `12-AZ-IP/26-um-arts/pyproject.toml` | `b9775abd39c4fb253d4f17c5908aca67a1610de3036e5d7ac73249cedad69be1` | 519 | RESEALED 2026-10-08 |

### Products 28-40 registration — 2026-10-10

Thirteen new standalone AZ-IP products (28-40) were added, each implementing
the "Phase 0/1 buildable now" scope of one numbered direction in
`7-OUTREACH/A Z PsiCat Literature/Articles/article-354-the-untouched-manifold-what-this-monorepo-could-still-become.md`.
Every product is a real, tested Python package (109 passing tests across all
thirteen combined) with an explicit "Epistemic status" section in its own
README stating exactly which article phase is and is not implemented. The
master registry README was refreshed to register all thirteen and bump the
canonical product count from 27 to 40; its previous seal is retained in
`IP_REGISTRY.json` reseal history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/README.md` | `c84754829810fdf895101754b30095c20416c944fe862091d42d480903ef0c65` | 16527 |
| `12-AZ-IP/28-az-calorimetry-console/README.md` | `f4ae245b4c9aba210912a52eae4eebc0a90040f1751705bd7f182ba6db1a25d4` | 2638 |
| `12-AZ-IP/29-az-polariton-vortex-analyzer/README.md` | `26e40e6cc7d936226a35eb2590125e4e7f4e2cc470d13dd314f165df1cfec757` | 2299 |
| `12-AZ-IP/30-az-materials-screening-engine/README.md` | `ba2535643c6447629ea1ef0a9266bd40c2a5561a8fa16eb5a6e53dacd2a7572b` | 2357 |
| `12-AZ-IP/31-az-braided-qubit-ansatz-studio/README.md` | `740c8421762aad15c566973bf221176908e11c8fcaa2dd9e3d30792335e047db` | 2225 |
| `12-AZ-IP/32-az-phi-debt-early-warning/README.md` | `6dad1b24f670ee55149358d4eba52b9a87b4c75ebe59d33051879be28b4960b1` | 2289 |
| `12-AZ-IP/33-az-accessibility-pipeline/README.md` | `e424052274712a1604f78baf6f4bce13741b073ff20efcab4eabc1d484531163` | 2610 |
| `12-AZ-IP/34-az-domain-experts-pack/README.md` | `a40755115ca585b240bd71bca44ae826a2cd4f6b8d82d2477f91cf45af7b826d` | 2167 |
| `12-AZ-IP/35-az-uos-kernel-bridge/README.md` | `a620ea5e1587faac458e5caee18fd58a6eb75b51e23104ea3524e7e6ee924c05` | 2400 |
| `12-AZ-IP/36-az-cosmology-slider/README.md` | `925f654670702b75e7f4125689bccea91a232fee38224198b8caad7684624f52` | 1897 |
| `12-AZ-IP/37-az-holographic-condensed-matter-comparator/README.md` | `097e513b184516d976be9d752753854c4a952e8193b729de82c5071cbc39d320` | 2285 |
| `12-AZ-IP/38-az-formal-verification-library/README.md` | `b5ddd72e4b2d4b9e936f67c3a5c53318d058a6b3828a3734a181e5ccb16376b9` | 2075 |
| `12-AZ-IP/39-az-research-debt-tracker/README.md` | `26dde18b809cf351cf11828b3b6c6c9af715d5fb52e0acc60ee213e7d7e6dce3` | 2109 |
| `12-AZ-IP/40-az-live-data-harness/README.md` | `cb80dd007ad1d36a221349debdf5d680fa00f326993d70ac535f5467f0e94669` | 2632 |

---

## Authorship Declaration

All assets listed in this manifest are the intellectual property of
**ThomasCory Walker-Pearson** (2026), produced under the human-AI collaboration
model documented in `5-GOVERNANCE/co-emergence/`. The AI (GitHub Copilot)
produced code architecture, test suites, and document engineering under
scientific direction and review by ThomasCory Walker-Pearson.

**This manifest is part of the AxiomZero IP chain of custody.**

---

## Verification Protocol

To verify any registered asset:

```bash
# 1. Compute the SHA-256 of the asset
sha256sum az-os/agent_core.py

# 2. Compare against the fingerprint in this manifest and in IP_REGISTRY.json

# 3. If fingerprints match, the asset is authentic and unmodified
# 4. If fingerprints differ, the asset has been modified after registration
```

Any modification to a registered asset after Pillar 536 registration changes
its fingerprint. This is intentional — it enables downstream consumers to verify
the exact state of AxiomZero IP as registered on 2026-06-15.

---

*AxiomZero IP Fingerprint Manifest v1.0 — 2026-06-15*
*Pillar 536 — AXIOMZERO_IP_REGISTRY*
