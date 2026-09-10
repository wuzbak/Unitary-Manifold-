# AxiomZero Browser & AI Testing Doctrine

This doctrine defines how browser-facing AxiomZero products are tested on this branch while Product 24 develops deeper Playwright conventions on a parallel branch.

## Canonical defaults

- **Playwright is the canonical browser automation layer** for AxiomZero browser products.
- **Product 24** remains the proving ground for deeper fixture, browser-matrix, and CI lessons on the parallel branch.
- **Cypress is not a default tool** in this repository-wide rollout.
- **Appium is reserved for true mobile/native products** such as `12-AZ-IP/14-sdam/` and `12-AZ-IP/15-pentacorder/`.

## Integration classes

### Class A — Deterministic browser/static apps

- `12-AZ-IP/17-um-image-generator/`
- `12-AZ-IP/18-um-reader/`
- `12-AZ-IP/19-falsification-observatory/`
- `12-AZ-IP/21-geo-monitor/`

These products use Playwright as a **product-contract verifier**:

- launch and render checks
- key control-path validation
- cross-browser execution matrix
- local/offline shell integrity
- accessibility-smoke selectors
- screenshot capture for layout-sensitive review surfaces

### Class B — Browser + backend + AI interaction surfaces

- `12-AZ-IP/20-psicat-navigator/`
- `12-AZ-IP/23-psicat-dm-assistant/`

These products use a layered stack:

- **Playwright** for browser workflow reliability
- **API contract tests** for backend stability
- **Promptfoo/DeepEval-style AI evaluation artifacts** for response-quality, contract-shape, and drift monitoring
- **Telemetry/readiness surfaces** for observability and rollout gating

### Class C — Platform/browser infrastructure

- `12-AZ-IP/01-axiom-os/`

This class absorbs the shared standard rather than leading it. The existing browser precedent in `12-AZ-IP/01-axiom-os/mcp/browser_server.py` should remain aligned with the canonical Playwright direction.

## Visual regression policy

Visual regression is a selective second-wave enhancement, not the first dependency to wire into every app.

- First targets: `18-um-reader`, `21-geo-monitor`
- Secondary target: `19-falsification-observatory`
- Deferred target: `20-psicat-navigator`

## PsiCat doctrine

PsiCat is the canonical example of **browser test + API contract + AI evaluation + observability** working together.

Its testing stack should keep these lanes explicit:

1. Browser shell reliability and session continuity
2. API contract verification for primary query, toolkit, orchestration, memory, telemetry, and readiness surfaces
3. Prompt/regression evaluation with observability-backed review artifacts

## Rollout rule

Adopt proven Product 24 lessons only after they are earned on the parallel branch. This branch establishes the shared doctrine, Class A browser contracts, and PsiCat-led layered validation without waiting for Product 24 to finish every experiment.

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
