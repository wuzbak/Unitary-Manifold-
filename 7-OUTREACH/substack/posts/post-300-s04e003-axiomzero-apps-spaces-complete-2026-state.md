# AxiomZero Apps & Spaces: Complete 2026 State

**Unitary Manifold — S04E003 · v35.7**

---

This post is a full application-surface inventory for the current repository state.  
It is not a physics-claim promotion post. It is an engineering/status post.

Canonical status source for all live counts in this post:

- `STATUS.md`
- `9-INFRASTRUCTURE/um_live_status.json`

---

## Executive summary

- The canonical software registry currently tracks **23 products** in `12-AZ-IP/README.md`.
- Merlin is split into two distinct products:
  - **Product 20:** Merlin Navigator (repository-grounded navigator, OX-compatible)
  - **Product 23:** Merlin DM Guide & Player Assistant (offline-first D&D campaign system)
- CI was not fully green at intake because of a fingerprint-registry tamper mismatch; that blocker has been corrected in this implementation pass.
- Public and submission-facing surfaces were updated to reduce stale-version drift.

---

## Product map (1–23)

Reference registry: `12-AZ-IP/README.md`

| Product | Name | Primary surface |
|---|---|---|
| 01 | Axiom OS Core Suite | `12-AZ-IP/01-axiom-os/` |
| 02 | AZ-KERNEL Rust Kernel | `12-AZ-IP/02-az-kernel/` |
| 03 | EIGE Governance Engine | `12-AZ-IP/03-eige/` |
| 04 | UM-SOS Scientific OS | `12-AZ-IP/04-um-sos/` |
| 05 | UOS Kernel Prototype | `12-AZ-IP/05-uos-kernel/` |
| 06 | Omega Synthesis Engine | `12-AZ-IP/06-omega-synthesis/` |
| 07 | Holon Zero Engine | `12-AZ-IP/07-holon-zero/` |
| 08 | AxiomZero Journalist AI | `12-AZ-IP/08-axiom-journalist/` |
| 09 | OmegaHolon Engine | `12-AZ-IP/09-omegaholon/` |
| 10 | Filmer’s Companion | `12-AZ-IP/10-filmers-companion/` |
| 11 | Terra OS | `12-AZ-IP/11-terra-os/` |
| 12 | Lithos OS | `12-AZ-IP/12-lithos-os/` |
| 13 | Delphi | `12-AZ-IP/13-delphi/` |
| 14 | SDAM | `12-AZ-IP/14-sdam/` |
| 15 | Pentacorder | `12-AZ-IP/15-pentacorder/` |
| 16 | AxiomZero Ω Oracle | `12-AZ-IP/16-oracle/` |
| 17 | UM Physics Image Generator | `12-AZ-IP/17-um-image-generator/` |
| 18 | UM Reader / Educator | `12-AZ-IP/18-um-reader/` |
| 19 | Falsification Observatory | `12-AZ-IP/19-falsification-observatory/` |
| 20 | Merlin Navigator (OX-compatible) | `12-AZ-IP/20-merlin-navigator/` |
| 21 | UM Geophysical Monitor | `12-AZ-IP/21-geo-monitor/` |
| 22 | AxiomZero SGE | `12-AZ-IP/22-az-sge/` |
| 23 | Merlin DM Guide & Player Assistant | `12-AZ-IP/23-merlin-dm-assistant/` |

---

## Spaces and deployment surfaces

Primary deploy index: `hf-spaces/README.md`

| Surface | Role |
|---|---|
| `hf-spaces/az-portal/` | public hub |
| `hf-spaces/oracle-space/` | synthesis assistant surface |
| `hf-spaces/cmb-calc-space/` | calculator suite |
| `hf-spaces/axiom-apps/` | app cluster (01–10) |
| `hf-spaces/az-tools/` | app cluster (11–20) |
| `hf-spaces/vqe-sandbox/` | quantum adjacent lane |
| `hf-spaces/az-os/` | OS-facing aggregation surface |
| `hf-spaces/az-ip/` | IP catalog surface |
| `hf-spaces/um-knowledge-dataset/` | RAG dataset surface |

---

## Merlin now means two products, not one

### Product 20 — Merlin Navigator

Canonical product doc: `12-AZ-IP/20-merlin-navigator/README.md`

Key points:
- Merlin API surface is first-class (`/api/merlin`, `/api/merlin/status`, toolkit endpoints).
- `/api/ox` is preserved as compatibility.
- Local/offline-first is primary; external router fallback is optional compatibility mode.

### Product 23 — Merlin DM Guide & Player Assistant

Canonical product doc: `12-AZ-IP/23-merlin-dm-assistant/README.md`

Key points:
- Separate DM and player dashboards.
- Invite-code joins and character import.
- Offline-first D&D 5e/5.5e campaign operations with rules-aware Merlin support.

---

## Readiness and remaining pressure points

| Area | Current state | Pressure point |
|---|---|---|
| Registry integrity | Corrected for current `IP_REGISTRY.json` tamper drift | Keep fingerprint updates synchronized when tracked assets change |
| CI / tests | Targeted blocker identified and fixed in this pass | Re-run full pipeline after each registry-affecting change |
| Public app hub | Product coverage expanded to include 22 and 23 | Continue removing stale version/count strings |
| Submission metadata | Zenodo/arXiv guides moved toward canonical-sync wording | Keep metadata aligned with live status before each publication |
| Merlin naming | Product naming now normalized in main hub and navigator page | Continue migration while preserving compatibility shims |

---

## Known open items (not hidden)

These remain explicit in canonical truth surfaces:

- `CMB_AMP_CONFIRMED_IRREDUCIBLE`
- `ALPHA_S_TYPE_B_FLOOR`
- `HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW`
- `CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED`
- `FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED`
- `JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED`
- `DESI_DR3_MONITORING`
- `LITEBIRD_BIREFRINGENCE`
- `NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT`

References: `STATUS.md`, `FALLIBILITY.md`, `docs/CLAIM_MASTER_BOARD.md`, `docs/TRUTH_LAYER.md`

---

## Bottom line

The Apps & Spaces layer is now closer to a coherent 23-product surface with clearer Merlin separation and less stale outward-facing state.  
The remaining work is operational discipline: keep registry integrity, CI health, and public metadata synchronized every time the underlying system changes.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
