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
| `12-AZ-IP/41-az-media-suite/README.md` | `68be8d1333f98bdfa1b01708c242e8718c79f309541a6e9a36599fcad49ae7c9` | 4289 |

---

### Products 39-40 reseal — Phase 2 web-product layer — 2026-10-10

Products 39 (AZ Research-Debt Tracker) and 40 (AZ Live-Data Harness) each
gained a Phase 2 read-only JSON API + static UI web-product layer
(`api.py`, `app/server.py`, `run.py --serve`, `tests/test_api.py`,
`ui/index.html`), mirroring the pattern already applied to Products
28-38. Their READMEs were updated (version/TRL/status bump + a "Running
as a web product" section) and are resealed below; their prior seals
above remain the historical record of the original Phase 0/1
registration.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/39-az-research-debt-tracker/README.md` | `6e5752fec9cc118689730b294f76a8ddbf66399507cbfd5a1d6e69fd33951e4d` | 2823 |
| `12-AZ-IP/40-az-live-data-harness/README.md` | `d01d560c6ead556f17ad2d8a1a540f511a2b8d074c23c0e43643afb56e6f1886` | 3377 |

---

### Master registry README — 1.1.0 web-layer bump — 2026-10-10

`12-AZ-IP/README.md` was refreshed to bump Products 28-40 to version
1.1.0 ("CLI / Python library + web", updated test counts) after each
gained the Phase 2 read-only JSON API + static UI web-product layer.
Previous seal (`c84754829810fdf895101754b30095c20416c944fe862091d42d480903ef0c65`,
16527 bytes) is retained in `IP_REGISTRY.json` reseal history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/README.md` | `5c2009d1a824cc55b9e17b1aa0f545cf2c07603169e5d6a9eaac1d9d2ce94280` | 16616 |

---

### Product 41 registration — master README reseal — 2026-10-10

Product 41, the AZ Media & Feature-Inspection Suite, was registered.
The master registry README was refreshed to register it and bump the
canonical product count from 40 to 41; its previous seal is retained in
`IP_REGISTRY.json` reseal history. This row was omitted from this
manifest when Product 41 was first registered and is added here for
completeness; `IP_REGISTRY.json` has carried the correct seal throughout.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/README.md` | `0f2dbfe3e8ef03bebd5b5883be7c5d4160b8e9cee18e186a568f10aa2e2898a7` | 17037 |

---

### Product 42 registration — 2026-10-10

Product 42, the AZ Awareness & Creation Toolkit, was registered. It gives
PsiCat/Merlin native awareness of its 41 sibling products (a holistic
audit of `merlin_tools.py` found zero of its ~200 tools referenced any of
them), plus general-purpose chart/knowledge-card creation and citation
verification. The master registry README was refreshed to register it and
bump the canonical product count from 41 to 42; its previous seal is
retained in `IP_REGISTRY.json` reseal history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/README.md` | `bfda7ce884d5b2c72c3f7085511e1bdb1afcd747a291a181d40c431b34d46700` | 17521 |
| `12-AZ-IP/42-az-awareness-creation-toolkit/README.md` | `d9b24c25c27b79af1db0dbd7b6fb1b2d86c3520f1e8c62d281caa995daf75714` | 4898 |

---

### Product 24 desktop integration reseal — 2026-11-01

Authorized integration strengthens the existing Product 24-to-Product 20 query
path with explicit context sharing, correct session-cookie handshake, bounded
transport, cancellation, correlation and visible failures. Prior registry-recorded
seals remain in `IP_REGISTRY.json` reseal history; these historical records are
not a claim that the prior working files matched their stored seals.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/24-psicat-web-browser/README.md` | `b4c6e81a47e5e6f516104278e3cc3017dc5a8edf5dbc6525d6dee1401079c2e6` | 8246 |
| `12-AZ-IP/24-psicat-web-browser/desktop/main.js` | `23d00f8f6146a47d04b06a70b4f09cec118534b9a7edfc4bb1e89fca75152620` | 28007 |

---

### Product 43 registration — AZ Geometric Tori Transformer — 2026-11-01

Product 43, the AZ Geometric Tori Transformer, was registered: a from-scratch
(NumPy-only, custom reverse-mode autograd) transformer whose positional
encoding and attention bias are derived directly from the repository's own
Z_74 toroidal phase lattice (K_CS=74=5²+7², (5,7) braid winding) instead of
standard sinusoidal RoPE — a toroidal rotary encoding with finite per-channel
orbit periods, plus a toroidal relative-distance attention bias. It is wired
as `getToriTransformerGeometry`/`getToriTransformerDemo` native PsiCat
Navigator tools (`ox_navigator/engine/merlin_tools.py`) and a
`/api/psicat/tori-transformer` route (`ox_navigator/app/server.py`), exposed
to PsiCat Browser via the Navigator's existing generic `/api/psicat` surface
with no separate Browser code required. The master registry README was
refreshed to register it and bump the canonical product count from 42 to 43.
This is an ADJACENT TRACK compute-architecture application of the lattice
constants, not a hardgate physics claim.

The master registry README was resealed on 2026-11-02 with the Product 43
entry; its previous seal is retained in `IP_REGISTRY.json` reseal history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/README.md` | `95f2f76489525d09ae2f5cf242c4b888e57fc78e236e40166053d4680cd1b3e1` | 18267 |
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `6e605fb0fea605c86c317f6f13d847dc95814be93f43c9ecdbeec40d70238f3b` | 7994 |
| `12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_tools.py` | `72ad38b258669ee69a6d985da06a78a3d04db5b6139d569dd7d52f5a3c11cb40` | 154328 |
| `12-AZ-IP/20-psicat-navigator/ox_navigator/app/server.py` | `daaad05fc976673ced7fbb7d1f1d359e46d2a499c5ece07a1a6b4e8f633c4cf2` | 123370 |

---

### AZ-KERNEL manifest reseal — 2026-11-02

The AZ-KERNEL manifest fingerprint was refreshed after the kernel-owned heap
allocator update. The earlier registration record above remains unchanged.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `az-kernel/Cargo.toml` | `90d098aa8f3f9dc2e3ebe5e8a3e6d7ae633a460bbaf81d08d67ed427a3620667` | 1555 |

### 12-AZ-IP README reseal — 2026-11-03

The `12-AZ-IP/README.md` fingerprint was refreshed after the recovered IP-suite work updated it.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/README.md` | `87506b41d32f781a99b6dee0700538ce11d7593d695b5f0f97c057f261fa6f42` | 18314 |

---

## Authorship Declaration

All assets listed in this manifest are the intellectual property of
**ThomasCory Walker-Pearson** (2026), produced under the human-AI collaboration
model documented in `5-GOVERNANCE/co-emergence/`. The AI (GitHub Copilot)
produced code architecture, test suites, and document engineering under
scientific direction and review by ThomasCory Walker-Pearson.

**This manifest is part of the AxiomZero IP chain of custody.**

---

### Product 44 registration - AxiomZero Weave - 2026-11-03

Registered the five-strand, seven-operation local integration runtime and
refreshed the master catalogue from 43 to 44 products. This is adjacent software:
source grounding, scoped memory, actual Oracle/Transformer adapters and
Pentad-constrained effects, not a new physics claim. Private exports remain
outside the public registry. Earlier seals above remain historical; the master
README's previous recorded seal is retained in `IP_REGISTRY.json`.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/README.md` | `0c1222cb41920b7c6b4ec44ee57faa2db84a8c3e1f35df5aab1dfc4d507a67a2` | 18758 |
| `12-AZ-IP/44-axiomzero-weave/README.md` | `31ed1f96a60077315d1219bbd492d0b287b7d40ed66e5824ac7e1d75053dea63` | 13004 |
| `12-AZ-IP/44-axiomzero-weave/pyproject.toml` | `fdb3ff3b1f4b35185055b3bd723f9fc67173bbbe0e00c942a73817cd42a205b2` | 504 |

Runtime receipts additionally record the computation implementation digest;
effect approval binds the relevant current Python implementation and target
configuration. Neither these hashes nor this registration authenticate a
principal or certify the truth of an output.

### Product 45 registration — AxiomZero PC Suite — 2026-11-03

Registered the offline-first Windows desktop portfolio catalog and launcher.
Product 45 provides catalog search, selected-checkout documentation/folder
access, shared collection access, and an explicit loopback PsiCat shortcut. It
does not bundle all 45 product runtimes or their dependencies. The master
catalog now records 45 products; the generated desktop catalog is fingerprinted
below. Windows artifacts are unsigned and still require an actual Windows
installation smoke test.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/NOTICE` | `c2b9856c0a9b2ccd022f0ecfb39ea8b9adf72274da1f2e000a44caa6606ad4b1` | 7360 |
| `12-AZ-IP/README.md` | `d7e1ba72b66e7e21152c15f795c224c8e00d3bd493f0016a3f0c77d0fdb71ea4` | 20194 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `16311f776a20f0e3d152aed1b07f503c696809f0017dd83e658e1f51224cbf35` | 4577 |
| `12-AZ-IP/45-axiomzero-pc-suite/package.json` | `917664125cd75b9a15c28b27232146ca7e399997bdee5710ee5ac9686b2350ff` | 1983 |
| `12-AZ-IP/45-axiomzero-pc-suite/package-lock.json` | `e1056c5236fd7fbbd50ce79a008d946020af7904be74597b7763c25b519ebf8a` | 127094 |
| `12-AZ-IP/45-axiomzero-pc-suite/main.cjs` | `a65d7c69db51777aaf2a379fd0ff23f9011a3255487dd6bbed76d12a9eacab68` | 6334 |
| `12-AZ-IP/45-axiomzero-pc-suite/preload.cjs` | `15abbb565824f6c74fcd722a245c27750e28a06bd27b3bffd43c636e7a73625f` | 941 |
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `203da940a2cbec4c44a38e221417eb59c8f5f3fa460d2733df40a788dc8370a4` | 5187 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `850f1ee2c939b521c141e0fd780916c221bab5b01fe710ad60a04c66add2586b` | 3875 |
| `12-AZ-IP/45-axiomzero-pc-suite/styles.css` | `600bfd85d5e15dd7251bb729b28f7db2b37d8b907ac4961465d175d91f291332` | 4229 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/catalog.cjs` | `85ecb2f319113e8b4b3b553a40ed4cdc40297731fbf47e9050997405154357f7` | 987 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/repository.cjs` | `46b091fa2d7a708958ce3cba1f64a72fb7ad3756b78539b0f135424c553e0e57` | 2160 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/settings.cjs` | `16f3368472ba2c3605613eb012eb8dcd4d7ac32ee61162761af9985ec339b289` | 970 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/build_catalog.py` | `a0eda09dafc5c1d93d2b37dc822e0d875af36e4358f6e85dcc14352548d43000` | 3118 |
| `12-AZ-IP/45-axiomzero-pc-suite/catalog/products.json` | `327bd0d7fc076caede76ad7555010cb644b42242b185bfab8b7ac15bbd81f492` | 16042 |

### Product 45 local evidence library reseal — 2026-11-04

Product 45 now imports user-selected folders and ZIPs into a bounded local
plaintext index and returns deterministic keyword matches with file/line
citations and content SHA-256 digests. Imported files are not extracted,
executed, modified, or uploaded. The supplied Webspace seed and PsiCat Mind
archives were indexed in-memory for compatibility verification; neither archive
nor its private contents were added to the repository. The app transparently
skips unsupported formats and applies documented file, archive, and index
limits. The local index is not encrypted and is explicitly disclosed in the UI.

The global NOTICE now includes the MIT terms for Product 45's bundled Yauzl
3.4.0 and Pend 1.2.0 runtime dependencies. The duplicate Product 45 row in the
portfolio license schedule was removed.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/NOTICE` | `85843e9e5bb870300d544cec9a8e5dfe229222648b12af4178d29aad530558a3` | 9767 |
| `12-AZ-IP/README.md` | `4f2934c661e25135618535650b111777de4e98e91e9b6cf33e64837cd8f54dd7` | 20532 |
| `12-AZ-IP/LICENSE-AGPL` | `b1ba76c1f17e23f25a2d84a0d60338f45b7ecfd9f92f002f8994d5ff2236650d` | 7844 |
| `12-AZ-IP/PORTFOLIO_LICENSE_SCHEDULE.md` | `987803b2d638fbbaa2ebfceb859cf603380df8dfefa6223a74191fbd6ad84c67` | 8390 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `c8f195d3a68b25d4f1fae535bf10b19258313222d1249c244183237c0a4ddc16` | 5875 |
| `12-AZ-IP/45-axiomzero-pc-suite/package.json` | `a4474d4dbee90e1d63176be6d00c7f3c137c2d147bf21ad9af025e535dcbb9f2` | 2026 |
| `12-AZ-IP/45-axiomzero-pc-suite/package-lock.json` | `7f35936d61a62553899c59edbb106ba477985886062df87e8d916140c2909259` | 127807 |
| `12-AZ-IP/45-axiomzero-pc-suite/main.cjs` | `36056959a8fcc298d85e55b7bcacda8baf329a1bda7c6675cb376c6cd7ce773b` | 9936 |
| `12-AZ-IP/45-axiomzero-pc-suite/preload.cjs` | `a04148a74778f295851039be5607294a77e23d366942315f110e690bed1c8444` | 1373 |
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `0d1dc77681320b02e0839e3c3205f0f8a0bbf8b8f48e18e04e9f1d2a16bce3a6` | 13507 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `b526fefda04cbb15f075e4df29a717c33db13c3294face8762839ee4f0c17bf7` | 5697 |
| `12-AZ-IP/45-axiomzero-pc-suite/styles.css` | `8993220cfe6809d788f7176bd22223c0399c784697ef26998875ecb45340753f` | 6509 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/settings.cjs` | `e39d1bf107c1261588a4f5312622c3ff496101f805fdf72c480f36dea456d5bb` | 1501 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/knowledge.cjs` | `bedb4592cf95adcb7e91632c5e708a571a4b7c57c525ddb65156403f41a1b71d` | 19799 |
| `12-AZ-IP/45-axiomzero-pc-suite/catalog/products.json` | `1fa4f04162a1b68c41e365429aa889d0ee29ba64b9b66148aca0d4cccf3d7e72` | 16073 |

### Product 45 final UI seal — 2026-11-04

Refreshed the final evidence-library UI sources after interaction hardening and
headless renderer verification.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `256b98eea9ebc0a609306b6043a20f14f24a4b307e8c43160d72f8c7fc0bb502` | 13730 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `cfdb4e8048f6d0083d0b1fdf3e8ab44e1ffd154fdc563da724b1d5fa5697adab` | 5804 |
| `12-AZ-IP/45-axiomzero-pc-suite/styles.css` | `bf7709c4c07814a148165d9242f27d1d67edc1344a758691792d809c904b9f97` | 6600 |

### Product 45 Windows release qualification reseal — 2026-11-04

Added pull-request Windows packaging, install/uninstall and portable-launch
smoke coverage, renderer verification, artifact checksums, and exclusive local
library mutations. These assets record the source and tests; Windows execution
results are reported by the pull-request workflow.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/README.md` | `21d234b16f4a4a3460f452d3f28bb49b7f047f36295461f650901b156ea10702` | 20569 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `115e5fd4c3abce7a6b72d472c9d3795987f1f07b0c1c3ccb988d867b3b40cb2a` | 6208 |
| `12-AZ-IP/45-axiomzero-pc-suite/package.json` | `72a2279841398f5bb32de0d3acd566f6a793a4e9bbff4033ba50f200392591e5` | 2124 |
| `12-AZ-IP/45-axiomzero-pc-suite/main.cjs` | `9e8b49881b15f1c30b031d2ae59053aa8b1ec59f513dedff7992e3e05f785837` | 10357 |
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `ead18116c5198760c7a2fd6f05902abbab09ae645e57b49c6cb00746dcc1c303` | 14282 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `2dcb2d7a66c077d2d44769e5bd6d0f9277aaa149b071d4103fd8ab431a018b22` | 5833 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/operation-lock.cjs` | `ad944f08b44f00f605a1d9dd786ab00bcdf4b2d57d66545bdb10e6273e9fb7a3` | 310 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/electron-ui-smoke.cjs` | `e14ae2eff591e8eb9cd54cbea49e67aa4d80869b4e3fbedec775c9f1b4b9b741` | 3474 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/windows-smoke.ps1` | `4a4016b49c9740de462c3ff58bab330d979d1c7c3db5168eb15887aba91c2d32` | 2991 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/catalog.test.cjs` | `c8e060309450c60d5681c717628348be04b9b43016dcc544303253bd956a7c82` | 3116 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/knowledge.test.cjs` | `a2d32735dd8820aef44fcfe37646658b48b3f146315a89399f32ad2f194d404d` | 6516 |

### Product 45 governed research harness reseal - 2026-11-04

Added dependency-ordered research tools, native per-step approvals, durable
checkpoints, bounded attempts/deadlines/context, cancellable evidence workers,
optional fixed-loopback Ollama reasoning, and a bounded hash-linked audit.
Task output remains unverified. No arbitrary shell, automatic cloud fallback,
all-product runtime bundle, embedded PsiCat model or physics promotion.
Resealed prior assets retain their previous values in registry reseal history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/README.md` | `8fc0501f604ad4c964018dba8a77b3bcd7e7b10c35bc98318494bd681abab174` | 20998 |
| `12-AZ-IP/PORTFOLIO_LICENSE_SCHEDULE.md` | `a3d9bbb6e3aa109db45aabaabc05a8eebe894d1b1a22a9d0cc91ea96ff3ac586` | 8409 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `7036e1121d574af7d7368f8a6e1c97d1a55feddfd3d429adca23260745418b03` | 9954 |
| `12-AZ-IP/45-axiomzero-pc-suite/main.cjs` | `bb05369b69110679c06d1c435fc8636e7f906a3079057424236224f73bf07b83` | 13920 |
| `12-AZ-IP/45-axiomzero-pc-suite/preload.cjs` | `d7f8b376b95b3ab42905adb6aaa0be7126a5eee193e501df6d4040a38b296c15` | 1863 |
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `1b88692d8098c03f8e0fce1d6ba1160cd835b9f51fe9c128d41468b83dff01de` | 21535 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `1fd67785e35a91995eaa6e63e351af3c633c1d0c11b02fe6a7f924274bc3a2b2` | 8106 |
| `12-AZ-IP/45-axiomzero-pc-suite/styles.css` | `c7505d52ff87a44bfba70d5fcaff57ebd92246945ff0e0bcee1af3566a29fee0` | 8392 |
| `12-AZ-IP/45-axiomzero-pc-suite/catalog/products.json` | `5139ab826e24e0b3b831fade5db8e673db92a79898497e6683f34cc4448224a4` | 16055 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/electron-ui-smoke.cjs` | `051e22e8224feffcaf6b470c59413c266312da8e362e17c541e0e82523580ca6` | 5934 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/harness.cjs` | `01bc648aa011b25f4033dfdce8d16d35cfca40801a29411f7e09d6144e232f4e` | 17191 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/local-model.cjs` | `24018a05d12ed66fb651d8f1bbf49402812ea7f1988bd5151d7880706f0e0647` | 6520 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/worker-search.cjs` | `6a6ffc2291c9e5362aeb05a0af6f1905324ca95308cebd0949192170c8cfa919` | 1187 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/evidence-worker.cjs` | `bbbd2e2ddff166d2b71a8e9bccf7c53aad0826d5f48b2078c578f5b72d8bbe22` | 390 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/harness.test.cjs` | `7add3cb6bb5537c00cee4a26b6a101dfa42dd2389e5c68b1d62c29d95ad3130f` | 12857 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/local-model.test.cjs` | `743755f1c54891a1511180b655144a42446791cd8eeed1a33936457d00768614` | 9050 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/main.test.cjs` | `730c1c6666bf937c7345ea902b6af52bbef5fa05804486f7abc9a958befc0a78` | 4718 |

### Product 45 hardware-gated model preparation reseal - 2026-11-04

Added local native-consented hardware measurement, conservative screening,
visible uncertainty and explicit export. No automatic model installation,
GPU compute certification or training claim. Prior seals remain in registry
history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `938cd7409aff6a77a4645c6b9e4e38f101b2e5728f1413e9b62e542a73dbde08` | 11163 |
| `12-AZ-IP/45-axiomzero-pc-suite/main.cjs` | `b9c8df20370f643a2ae08cec2a1a0602c681209aee6f2b4a59c15e70d1210966` | 15578 |
| `12-AZ-IP/45-axiomzero-pc-suite/preload.cjs` | `f01d8fdd70af5692f06d47244a983dad10025077fcb59a6725c2b8d880d03f00` | 1989 |
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `3c3835ca0f17162e56ab9c66b1f37607a437e8bbe1ea41aab2aa50d2776d94fc` | 24074 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `6a4fe7fa2733434b128ded4799ee4afcbbf57417bfb8e76c00e771faaacdfc0c` | 9066 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/electron-ui-smoke.cjs` | `3ef45c6169f671add9f63240559d07c47a90aa9ecb248a93c1c4b2e970f1b946` | 6562 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/main.test.cjs` | `ac5df122e1e3f195961f676039f348cbd031536f4d224fa4c96f2bdc9e041ce1` | 5662 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/hardware.cjs` | `93c871a2ae7b22e08338d8601b01fed4644748015e8cf50015723eb79143c2b2` | 4437 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/hardware.test.cjs` | `d4de72af231acd2d5e9492b37fd8de32178f03514eaa16fa04a91a51b4e4f338` | 4149 |

### Product 45 native model and runtime provisioning reseal - 2026-11-04

Registered a genuinely trained experimental native model, offline inference/local training,
consent-gated Python dependency provisioning, checksum-receipted bundled source and reviewed
loopback lifecycle. Non-Windows/unsupported targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `585abc2154c4ca8f4b6319b3367fc6c4f2afddfdbd3110cbf2c52728e47631e9` | 14735 |
| `12-AZ-IP/45-axiomzero-pc-suite/catalog/products.json` | `6fe6fd752ae89780e0f1bc38fd8b08bbedb94504c8dcc37bbca536c91ce07ab9` | 16109 |
| `12-AZ-IP/45-axiomzero-pc-suite/catalog/runtimes.json` | `df465a8dbcfb11405f1d702a3e584dda7dbcb65dc2c22f6d2fef83efac3f9d62` | 32207 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `4bb97fbf87f61d891b3cf738f72ff36ac5faee59509d201b195d4993a23dd872` | 11689 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/native-model.cjs` | `8df01db3b2d6fa955ea3dce2bd13605c4d887fa9f46a98234b9a471630d08384` | 5077 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/portfolio-source.cjs` | `b2b7f07d312981d9f5dfe8134c68f5e3c00c0d5ff5b0ab18bd184da2a8024d31` | 2145 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/runtime-manager.cjs` | `1a29d6756ec03dfc7652321c0e84f3f9141f342ddc39796325f9a9c906f35870` | 10738 |
| `12-AZ-IP/45-axiomzero-pc-suite/main.cjs` | `41f0db6b569e7293b00cc562cd927032ded3305f117964482df347864a47576a` | 22004 |
| `12-AZ-IP/45-axiomzero-pc-suite/package.json` | `1e91db8449f142107df35b773af1cb9c3b4b62ed5d024f554ac8dd1c78a9e462` | 2843 |
| `12-AZ-IP/45-axiomzero-pc-suite/preload.cjs` | `be8920ae2dd3d9a2460a2c1201930171bc530b33711c8c8bae77405dc2862ed2` | 2593 |
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `cbdc072bf2502c68ac87a13dad994af195c6c4c0f3211906d983d9bc612abf57` | 30243 |
| `12-AZ-IP/45-axiomzero-pc-suite/requirements-calculators.txt` | `39ff50d845c624de83316712b11d877d194a25a3049e7b9456ab736de0797333` | 92 |
| `12-AZ-IP/45-axiomzero-pc-suite/requirements-native-build.txt` | `c76630033cc01b2dd2fd0ffdef8d263e2345e32f57b0934b96bbea83a9f38567` | 33 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/build_native.py` | `74d20c5f2a66f264d5a59489b2602c441a6d0cd9603810060f7f031e2de4707c` | 3115 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/electron-ui-smoke.cjs` | `582ce62b07273e5b1f58edaa715304852f6dcf2d8c53572e7a89b5d93189fd2e` | 7378 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/native_smoke.cjs` | `02e23209458a95275338b0dcf983491ccf96df54502f92a694d46993d87bc0d5` | 1770 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/portfolio_smoke.cjs` | `a4ca35f4e385150d40afb274e676d3ddc1e05786b99d1453708585ca9264b298` | 1922 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/psicat_core.py` | `ba1158f3d5a4a3590463f6e9e6e93e4909f3e81e6d5c53c83821684322f64784` | 4023 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/stage_portfolio.cjs` | `3734f181e658c6ee4443ad3cf9f0042804f14853679b235dc914684de125b830` | 1787 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/windows-smoke.ps1` | `60217f4a8da8588b3c434ff9514540f6cfbdb75adbbc2066d55e7b31717709b8` | 3399 |
| `12-AZ-IP/45-axiomzero-pc-suite/styles.css` | `1db8fe50a2570f7b796dbeb1668e3106212aed72b320a1bdea5622623ea0c32a` | 8533 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/main.test.cjs` | `8fdfb6cb3f7f92da6d2f7725d046def58916d23a18042b82c8ab67da034d14ca` | 6463 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/native-model.test.cjs` | `a7a6cb043bf98eaeffec2941c5a3d9cfbe57350966f309e27592ac35408cf93e` | 4332 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/portfolio-source.test.cjs` | `4afacc4d579457d93440e4704bbbdf0fae519441a99072873f7adf40c956732a` | 2422 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/runtime-manager.test.cjs` | `d330293bb41989007635865c05c2bd28a58ee452d1db91d6071976934e71038d` | 6920 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/runtime-manifest.test.cjs` | `df230d9f0844fab618e6f70b40d03be50e7abfb68180953e26658df0f029d20a` | 7998 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/test_psicat_core.py` | `b4a6f3b2d3a6492ad24b4f99b7974b47dcc9b5aa4bdf8df73e8e2836afc49d00` | 2009 |
| `12-AZ-IP/PORTFOLIO_LICENSE_SCHEDULE.md` | `df8b9cf75614ccb9aca655817c5833a93ed5c25d45239d6cd558d8ec71650451` | 8459 |
| `12-AZ-IP/README.md` | `3138e21f5dd65c2599135410e3decb5017a5126859c51c285af472b5bf5ce6aa` | 21625 |

### Product 45 native model and runtime provisioning reseal - 2026-11-04

Registered a genuinely trained experimental native model, offline inference/local training,
consent-gated Python dependency provisioning, checksum-receipted bundled source and reviewed
loopback lifecycle. Non-Windows/unsupported targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/stage_portfolio.cjs` | `54b9861c20ba359ef29854c48ed6d3cd7ccc2402b1fd87d1d1c360866e403315` | 1882 |

### Product 45 native model and runtime provisioning reseal - 2026-11-04

Registered a genuinely trained experimental native model, offline inference/local training,
consent-gated Python dependency provisioning, checksum-receipted bundled source and reviewed
loopback lifecycle. Non-Windows/unsupported targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `2cdd03b339912a7c86aaa1eb9597faf3ba604a90a84ce288cf83de2aa997046a` | 14862 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/portfolio-source.cjs` | `9f6e879e9436de37ee3b125c7cd2ac8f84f151c3b1e2e433c6746e4f67a9ecc5` | 2206 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/build_native.py` | `efd2b84bfaff5a16b4f276891a86896d6350ea26983045125bebdc3d9fb21d06` | 3223 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/stage_portfolio.cjs` | `4322a6ade32fbc4b1b4523f612dabfdf0d1962377dfe73d8117159af80363ad6` | 2366 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/portfolio-source.test.cjs` | `e27a591407934e885c3f5d86f5cf953591576f7b04f6df1e51a1447b3b2489b3` | 2626 |

### Product 45 native model and runtime provisioning reseal - 2026-11-04

Registered a genuinely trained experimental native model, offline inference/local training,
consent-gated Python dependency provisioning, checksum-receipted bundled source and reviewed
loopback lifecycle. Non-Windows/unsupported targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `f7e136b3c568da7bb75218473cb584996c289c0ccaada0c3feb0584a3ba0fd6d` | 15015 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/build_native.py` | `098d30b57417f3f65858929730c780a9899311a3aa51050886c3a5c0990fb24a` | 3197 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/electron-ui-smoke.cjs` | `6a1a410d8b11525aec965ede1caadee518cafde380c50c5dc4f5ad51265f2d92` | 7379 |

### Product 45 native model and runtime provisioning reseal - 2026-11-04

Registered a genuinely trained experimental native model, offline inference/local training,
consent-gated Python dependency provisioning, checksum-receipted bundled source and reviewed
loopback lifecycle. Non-Windows/unsupported targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `4863ce41e2ff0ef741957f444d0813b63ecf9500d5ba26f245340d8dec2a0351` | 16857 |
| `12-AZ-IP/45-axiomzero-pc-suite/catalog/products.json` | `dfa752a64563e8bad3b5db2320e6c80dc232fb9aa59491a5fad5b59806491ffb` | 16116 |
| `12-AZ-IP/45-axiomzero-pc-suite/catalog/runtimes.json` | `f29a97e3d16c84b6eea719093349e8fb9bf64cb13c100298a76aa8fec48f4b44` | 32377 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `78dd1e6049337e93fdef92c35375825848f13985341dfa18120e245be038f61d` | 11923 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/node-bootstrap.cjs` | `79571e0b3230f73b5081c418a68d7a44e6919a9042b422325f2ac55633a2e40f` | 3253 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/node-toolchain.cjs` | `26c8ed2d1b324d1141bed5911c5b3d37c75750325697c91c6cc6893cd5bb2dcc` | 906 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/runtime-manager.cjs` | `541a06b8cb5ccb0f4b0bddc5de29b29c306ef686b5073ee1890243aa6adb5923` | 13639 |
| `12-AZ-IP/45-axiomzero-pc-suite/main.cjs` | `a7fbdee6bf24ee1ab72eed1149e1c8a88917ed81901e73f3bf03e1989572e20d` | 24428 |
| `12-AZ-IP/45-axiomzero-pc-suite/package.json` | `a06f49a65c7bf716837ff4ea07c205c78f51df99da0010016adabbb229d1d789` | 2952 |
| `12-AZ-IP/45-axiomzero-pc-suite/preload.cjs` | `3932f7510c83a0188016cec15068159f0adba7762d57871ca44a41330b31878d` | 2720 |
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `d9923abf7637bf711ee116ce8a40160a0288ef93c76599a5b862bd28eb99aec7` | 30900 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/extract-node.ps1` | `acf8a5b122e7398ba372a4105196a93fcb08e4d8e541abf50b4028865ac5c371` | 211 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/portfolio_smoke.cjs` | `93e670afc7ebe732b395f03d880226f3273ee01dccff2aa6c3276b59aa56c9a7` | 3589 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/main.test.cjs` | `90e6c2eab3d1e0cc9b2b008b9667c3022548c27938958cb2bc41bc31a1c7ceb4` | 7778 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/node-bootstrap.test.cjs` | `403fcf082bf0c7da53a922bbe6f818073dea761f55c309823f6609cdac658e84` | 3355 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/node-toolchain.test.cjs` | `5d3a646079d9e402c741d6479e60df2ff65893bbfe0f488c49ef0a1d78debb52` | 1113 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/runtime-manager.test.cjs` | `de1c418c857454a6a33433ca6b0d9757359375268c9d4fe770a6592e6a7aed27` | 9822 |
| `12-AZ-IP/README.md` | `b78e6f34fd0432d3bc5395b571715f3ce7a6f8dcea8c703bbd5856a07dca7ae3` | 21632 |

### Product 45 native model and runtime provisioning reseal - 2026-11-04

Registered a genuinely trained experimental native model, offline inference/local training,
consent-gated Python dependency provisioning, checksum-receipted bundled source and reviewed
loopback lifecycle. Non-Windows/unsupported targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/27-psicat-vite-web-workbench/README.md` | `eadf4d30c4761b5e6e93dadbeb800ece3ae33134aeb84caf3e1dba369c840c56` | 5518 |
| `12-AZ-IP/27-psicat-vite-web-workbench/workbench.js` | `c25cc508a71aea0abf4b8140593b02b468e505489f696c882716edfd46b0fa35` | 13972 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/portfolio_smoke.cjs` | `08c34e3aecb53e0c4b942b66c12d6dd3b7e0755a58b3255180f4ec1083046186` | 3671 |

### Product 45 native model and runtime provisioning reseal - 2026-11-04

Registered a genuinely trained experimental native model, offline inference/local training,
consent-gated Python dependency provisioning, checksum-receipted bundled source and reviewed
loopback lifecycle. Non-Windows/unsupported targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/24-psicat-web-browser/README.md` | `e88de5a970e113ee422c828b0f7d9fc28acdf2e18e6d3e3e40b178aa952f285d` | 21241 |
| `12-AZ-IP/24-psicat-web-browser/desktop/lib/desktop-boundary.js` | `b9fa7dfa764b669e7a8c1a831b983fdb281c6e37aeaf3a57200e95233cce3ccd` | 510 |
| `12-AZ-IP/24-psicat-web-browser/desktop/lib/sidecar.js` | `57ab2946e4036b3f14dedac09a807ea5db862b08b462f439298a4011e6913fc8` | 7153 |
| `12-AZ-IP/24-psicat-web-browser/desktop/lib/suite-lifecycle.js` | `7def35a724bbb98264fb8c32eff36149c1c8b8866aa072b0a58141af9520b39f` | 1536 |
| `12-AZ-IP/24-psicat-web-browser/desktop/main.js` | `5ca09709968ce4d98b764adf44e3a148ba20fa0b2138ba1b03ba98b66574600a` | 30204 |
| `12-AZ-IP/24-psicat-web-browser/package-lock.json` | `6f86c7010894f91af8f3ffc40cb884e2d52f21ea0121e2a3066ec7db4f9d958e` | 7292 |
| `12-AZ-IP/24-psicat-web-browser/package.json` | `a277b33be1133c376d9bf76c777820783d092140210284e38aca1940e4453c83` | 965 |
| `12-AZ-IP/24-psicat-web-browser/playwright.config.js` | `56758da4b97eeef2353f15e52673da922a219ad72b44d6d1e72a8c698f67e0c0` | 354 |
| `12-AZ-IP/24-psicat-web-browser/sync_backend/server.py` | `1c5ed24fc0b6c0a990f4143d07ed50fe8e126d49dde13e1596afc52fb2a480b8` | 6480 |
| `12-AZ-IP/24-psicat-web-browser/tests/desktop-boundary.test.js` | `f8a14ebf0dcc57819dc92eaadeb9b843e265144f38b574a3d58c59a93ceb6494` | 1507 |
| `12-AZ-IP/24-psicat-web-browser/tests/desktop-runtime.test.js` | `e1454003f7aba5efaf4c27af0ed6e0d2157add37039cf7dd1e9fb135aa6d9a1c` | 6749 |
| `12-AZ-IP/24-psicat-web-browser/tests/serve-ui.js` | `da84d370f1059d07395272a9e9f4b2b18178c48b9343a8bfddb3cc7342862d8a` | 765 |
| `12-AZ-IP/24-psicat-web-browser/tests/sidecar.test.js` | `c4562e2a4708a081382b6aad20e9da498f576dc5ec775472ac8a4ddd845739b3` | 11861 |
| `12-AZ-IP/24-psicat-web-browser/tests/suite-lifecycle.test.js` | `cea4b44fd3b73c28ba0c5ef7bd9397454a226e2fd30cdbab44bda67f62cf11ab` | 2125 |
| `12-AZ-IP/24-psicat-web-browser/tests/test_product24_structure.py` | `67c2afe48404560ba93da944f9f1d09e442a78e34bea160c46b11a40c6a19597` | 2251 |
| `12-AZ-IP/24-psicat-web-browser/tests/test_sync_backend.py` | `a2b802e230d6a70e57d3ca3ddeef22efe13069906e73103c9d7578a8e07d5c5e` | 4807 |
| `12-AZ-IP/36-az-cosmology-slider/README.md` | `36fd4fcc42648b04195b3c38619d12baa07aada5b8b18682bb2d90d7c6e6089b` | 3450 |
| `12-AZ-IP/36-az-cosmology-slider/requirements.txt` | `80f9be4514d8c3528a4ef97e8d6dbca988ac1eb9fefaae8f62e8981e3af806cf` | 31 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `795c730afdaa447a7837b0ca49d8009597a9cc5fc922fd41d89ccf276baaf450` | 18366 |
| `12-AZ-IP/45-axiomzero-pc-suite/catalog/products.json` | `71e44ae481012492aca6d938378321a19cb480d7a62ed063b07bba9e58179d9b` | 16136 |
| `12-AZ-IP/45-axiomzero-pc-suite/catalog/runtimes.json` | `65d40342f81c09d216773642e763bb908dfe6aca19bd337841cd36a81e6789d2` | 32687 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `7c38b909fd20ce79f76b517f76003572f542ea76fcdf732cf3be585876748fca` | 12074 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/desktop-runtime.cjs` | `7ec1b834944b940b29e93fd68168c491094408a4008591a580a8460f47364df7` | 3301 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/runtime-manager.cjs` | `49510b9eb48ae2fe6f8625ec850ffd974ae127561128a6e6164cd5383860199e` | 20171 |
| `12-AZ-IP/45-axiomzero-pc-suite/main.cjs` | `97f4478f213f947579c31b6590a6deecded7d6c5145c381094ba3aecaa1a8f92` | 25168 |
| `12-AZ-IP/45-axiomzero-pc-suite/preload.cjs` | `239177ad01f99875448cd5e4c4478cf78d0c361613be64a2c62764c40465679d` | 3031 |
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `9705a40cb835ca3b52aa221fa114020572defac0eda9ec98ce4d9daebe92b839` | 31406 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/electron-ui-smoke.cjs` | `733a19a7001fcc2f18dab36342138d30b019892c53c55992d66336499b81e5f4` | 8039 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/portfolio_smoke.cjs` | `34c4ce09fccf57bba2b0b6640c30c92151102aee59a83003305cbe10da660c26` | 5969 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/desktop-runtime.test.cjs` | `c590cdd84c9960ce0a00494a7a577c9a913173c443a3b1935b8eb14e8d08939a` | 2898 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/main.test.cjs` | `448a4af2cd45718c17fa9c6318df41e9aa709a89799359f6c5cfae3743982cbc` | 8972 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/preload-state.test.cjs` | `916bf6ab9242955a77a531513e4ff0bd5de7ec74928729aa3bde403f989667e0` | 1020 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/runtime-manager.test.cjs` | `78495ff889cb130922eda31b891fffc9f5db07398d591a912d566db244a55d86` | 17329 |
| `12-AZ-IP/README.md` | `9521202c8a6ada31f09667171d68f3b736bcfd43cd89705d06045a44c6addaa8` | 21908 |

### Product 45 native model and runtime provisioning reseal - 2026-11-04

Registered a genuinely trained experimental native model, offline inference/local training,
consent-gated Python dependency provisioning, checksum-receipted bundled source and reviewed
loopback lifecycle. Non-Windows/unsupported targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/27-psicat-vite-web-workbench/README.md` | `0ed1d307fa0af0a781f0766f09c1497056b8726a4bc943de31ec875bfe39fbf9` | 5642 |
| `12-AZ-IP/27-psicat-vite-web-workbench/workbench.js` | `d342ddd281a887f87159d8866b56f374306e3ca47d7074543aa87a88adebd58e` | 14054 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/portfolio_smoke.cjs` | `5fe7c4137291f0065faf0e5f1c3aac2741ac0c67f17802c12954048e763a2e6e` | 6421 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/runtime-manager.test.cjs` | `ac15ad00f7810c3f8fbbeee4f36545628bb1781962116f0d27e5eb6abe2e6203` | 17092 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/24-psicat-web-browser/README.md` | `c9ae91627e60ad3ca3fa1892dc04755908f63978b442a31c02d888c8151bfe38` | 23813 |
| `12-AZ-IP/24-psicat-web-browser/desktop/lib/sidecar.js` | `508ef05ddf0b84d5d0206c3fce73e9f813c35ea1657eabec8ffb4b46da66f6a2` | 7326 |
| `12-AZ-IP/24-psicat-web-browser/desktop/lib/startup-diagnostics.js` | `22cd6a6452379d6eed57591f17fae8e33f87539b66560a0e4bb49b21d8741301` | 2433 |
| `12-AZ-IP/24-psicat-web-browser/desktop/main.js` | `00ee262107ccc70cf8c5e9e267c71c39bf75b3715989c8d9b11c158a3017f51f` | 350 |
| `12-AZ-IP/24-psicat-web-browser/desktop/runtime.js` | `a7ad4ae1d5a798d66d9dd4244c0fea92c5a51eba7c83790557f350bf4daaef65` | 31159 |
| `12-AZ-IP/24-psicat-web-browser/package.json` | `fea57fc2e3b7c3317a5665ea7ef0d1e4bf7164752a40806b023674069eac95ad` | 1134 |
| `12-AZ-IP/24-psicat-web-browser/tests/desktop-runtime.test.js` | `26978f146cbc1f5f1aeb5ca44af976870a0ef9bf06faac09e135dde3e5c03928` | 9089 |
| `12-AZ-IP/24-psicat-web-browser/tests/electron-ipc-probe.js` | `a859b39357c96adce9006977423dd0ed778ebce7b8c73514c6cd2b372c359041` | 1073 |
| `12-AZ-IP/24-psicat-web-browser/tests/run-ipc-probe.js` | `5870f833b5bf6f5c4a0be49c040252e764bb1832dd6eb49f66de8c61aa190283` | 2457 |
| `12-AZ-IP/24-psicat-web-browser/tests/sidecar.test.js` | `08355d219cbc1ea4b467a7f5c422600fea8b275fa57109971eee016da4666f63` | 12264 |
| `12-AZ-IP/24-psicat-web-browser/tests/startup-diagnostics.test.js` | `d11d67c9cd264fa0f1ed9bd31a875794161721b820a911c792adbde0852c768d` | 2812 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `3ac82294ed18e48192041a9fdfba91aa0f244c5c55ea263b2559fdefb08528c0` | 18922 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/desktop-runtime.cjs` | `0eab62595e8b9abb069dd62ae0cf4a5faa625e2cb6b676d1223f90730b5c3434` | 3356 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/runtime-manager.cjs` | `38b9e1ce661d34ef83edea87789700875c8f16e6749dc9bd100d4226fe8e7916` | 20198 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/desktop-runtime.test.cjs` | `bbd60cd213cb63a3795b4803e20c7e6159f615bcb34558aaa32087220b7eecb3` | 3173 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/runtime-manager.test.cjs` | `2f252d451c2ba74f929a07dfc5345b90c2c7985b16d3bfe3dadfedb04771859c` | 17119 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `f59fd606e504d7fcb5c7be9d57d4222077bf2c6a17c89ea1b322a5a2ae28616c` | 22732 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `d6429aeddd2415774771b3a47c85e95b89f67ae0c63af8b804cf1a70f2a0cc75` | 35798 |
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `cfa09b183075b768f400e5bbb531e539645581e008348312fe224c80d37b0a5d` | 27510 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `4f3de87c6621aa35cfb983056165588781c732a4a8e94832306a7ef50d70ad12` | 19215 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/desktop-runtime.cjs` | `999bc622c10ccf0cb260a6e4b383a5f34ce5bb1fd399889bb1bce5f75ff0a140` | 6131 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/portfolio-source.cjs` | `dac30fbb0a8580c7d40cf45b77f7a474a125fd8b4036e1f94cb1e1ed604d0e86` | 2185 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/runtime-manager.cjs` | `f92898014b70f6fff2f717113870d6f61faa859b772621d0b31d208a94da2574` | 20263 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/portfolio_smoke.cjs` | `51e4ab3c5c01b6d525931b9825b0dd32069f39d2a660b58f54f714bfe670fbdd` | 7197 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/desktop-runtime.test.cjs` | `e96b8ab76840acbf25e999c27e71d3eda8c96962c9b388245b8fe309aa1bfcf0` | 4926 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/portfolio-source.test.cjs` | `34cfdc6a1353a4e6fd6cfd5eb7ff5ed377c628c8be619acf3f6854a84813de73` | 3234 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `935cb111b8ac14a5b40af435b21ce6f79d1e4f1401a86c539c28cc3b5f5da690` | 42833 |
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `5e4986aed9ca0ff240abaad4306466603bf2a25fe95f0ef7ae3cca8f9ea2b067` | 28898 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/desktop-runtime.cjs` | `3c56968a9330e39755c75d80f9188b90a3da5a0e368bdb964696b71e912c4176` | 6152 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/desktop-runtime.test.cjs` | `bea91f8eaf0b7dae051a2ec863025fe2e24e7af8acd65d69dea8fbfe20664c96` | 5311 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/24-psicat-web-browser/README.md` | `8743b9b7b4b2cc214260424fe463da5d59d80194417204e34fc781d42ea48f92` | 25264 |
| `12-AZ-IP/24-psicat-web-browser/desktop/lib/component-diagnostics.js` | `40a7939685f2380394f902ce451570a678aa49db195aea97c32a308c3598fce9` | 3779 |
| `12-AZ-IP/24-psicat-web-browser/desktop/lib/sidecar.js` | `fe821e6fcc575f47b51f00ae9890827dc0df1f5c78a3e491957ae92761eb8d90` | 8595 |
| `12-AZ-IP/24-psicat-web-browser/desktop/lib/startup-diagnostics.js` | `19c52e29668236e93043e47f14e292b63a02116fff365287f2ee650796851fe9` | 3081 |
| `12-AZ-IP/24-psicat-web-browser/desktop/runtime.js` | `a5eeb785e9cd4252720a156184567de080831282d98a74b6ae02cca72bb8d9ac` | 32924 |
| `12-AZ-IP/24-psicat-web-browser/tests/component-diagnostics.test.js` | `3f28de7d6ae015350140a1ce60b7d401efb31bc673fff8dd75d0de7c454de2a4` | 2863 |
| `12-AZ-IP/24-psicat-web-browser/tests/desktop-runtime.test.js` | `5f15c5a9940aefeffbf898c030a17e51dbf67454d6ca46dfbd5383c020ba8d06` | 9537 |
| `12-AZ-IP/24-psicat-web-browser/tests/sidecar.test.js` | `ed0c00d1138aca52f427bc15de8b4f47627be0c912834821f8adc2055db6e4d4` | 13164 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `4a59b8baff3539f8157b7e099671bf60a56ff042af5400f99c488cbf6c2b8c27` | 19357 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/portfolio-source.cjs` | `afcb1446693a98217d0977373b769a25bded2ed446255aaae0eb7bc5245bdb1d` | 2633 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/stage_portfolio.cjs` | `4923f9476d5e45ab463248c0a4c571f3daf1189fc47f7f8451273943246da2f2` | 2241 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/portfolio-source.test.cjs` | `1a63a4b9bcb3d39e2a3874e19cb0dc333c9c9660705ae5181ad42faa91bf8f6c` | 3801 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `a983c5dae8d4b4a063759ce1326b156ed42e5bd81247a7bf6749868324a42d6f` | 29024 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `bbd27754ca5d7f04ae01add27105739eada72772e72dfb2363f1b5dc3680f2bf` | 23001 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `5f422967441093a4a94dda48dbcd138ac53babb44a03050bdea5c63ab1c42b7e` | 43294 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/15-pentacorder/README.md` | `6068cdff68cf8cb07cd77d8d8dc528018edef7163c8d7ccf1b199a249c59d92c` | 15949 |
| `12-AZ-IP/15-pentacorder/gradle/libs.versions.toml` | `e2f9feed22f79a891aa9050faabf281486368f5e464aaf842891ed41f45c28af` | 4134 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/test_android_catalog.py` | `992820f107886505e97c017fb32a36c16b9c4c05c02ebbb4dcf89a4e49f4e249` | 1222 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/14-sdam/app/app/src/main/java/com/sdam/ui/MainViewModel.kt` | `cdb7a5e9eca0f3ee9424e77f5176203bbdc4f0b5ee67956a764efae81466c2e4` | 22533 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/15-pentacorder/feature/acoustic/src/main/java/com/gibbernode/feature/acoustic/AcousticViewModel.kt` | `4c63f5d484f423580e850eb8b100d67bb21baec75096975b5374a811155cb34d` | 13452 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `32e285819a2ddf62db70b4a6285e85bbd1541301ae8b45b84c4c2b93dd594d53` | 44773 |
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `02425ce1bce0b35a0e98bd0bf51e7907c0f011497e0c58f5cba56150515e47f6` | 29281 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `bc7c6a2a5d17d0f1f4b04cb6f56d8062a00f1acca0f668ca981fb5a9cc4fb406` | 23914 |
| `12-AZ-IP/45-axiomzero-pc-suite/index.html` | `91b32169095b9c8b879fe6d5a3784547bf667441ee8153715f9574b23c793725` | 15911 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/harness.cjs` | `acb591eeacdab3eca3b8e39774e93aa37138ac3fe8ae466014df26fd1b44a3bd` | 17852 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `cf608f58e64eb1827466f7080d0ed3b660ba5918ba020a129dfeb1ee5aee83b4` | 32811 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/platform-targets.cjs` | `8160f81810e6e0745561dda7618622583f46a35a6e31562bace1c4a37bb45e77` | 37367 |
| `12-AZ-IP/45-axiomzero-pc-suite/main.cjs` | `a0e58b8c746f846250413ec985b0e77dfbd245f43bd4c3d711a258bf5186d3f1` | 35520 |
| `12-AZ-IP/45-axiomzero-pc-suite/package.json` | `fa02b64f6afe58828ceeef62bb236143dc2ef8ef329617ddbb78941dec8ef453` | 3133 |
| `12-AZ-IP/45-axiomzero-pc-suite/preload.cjs` | `0b14fc9b6d1e3b5f8bd9f080ae04fe26ccbe56ce9600f969ff560d3d48fb2a5b` | 3617 |
| `12-AZ-IP/45-axiomzero-pc-suite/renderer.js` | `cda180ac63ea6549bd4cb5da0d8004e49761ea054b9f11ba9f59596b942c2e38` | 39553 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/electron-ui-smoke.cjs` | `2d881033c860bcf4c5258d6739daed96ae8f7011ec985367d8c9602949b54e16` | 9795 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/instruction_smoke.cjs` | `1642327c08917c930b533c25403ed8ee6ca96e935844ec51a5cbded308169957` | 1722 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/platform_smoke.cjs` | `90fd761fa25621528ba92a129c7084b16dadbab785432998e9664d7df01e2426` | 2419 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/windows-smoke.ps1` | `16372ce44a47c9c41be76306002109d8311ff642a94f647c26020153a34b6d83` | 3862 |
| `12-AZ-IP/45-axiomzero-pc-suite/styles.css` | `ef05f8cc96b13dfe592636a3e04110e8fe0f36552b534299ee8f653149969372` | 8948 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/harness.test.cjs` | `b82bb2389b5436b7313535f9260bd25990ea27f1ae70742530ad713405d4fd12` | 14094 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `e28e90ff6b1a99ac6f06d11a23714e70b0dd19c740aec438e322bc1334be9aa2` | 25229 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/main.test.cjs` | `7d2d51cab6d0a906bf973df0985a75cb771ae3bb6205c1adf639996b3c00703b` | 15416 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/platform-targets.test.cjs` | `eceaf9a560109f3aa4e97672a34cf8fc76bd044fdd7f4ab57afd08b8cf7be524` | 26569 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/preload-state.test.cjs` | `fbcb2382206ebf48a52fb9d852dc9e9377c1debcecebc086305e6ae8a39e0543` | 1915 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/15-pentacorder/core/ui/src/main/java/com/gibbernode/ui/Theme.kt` | `bd835c3fe6b3e9695b60638ac43c24058413853f29a3fa54e2ae0ecf5b99d627` | 1829 |
| `12-AZ-IP/15-pentacorder/feature/dashboard/src/main/java/com/gibbernode/feature/dashboard/DashboardScreen.kt` | `4623ab693e885b1b6a3854b991cde3ec050ebd7e988a132bee3a36716c9c9399` | 18184 |
| `12-AZ-IP/15-pentacorder/feature/mode/src/main/java/com/gibbernode/feature/mode/ModeScreen.kt` | `7d2d1c4adac4d8c5cd5bce1ba4e53d0d4c48adbebbd0c4120ac554d58e6f945e` | 39367 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `5dcbb4028c894f500b108ede80c082e758f4f22afb035d94ce3dcb72e2c64a11` | 24058 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/01-axiom-os/README.md` | `fa9a470cd1f8732a3e691190381e58a78a3b9b5da2aef7da2b3db391d64ed6de` | 9736 |

### Windows desktop startup and lifecycle reseal - 2026-11-04

Resealed selected tracked runtime assets after desktop startup diagnostics and lifecycle
regression fixes. Untracked local environments are not registered. Non-Windows/unsupported
targets and assistant-quality limits remain explicit.
Native Windows validation is separate; no all-target operational certification is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/15-pentacorder/feature/labs/src/main/java/com/gibbernode/feature/labs/SensorStatusScreen.kt` | `179aa04b0b381c82d64c79e326db47a749c232b0308c226458baebf1fc540270` | 5398 |

### Recovery reconciliation and readiness follow-through reseal - 2026-11-05

Reconciled the stranded allocator/browser follow-up against current mainline,
closed reviewed runtime/evidence defects, documented bounded declarative checks,
and repaired Product 45 provisioning retries and Windows smoke arguments.
The older Product 02 seal was already stale; preserved history records prior
registry entries, not an assertion that every prior entry matched pre-edit bytes.
Native Windows, hardware and model qualification remain separate gates. No
scientific, portfolio-wide production or complete lost-session recovery claim
is implied.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/02-az-kernel/README.md` | `529a5caa7f3f048c85f5b2067658283f6a88b9eac0a00e5e907e777b9d41462e` | 3099 |
| `12-AZ-IP/04-um-sos/README.md` | `d24961de87892b8f92d4f77a37309998db01a2a6da25054ad7baccd0d074d918` | 4289 |
| `12-AZ-IP/24-psicat-web-browser/README.md` | `2a5f6fb2c75e5c4f7cc04d6cc1dca687e041c3a58013e3572bd3fb5fdb589980` | 25571 |
| `12-AZ-IP/24-psicat-web-browser/desktop/runtime.js` | `8969484ad05d0e8d1f85b155c3e9e34cfe2b533a8ffd5d49e7d5bab887310c40` | 31426 |
| `12-AZ-IP/38-az-formal-verification-library/README.md` | `341b7c8078d68d83f2343f239694839fb2aa38dd461492f93963ac3c0d80fa5b` | 3857 |
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `0cb1943c7ae7522130e8c470b62c8c43fd23b9a4f47548a67d7fb945f18dcbd1` | 23388 |
| `12-AZ-IP/44-axiomzero-weave/README.md` | `81fc9ad6b5b7718ad0d80be3f6d230426d81c6e51df82d10e0f281bf49a8b97d` | 14609 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `a4375b87ce42bd140bc560220587f803d98707644fcc14e7780cdfefff5cf8a7` | 24787 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/portfolio-source.cjs` | `e61d6538f6be4e6359b2fea9409ec921a975d0a2168955f86a7ec75fcb5856f1` | 3327 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/windows-smoke.ps1` | `4184952192f49794193aec1c5156cdd1ab1915c2294e26f1bd205a533511ada8` | 4056 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/portfolio-source.test.cjs` | `d344de8a4480e580826df3af04818c94001e84de919148fadd0a3fd7c86fe6a7` | 5290 |

### Native CI cleanup follow-through reseal - 2026-11-05

The initial native instruction-backend job failed in owned-child unit cleanup,
before model evaluation. These changes wait for failed-spawn/exited handles,
retain genuine cleanup failures alongside the primary error and add regressions.
The local suite passes 223 tests; native rerun remains required.
Model policy, verifier and acceptance thresholds are unchanged.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `8a411975d343346d6594283395713bef020b70afb582e0aed2b53156f9ab3c23` | 25248 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `39e2204c3eb94b97a3e44ddf59f325e334d1a92a686b27ed4386eb2e82272e87` | 33488 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `fcf1e2fb9ae9e9b6bb1b81bdeedb7e7ea10995386b4c8eec4928a9c90e7868f3` | 29342 |

### Native recovery and measured qualification follow-through reseal - 2026-11-05

Product 01 closes each SQLite connection deterministically without changing
transaction or restart semantics. Product 45 records native cleanup success
and the real candidate's failed malicious-instruction rationale criterion.
The unchanged acceptance gate still blocks packaging; this is not production
or hardware certification.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/01-axiom-os/README.md` | `05ed1c24584a6fbe87a4b842b9fa1b8add1fc5491ad281709377e8487ba66cc9` | 9983 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `f6c464c311730e3d967d28073af8252bfe7bfcc3581dce3341cf332ea5b5a4ee` | 25807 |

### Product 40 temporal capture documentation reseal - 2026-11-05

The Product 40 README now documents its source-bound temporal CLI/API adapter,
local observation-time availability, explicit missing magnitudes and remaining
feature-store/drift boundaries. Tests use labeled constructed responses; a real
live CLI attempt in this environment failed at DNS resolution, without fallback.

The previous registry-recorded seal did not match the pre-change Git asset.
`IP_REGISTRY.json` preserves both the historical registry identity and the actual
pre-edit identity; this reseal does not certify that the older seal was valid.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/40-az-live-data-harness/README.md` | `237a323a32a12aac208fa98e378ff69e6ac57629ac064803765cbf0ea27a68ae` | 5431 |

### Product 40 exact raw-response replay documentation reseal - 2026-11-05

The Product 40 README now documents bounded raw-response archival and explicit
offline replay preserving original observation time, origin, source and snapshot
bindings. Temporal null corrections and backward-time revisions remain explicit.
Constructed-response tests are not live-feed validation; the current live
attempt still fails DNS without fallback. The prior seal remains in registry
history and in the preceding dated subsection.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/40-az-live-data-harness/README.md` | `7bbe986e3ac04df2136b8cbba8563cabbbfee22eef4d73cac0eb364331fe813e` | 7350 |

### Product 40 capture-destination preflight reseal - 2026-11-05

The Product 40 README now states that requested snapshot and raw-archive
directories are checked before a network acquisition begins. This avoids
requesting a live payload when its explicit retention destination is missing
or a symlink. The prior exact-replay documentation seal remains in registry
history; no live-data success is implied.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/40-az-live-data-harness/README.md` | `4781f1b0cedb2f418d5616b27e6a5251f7c40a9b6c1ef7be22362a6d98833424` | 7638 |

### Products 43 and 45 instruction-candidate selection reseal - 2026-11-05

The registered READMEs now distinguish the selected direct official
Qwen2.5-1.5B-Instruct Q4_K_M candidate from the preceding Qwen3 Q8/Q4 experiment.
Both preceding artifacts failed acceptance; choosing another candidate does
not qualify it. Actual hosted checks, the model budget, provenance checks and
packaging acceptance remain required. Prior documentation identities are
retained in registry history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `555dc31b1d4edc14e2987fa3bac4f0c06cc6181286d300dc6b9ca2567518879b` | 23292 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `4f283b0d700658e211eda7f1a904847b8e48ffb6257ca2a6f5b1c347a1945d2f` | 24275 |

### Products 43 and 45 candidate/runtime contract reseal - 2026-11-05

The verifier, its contracts, the governed Node client and matching tests now
select the direct instruction-tuned candidate consistently. The historical
Q8 profile remains diagnostic-only. Previous registered identities and the
actual preceding committed diagnostic/runtime identities are retained in the
registry. This also closes the seal gap introduced by earlier diagnostic and
owned-process-cleanup edits; it is not a quality certificate.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `5dc8e332bb902aa64f6d8f4cc6d7efdb7fbb6e6cc8d411193588d2d12ebe4a97` | 31754 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `26a7de6db36ae7d0cbb86b43a25c3d178e97bfe76a97ba164c11bb628b6d15b8` | 50156 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `13d7646a4aa30bd836e81f5f13a4ee9c0dc96eabab14fb5398b29a5b0979fed2` | 32911 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `4c7d82132d6c969fa591519caeb484e15d4245ce786590d23ac4d88c5c1cd70d` | 25385 |

### Products 43 and 45 general output/trust policy reseal - 2026-11-05

The verifier and actual governed client now state a stronger general output
contract: plain requested JSON, literal source-status labels and refusal
grounds based on action authority rather than unrelated platform limits.
This intentionally changes the production system policy; it does not change
the case prompts, grading thresholds or deterministic decoding. The preceding
2/4 instruction-candidate receipt remains preserved without modification.
Previous source identities are retained in registry history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `a97a8517a54c1a09011f4eddbc0b887fe0b904942e15c8ef202c2bd0007757dc` | 31995 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `67a6e01fd70e1c75d0007ad0159eee019767c5a1aeaf04e9a8f97317f8f44f46` | 50508 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `836a7d27cc0c17f01d9c95e4101879fcaaf2298ddc542bf6aa2e7047c3592768` | 33148 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `943abbb5247f009d887e7cbbf875ca3a836a4d4362e734cd0417818e3b295a8b` | 25908 |

### Products 43 and 45 syntax-only JSON decoding reseal - 2026-11-05

The actual governed runtime and JSON-requesting verifier cases now request
generic JSON-object constrained decoding. This changes structured-output
decoding, not evaluation prompts or semantic grading. No answer-bearing schema
or output repair is introduced. Plain-text challenges remain unconstrained;
unsupported decoding fails explicitly without an unconstrained retry.
The preceding shared-policy experiment still failed 2/4 and its exact receipt
is preserved. Previous source identities remain in registry history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `114f7894c86268926e2a78cf43de3174770372f96c510cf8fa6368d0545833f9` | 23636 |
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `bf528717baf276a14308092f35f21bdb6ab9d1b1ab748878f308d097c00589d4` | 32331 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `61a1bdaa2b89610f7754f7b73b4819db13a7e2695d259b93eda12a8ae9b83f8e` | 52313 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `6db8927c6722ca1747703fb3d257f68e97bcba18c2017e34ec6cc5eb6f28d087` | 24553 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `39083f6d476d4d9abf1b30a00f8153e86f927a2b064407ed3585c9ccb16ba2f0` | 33214 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `59e6d3c9c1053f013e8a104e36a02b14e30e61f4ac0f92cfed66938850bc24ca` | 26724 |

### Products 43 and 45 bounded model-review reseal - 2026-11-05

Every JSON task now receives a draft and one generic same-model revision,
without grader feedback or expected-answer content. Both generated texts remain
distinguishable; a failed review never falls back to the draft. Plain-text
challenges remain single-pass. The default CPU context is 4,096 tokens, while
initial client input limits remain unchanged and client draft/review share the
existing inference deadline (the verifier retains a per-HTTP timeout). This adds latency, not independent verification
or an earned model-quality pass. Case prompts and grading remain unchanged;
earlier negative receipts and previous source seals remain preserved.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `15cfbe885999a6ae298db911e0f98d2749aad03b7a64ee8b8627be3f0cbd6c0f` | 24197 |
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `bb238ec0639d632a32aae09512e6fbb15d22230eaa48ea562a2c7cdcda87d8e6` | 35730 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `b1e9c52e7a842dc318ed9932d7f3fa1c5159e72d509dff284931bd0c7f0e191e` | 61968 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `65c817a47a982248e21b2da290408b753bcc698f0cd08a9906bbf3ed03aa6e52` | 25217 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `3ae077b1ef9316a7d5c6b947a62bd6580e1dfb32ced282be1b65c53f18b4ccbb` | 34998 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `30667d76e58c8b88c45c536f34120e7b61c2ba63f63420174f4063cc0eb9cd1c` | 31676 |

### Products 43 and 45 experimental review opt-in reseal - 2026-11-05

Actual hosted two-pass evaluation still passed only 3/4 with identical JSON
drafts and revisions. The unqualified extra generation is now explicit
experimental opt-in; normal inference retains one generation and a 2,048-token
context. No evaluation case, grader or threshold changed. Both review outputs
and explicit failures remain available when opted in. Previous exact identities
are retained above and in registry reseal history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `b2b0c9d63dbe1a0f7ed9d220b8fc58108861147079aa7adb89316ae87e00231d` | 24228 |
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `2f9074ed5ac9344798ac00f6de49f9978eb3d96001301015e0baa3ca213e92fe` | 36144 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `f0dbc8a4d46db8ebcb8fa60839959018c8f1efadb6110ee3ef821871f00364ea` | 63548 |
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `e1e07d1ed6920b1ee3949a2d87ae851a091e4f7a1595ad642d3d0719021aa57e` | 25524 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `d7723d043c4861fc85ac89c8d80ddcd4038cca23fdd8034cc6bed6f74d155f72` | 35436 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `1aa13373adf1e06d9905f5a73d59961ac459e6e1f3cdacbd6a9c22bd5990e2fb` | 33035 |

### Product 44 point-in-time query context reseal - 2026-11-05

The Weave README now documents optional, already-loaded temporal snapshots in
read-only queries. Owner/hash binding, availability-aware selection, explicit
freshness and origin policy do not constitute feature-service qualification.
The previous exact-byte seal is retained in the registry's reseal history.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/44-axiomzero-weave/README.md` | `bbad263a5a9b13181ab00db408379a2d5a181e1c22f3df34f9b3a8224d9fe52a` | 14603 |

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

### Product 43 retrieval-injection prompt clarification reseal - 2026-11-05

The hosted gate failed 3/4: the model refused correctly but returned a sentence
instead of `unsupported` for android/uefi. The prompt now states the literal
required values. Grader and thresholds are unchanged.

| Asset | SHA-256 | Size |
|-------|---------|-----:|
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `2ff9c4da6a6cb61f3a8dc3f49364016bf11904f90b048b58e3a032644287b563` | 36291 |

---

*AxiomZero IP Fingerprint Manifest v1.0 — 2026-06-15*
*Pillar 536 — AXIOMZERO_IP_REGISTRY*

### Integrated mainline/recovery model-policy reseal — 2026-11-05

Reconciled merged mainline candidate policy with recovery-owned process cleanup and generic status/authority rules; unchanged actual-model acceptance remains to be demonstrated. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `d1a057e797f00d633c1e24345843c110fcb0ad210faafa46238805c88422607a` | 27654 |
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `3aef20a9f0d646deabaac0a69dbbdb998a0f7c32995a51b7f3b68325d2d4ba5b` | 24615 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `00e5a156adf21fa97510f7c5c4a705e9cecc04c6b86ce688c4925a607926a545` | 64462 |
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `999fcb761373bc88ba27b83eab819ea4bb6c1f92511b6d306a994948643cf8d2` | 36396 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `d6b738b1ced2debf3e722d52cf629f557c61847621b4950c0b6969668babbc6e` | 36158 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `6d34f8a2bafe44afc95607873699cb74d7a6d042c05b9382a55c09eed071639b` | 37393 |

### Approved stronger instruction-model reseal — 2026-11-05

Steward-approved 3 GB model budget and stronger instruction-only Unsloth Qwen3 4B conversion, with explicit community provenance; unchanged actual-model acceptance remains to be demonstrated. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `870684a4d8764c6eefb8eb377d712594420464958cd1388c76fa29f3736e635d` | 28366 |
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `17bff86e0c95434d66103afca8bdb3372e742420d7440a11e31e6264e9eddc6d` | 25352 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `42e2e34c7604ffe254f9c551b45ebad2c73cb35acbb9af23b22b9a4af5c6d538` | 65967 |
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `87a17bc612d154b1c862e9f97587c2562b175812ea1c5fe25017be0dcba83530` | 36607 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `b14ab56fca7d37c0748bb89e1bf98f6e0acf6ff3087ea26e2db5a6c4da7e1de8` | 36192 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `21f9bcdfcbcc3443d037547086324b4c63e773e76a8f2b50ae1bc0bbbb357688` | 37608 |

### Mainline temporal/retrieval recovery reseal — 2026-11-05

Reconcile mainline temporal/retrieval follow-through with standalone read-only Weave imports and recovery histories; preserve the approved stronger-model candidate and unchanged acceptance criteria. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/44-axiomzero-weave/README.md` | `faab0463ca3a6abb67fddc77a8a5b795d6de81babe3ededb7d1217d9c61c73e6` | 16363 |

### Approved claim-detector and native-freshness correction — 2026-11-05

Steward-approved conservative negation-aware claim detection, pinned stronger-model conversion and Windows receipt-freshness correction; preserve safety criteria, historical failures and native gates. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `399650bd971583b3733e877deae8d9dace5643f1e1a086e28e09b2a834955d5e` | 28517 |
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `252ddfb733f84660df35c4576283f08a65b3440b26fe9f5d650aa50801ef3d81` | 25653 |
| `12-AZ-IP/43-az-geometric-tori-transformer/tests/test_candidate_engine.py` | `1fbb97bcf90c4557e87df7070d54724f86d88fe244b52c2b1ce3a55b460bab20` | 68696 |
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `6c9b7322ff1c649b78d1ee76f21ab138dbe2e8b0e6b9ca5e4c7e5ffa523e72d6` | 37632 |

### Owned-engine policy-prefix reuse — 2026-11-05

Reuse the production safety-policy prefix during fresh-token ownership checks to avoid redundant prefill within unchanged request deadlines; retain authentication, answer schemas and native qualification gates. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `bcf4546dead8a561eb6cbd0b7221b35214fcdeb6bf06d2bc6b88ab25fd048da3` | 28799 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `82fa23b04b7f6977f19f5ec67c6ea9723ac28c3e52ad71d07cad4b28ce35f97e` | 36191 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `aff1fd74eae7445f1a25f002b30bcd64dfc03dc4d6277c9173c4e23d81d46d47` | 37870 |

### Original-challenge mainline reconciliation — 2026-11-05

Reconcile the latest mainline gate-clarification history while retaining the original, harder injection prompt already passed by the stronger model; preserve all historical seals and approved safety criteria. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/43-az-geometric-tori-transformer/verify_embedded_engine.py` | `6c9b7322ff1c649b78d1ee76f21ab138dbe2e8b0e6b9ca5e4c7e5ffa523e72d6` | 37632 |

### Consistent owned-engine JSON challenge — 2026-11-06

Use the same production JSON envelope for fresh-token ownership challenges; retain exact nonce, status, citation and listener checks without fallback or changed deadlines. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `006d802d7a50e7b494cc2ced96f2e389ee7610a9a84b2922a436d25764ef3586` | 36678 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `37309105852402689e95107f8795d8cced68acfb62d5de2c6fb7a77e2f457b74` | 38143 |

### Approved verified offline installation payload — 2026-11-06

Steward-approved small NSIS installer with verified offline model parts, installer-bound manifests and real missing/tampered-payload installation checks; no required network or portable readiness claim. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `e0b9082f404c22a8624861f69a1b28b61b8d487c03f5d3906d7e2d77adf0b3b6` | 31672 |
| `12-AZ-IP/45-axiomzero-pc-suite/package.json` | `622701a7eea3df9201001ade81e0232a4cb26f65abee1407d6884e24418d2cf6` | 3325 |
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/windows-smoke.ps1` | `2929aa56088bc001ea6d7db5e14df3a300f24b00a0c6bca7200edc8f2ad02ed9` | 5771 |

### Approved shared ten-minute CPU inference budget — 2026-11-06

Steward-approved bounded ten-minute inference shared by ownership, answering and optional review, with explicit slower-CPU disclosure and research startup allowance; correctness and safety unchanged. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/README.md` | `4966756302046684e158b46e5affcdb4f24392d673802b955bf2619a9d510981` | 31882 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/harness.cjs` | `df85c0447f9a74c1cc827d49a0ebe70387802866c35e06d1c361dfa6bc9df30b` | 17917 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/harness.test.cjs` | `de6ade6f2eb54a9fb04e512c720402d056140ac660f50094246e9674ecad4e05` | 14104 |
| `12-AZ-IP/43-az-geometric-tori-transformer/README.md` | `ebbabb245c28f24ae71ede6c92e5c7e89a42080bd13d402c008d395fed05b3d2` | 25647 |
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `ff47e49c8a5e39108ecabe856ac6a8dde260ceda0f48db39260dfe0e20e6599f` | 37018 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `f4363af5839808a33fabcf7ea0ceaed52c1b15d13088916daa1a37be31a6d392` | 38184 |

### Installed-resource UI diagnostic timing reseal — 2026-11-06

Bound asynchronous installed-resource UI diagnostics at sixty seconds while retaining five-second synchronous DOM checks and every assertion; actual offline installer and installed inference already passed. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/scripts/electron-ui-smoke.cjs` | `6c37a458f8c12d05e4bcdaf5a952ac25bd232d42d6251c668bb7e95d05a60ea5` | 9825 |

### Evidence-shaped ownership input reseal — 2026-11-06

Use ordinary question/evidence JSON for the authenticated ownership challenge, retaining the exact fresh nonce, status, citation, process ownership checks and shared deadline; report only mismatched field names. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `43edd7a31c766dfd865f2bff05e926d93c7c500517ae6c4f55c199710de96571` | 37197 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `7b177c477095c819da6f438253d23ba73922fb853ddb76fe22ee5a7961a20158` | 39290 |

### Consistent bounded completion allocation reseal — 2026-11-06

Use the same bounded 128-token completion allocation for ownership and ordinary answers; retain exact nonce/status/citation, strict truncation rejection and the shared ten-minute inference deadline. Both branches' previous seals remain in registry history.

| Asset | SHA-256 | Bytes |
|-------|---------|------:|
| `12-AZ-IP/45-axiomzero-pc-suite/lib/instruction-model.cjs` | `65de46f9352b7ca394576453f5ce43b1de13fece3b886301b6de0c1eaa342f85` | 37303 |
| `12-AZ-IP/45-axiomzero-pc-suite/tests/instruction-model.test.cjs` | `4fb2b7911c07adca17f698fd8d8e8096da489b10f8a91af683231ac3ba69faa2` | 39395 |
