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
