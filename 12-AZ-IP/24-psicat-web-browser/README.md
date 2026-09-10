# PsiCat Web Browser
## Product 24 — Advanced desktop + Android browser with embedded PsiCat

PsiCat Web Browser is the canonical **Product 24** browser surface for AxiomZero: a Chromium-based, AI-native, integrity-first browser with **Electron desktop**, a **native-tab Android shell**, a **research notebook sidebar**, **import/export**, and an **extra-credit Chrome/Edge extension** companion.

> **Integrity first:** this product distinguishes clearly between local heuristics, remembered research context, and live PsiCat responses. It does not claim a custom rendering engine; it builds on Chromium/WebView industry standards and innovates in the workspace, research, and agentic capability layers.

## What ships in this foundation

- **Desktop Electron browser shell** with tabs, navigation, settings, bookmarks, history, downloads, session restore, reopen-closed-tab flow, split-workspace controls, saved workspaces, sync packet import/export, and embedded PsiCat research sidebar.
- **Advanced PsiCat sidebar** with live active-page awareness, remembered page context, multi-page summary/interrogation, notebook entries, and import/export.
- **Android native-tab browser foundation** with toolbar navigation, tab strip, settings screen, notebook drawer, session restore, bookmark/history persistence, sync packet import/export, backend sync buttons, and contextual page capture.
- **Chrome/Edge extension foundation** with side panel, local notebook, page capture, import/export, and optional local PsiCat endpoint integration.
- **Local sync backend scaffold** shared by desktop and Android for account-scoped push/pull packet exchange.
- **Resume ledger** so implementation state is visible if work is interrupted.

## Folder structure

- `desktop/` — Electron desktop browser runtime
- `extension/` — Chrome/Edge extension companion
- `android/` — native Android browser shell
- `sync_backend/` — local Python sync scaffold for desktop + Android packet exchange
- `tests/` — Playwright browser tests plus targeted Node/Python coverage for shared state and sync scaffolds
- `SESSION_RESUME.json` — interruption-safe execution ledger

## Desktop quick start

```bash
cd /home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/24-psicat-web-browser
npm install
npm start
```

### Desktop notes

- Electron provides the Chromium shell.
- The desktop app attempts to launch Product 20 locally from:
  `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-psicat-navigator/run.py`
- The desktop app also launches a local sync scaffold from:
  `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/24-psicat-web-browser/sync_backend/server.py`
- Backend sync requires both a sync account email and a sync access token; the scaffold uses that token to guard account-scoped packet push/pull on the trusted endpoint.
- If Product 20 is unavailable, PsiCat falls back to clearly labeled local research summarization.

## Test standard

- **Playwright is now the default browser test standard for Product 24.**
- Run the proving ground first from:
  `cd /home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/24-psicat-web-browser && npm test`
- The default test script now runs Playwright browser coverage before the targeted Node unit tests.

## Android structure

The Android app is a native-tab shell intended for Android Studio / Gradle import. It includes:

- tabbed WebView browsing
- settings activity using industry-standard preferences
- notebook drawer with local persistence
- import/export via Android document pickers
- session/bookmark/history persistence in shared preferences
- sync account metadata carried in exported packets plus backend push/pull scaffold hooks
- Android backup is intentionally disabled for now because notebook, history, and sync metadata still live in shared preferences in this scaffold
- active page capture for PsiCat-style research workflows

## Extension structure

The extension is designed for **Chrome and Edge** using Manifest V3 side-panel APIs. It provides:

- current-page capture
- notebook and remembered-page storage
- optional endpoint-backed PsiCat interrogation
- import/export for research packets

## Honesty boundary

Implemented now:
- desktop tabs, navigation, settings, notebook, bookmarks/history/download visibility, import/export, split-workspace layouts, saved workspaces, backend sync push/pull, local research memory, and Product 20 sidecar handshake client
- Android native browser foundation with settings, notebook, import/export, session restore, bookmark/history persistence, sync metadata, backend sync hooks, and page-context capture
- Chrome/Edge extension foundation with side panel and local/page-aware research tools
- local Python sync service scaffold for desktop/Android packet exchange on a trusted endpoint
- account-scoped sync token checks in the scaffold rather than open unauthenticated packet reads/writes
- Playwright browser-driven proving-ground tests for the desktop UI shell before PR-ready validation

Not yet fully implemented in this foundation:
- hardened production-grade cloud sync service backend
- cross-device authenticated account service
- true multi-pane split rendering parity across all shells (desktop now has a first scaffold; Android/extension do not)
- secure secret storage / rotation beyond editable local settings and Android preferences
- on-device large-model inference packaged inside the browser itself
- Android-grade isolated private browsing storage separate from standard WebView persistence

These are intentionally left explicit rather than implied.

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
