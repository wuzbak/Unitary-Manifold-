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

The desktop PsiCat handshake/query and sync push/pull transports reject HTTP
redirects, including redirects from loopback services. Real HTTP regression
tests exercise the runtime's shared transports after hostile settings and
sync-packet imports; they use ephemeral local ports, not shared service ports.
Pending backend responses apply push metadata to the latest local state and
merge pull packets into that latest state, preserving edits made during HTTP
requests. Delayed-response tests cover both directions.

```bash
cd 12-AZ-IP/24-psicat-web-browser
npm ci
npm start
```

### Desktop notes

- Electron provides the Chromium shell.
- The entry point is `package.json` → `desktop/main.js` (`npm start` → `electron .`).
- `desktop/main.js` is the guarded diagnostic bootstrap; the existing browser implementation is in `desktop/runtime.js`. Both must be staged.
- The desktop app attempts to launch the sibling Product 20 `../20-psicat-navigator/run.py`.
- The desktop app also launches `sync_backend/server.py`.
- Backend sync requires both a sync account email and a sync access token; the scaffold uses that token to guard account-scoped packet push/pull on the trusted endpoint.
- If Product 20 is unavailable, PsiCat falls back to clearly labeled local research summarization.

### Native Windows / Product 45 integration contract

Use the existing Electron app, not a substitute web launcher. Stage the package,
its UI and sidecar sources, an installed **Windows** Electron runtime, and a
Python 3.12+ interpreter. The suite must set environment variables on this
Electron process (not through browser settings or imported packets):

| Variable | Contract |
| --- | --- |
| `PSICAT_BROWSER_PYTHON` | Absolute Python executable path, without embedded quotes or arguments. Both sidecars use it verbatim as an executable, with separate argument arrays. An invalid override fails visibly, without falling back to an ambient interpreter. |
| `PSICAT_BROWSER_USER_DATA` | Absolute writable Product 24 directory. Created before Electron initializes; browser state, sync mirrors and the sync backend store live here, outside installed sources. If omitted, Electron's usual per-user `userData` is used. |
| `PSICAT_BROWSER_NAVIGATOR_RUN` | Optional absolute Product 20 `run.py` path; otherwise use the sibling source tree. This is a Python script contract, not a frozen executable contract. |
| `PSICAT_BROWSER_NAVIGATOR_REPO_ROOT` | Optional absolute repository source/resource root; otherwise inferred two directories above Product 20's `run.py`. Passed as the Navigator child `PYTHONPATH`, replacing ambient import roots. |
| `PSICAT_BROWSER_DISABLE_NAVIGATOR` | Set exactly `1` to disable browser-owned Product 20 startup, regardless of saved auto-start settings. Local research remains explicitly local. |
| `PSICAT_BROWSER_SUITE_IPC` | Set exactly `1` only when launching Electron directly with an inherited Node IPC channel; enables the private lifecycle protocol below. |

PowerShell example (replace paths with the suite's actual installed assets):

```powershell
$env:PSICAT_BROWSER_PYTHON = 'C:\Suite\Python\python.exe'
$env:PSICAT_BROWSER_USER_DATA = "$env:LOCALAPPDATA\AxiomZero\Product24"
$env:PSICAT_BROWSER_DISABLE_NAVIGATOR = '1'
Set-Location 'C:\Suite\12-AZ-IP\24-psicat-web-browser'
npm.cmd start
```

Standalone defaults are `py -3` on Windows (the Python Launcher must be
installed), and `python3` on POSIX. There is no shell expansion of executable
paths. Electron's single-instance lock prevents a second browser in the same
user-data directory from starting duplicate sidecars.

The mandatory sync sidecar uses only the Python standard library:
`python -u sync_backend/server.py --host 127.0.0.1 --port 8787 --store <userData>/sync-backend/sync_store.json --instance-id <per-launch-id>`.
Readiness requires `GET /api/sync/health` to return `ok: true`,
`service: "psicat-sync-backend"` and the matching launch ID.

Optional Navigator startup uses
`python -u <Product20>/run.py --host 127.0.0.1 --port 8020 --no-open --local-execution off`.
Its interpreter needs Product 20's `requirements.txt` (numpy, scipy, sympy,
httpx), that product's source/resources, **and the canonical repository**
`src/` and resources. Product 20 imports
`src.infrastructure.execution_spine` on startup; its pip requirements alone
are insufficient. The launch adapter supplies the canonical repository root
as `PYTHONPATH` so those imports work when its working directory is Product 20.
Product 20 also eagerly loads `bot/assistant_api.py` and `bot/rag_index.py`;
their import chain requires `bot/__init__.py`, `bot/session_bootstrap.py` and
`bot/research_resources.py` (plus the existing `src/core/pillar258_trusted_open_resource_registry.py`).
An isolated source-filter reproduction excluding `bot/` failed before serving
with `FileNotFoundError` for `bot/assistant_api.py`; including the genuine
source-only `bot/` subtree allowed the actual server imports. These dependencies
must be staged; browser launch does not substitute missing RAG implementations.
Readiness checks
`GET /api/psicat/status` for `psicat_available: true` and handshake profile
material; readiness is **not** evidence of model competence or live inference.
The browser-owned process does not inherit `PSICAT_LOCAL_EXECUTION_TOKEN`,
`MERLIN_PROFILE_SHARED_KEY`, or `MERLIN_SESSION_SECRET`. Query handshake
cookies remain main-process memory; no suite token-sharing mechanism was added.

Both ports must be free. An occupied port fails visibly; this app never silently
adopts or kills a separately managed service. If Product 45 already runs Product
20 on 8020, disable browser-owned Navigator startup. Connecting to that existing
instance with an explicit identity/authority policy is a separate integration
gap, not implemented here. Product 20's own persistence/resource layout also
remains that product's responsibility.

Spawn failures, early exits and bounded health-check failures appear in the
desktop status line. Health requests do not follow redirects. Timed-out starts
are terminated. Quit waits for specific owned child processes, with bounded
TERM/KILL escalation; no name-based process kills are used. This covers normal
Electron shutdown, not forced termination of Electron or a machine crash.

#### Suite-owned graceful lifecycle (required instead of Windows `child.kill()`)

**Runtime patch status, checked 2026-11-04:** this package now pins Electron
**44.10.2**, verified against npm metadata and the official release. This is
the latest maintained patch in major 44:
[44.10.2](https://github.com/electron/electron/releases/tag/v44.10.2)
(2026-11-03), and the latest stable major release is
[45.2.2](https://github.com/electron/electron/releases/tag/v45.2.2).
Electron's [support policy](https://github.com/electron/electron/blob/main/docs/tutorial/electron-timelines.md)
supports only the latest minor in each of the three supported major lines.
44.10.0 fixed File System Access blocklist gaps for `.git/hooks` writes and
hypervisor UNC shares; subsequent releases include Chromium/V8 and other
upstream backports. The stale 44.3.0 pin was replaced without a major upgrade
or unrelated dependency upgrades. On this tested lock, the existing browser
tests (6), Node tests (51; 1 opt-in skip), Python tests (10), lint and opt-in
actual Linux Electron UI/IPC start/failure/graceful-stop test all passed.
This resolves the stale-runtime blocker, not native Windows validation or
production certification. An ongoing browser update policy remains necessary.

The tested `package-lock.json` SHA-256 is
`6f86c7010894f91af8f3ffc40cb884e2d52f21ea0121e2a3066ec7db4f9d958e`.
The Windows native entry point after installing the Windows artifact is
`<Product24>/node_modules/electron/dist/electron.exe`; preserve the **entire**
`dist` directory, including Chromium resources/locales/DLLs, not just the EXE.
`node_modules/electron/path.txt` must say `electron.exe`, and `dist/version`
must match the approved lock. Linux's installed `dist/electron` cannot be
reused as a Windows artifact. Avoid `require('electron')` as a runtime discovery
probe: this package can download a missing binary as a side effect.

Provision using the suite's approved Node executable and npm **JS CLI**,
never `npm.cmd`, shell command strings or an npm wrapper as the supervised
process. For example, pass these as argument arrays to `spawn` with
`shell: false` and `cwd: product24Directory`:

```javascript
// Restore the locked packages, including the Electron dev dependency.
spawn(approvedNodeExecutable,
  [approvedNpmCliJs, 'ci', '--include=dev', '--ignore-scripts', '--no-audit', '--no-fund'],
  { cwd: product24Directory, env: provisionEnvironment, shell: false });
// After successful restore, explicitly provision the locked native artifact.
spawn(approvedNodeExecutable,
  [path.join(product24Directory, 'node_modules', 'electron', 'install.js')],
  { cwd: product24Directory, env: provisionEnvironment, shell: false });
```

Wait for each provisioning child to exit successfully before proceeding.
For cross-platform staging set `ELECTRON_INSTALL_PLATFORM=win32` and
`ELECTRON_INSTALL_ARCH=x64` or `arm64` to match the target; actual Windows
staging uses its native defaults. Verify the installed artifact/version before
launch. The locked installer requires provisioning Node >=22.12.0.

The suite must launch the **Electron executable directly**, not `npm`, when
using supervision. A Node parent can use:

```javascript
const child = spawn(electronExecutable, [product24Directory], {
  cwd: product24Directory,
  env: {
    ...process.env,
    PSICAT_BROWSER_SUITE_IPC: '1',
    PSICAT_BROWSER_PYTHON: suitePythonExecutable,
    PSICAT_BROWSER_USER_DATA: product24UserDataDirectory,
    PSICAT_BROWSER_DISABLE_NAVIGATOR: '1',
  },
  stdio: ['ignore', 'pipe', 'pipe', 'ipc'],
  shell: false,
  windowsHide: true,
});
```

Do not set `ELECTRON_RUN_AS_NODE`. This launches the real desktop window.
The inherited process channel is the authority boundary: there is no network
shutdown endpoint, token, renderer API, or credential-bearing ready payload.
Setting suite mode without an IPC channel is a startup error.

Messages use `protocol: "psicat-browser-lifecycle-v1"` and `product_id: 24`:

- `ready`: emitted only after the desktop UI file loads, tab views mount and
  the mandatory sync sidecar passes its instance-specific health check.
  Includes public `sync`/`navigator` status, PID, loopback base URL and error.
  Navigator may be explicitly disabled, but **when enabled it must also be
  ready**; a failed/missing enabled Navigator produces `startup-failed`, not a
  false successful desktop start. Healthy status does not certify inference.
- `boot`: credential-free bootstrap phases and actual IPC availability,
  platform and Electron version. These are diagnostic only, never ready.
  In suite mode the same records are appended to
  `<PSICAT_BROWSER_USER_DATA>/product24-startup.jsonl` so Windows console
  redirection cannot hide all main-process diagnostics. Unknown exception
  reports include phase/name/code, not exception messages, stacks or environment.
  A startup failure additionally includes allowlisted `component` (`ui`, `sync`,
  `navigator`, `bootstrap`), `components` status/error classifications, and
  fixed repository-relative `resources` existence checks. The **first**
  `startup-failed` message's human-readable error identifies the failed
  component, code, Python exception class and recognized missing import/resource.
  Sidecar stderr is drained through an 8 KiB parser window; raw output and
  traceback paths are never transmitted or written to diagnostic files.
  Unknown module/resource names are redacted. Component fields include
  `failure_code`, `exit_code`, `exit_signal`, `spawn_code`, `python_error`,
  `missing_module`, `missing_resource`, `health_http_status` and
  `health_payload_valid` when available. Health response bodies, handshake
  credentials and arbitrary exception messages are excluded.
  An empty/missing file and no `entry` IPC record means the Product 24 entry
  was not observed running; it does not establish a Node IPC limitation.
- `state`: public state changes, **not** startup-success evidence. After ready,
  a required sync status other than `ready` must invalidate suite readiness.
- `startup-failed`: includes an error; no `ready` follows. Suite-mode startup
  failure initiates owned-process cleanup and exit without a blocking dialog.
- Parent shutdown request:
  `{protocol: "psicat-browser-lifecycle-v1", type: "shutdown", request_id: "suite-stop-1"}`.
  Correlation must contain 1–80 ASCII letters, digits or hyphens.
- `stopped`: sent after all owned Python children have actually closed;
  echoes the shutdown `request_id` (or `null` for user-initiated quit), then
  Electron quits. The suite must wait for **both this message and child exit**.
- `shutdown-failed`: cleanup failed; no successful-stop acknowledgement or
  forced Electron exit is substituted. Surface the failure to the operator.

Allow at least 20 seconds for startup and 10 seconds for graceful shutdown.
Do not mark started on `spawn`, an open port or `state`; wait for `ready`.
Do not treat exit code alone as start/stop success. IPC disconnect requests
the same owned-child cleanup, so a normally disconnected supervisor is handled.
Neither IPC nor Python cleanup protects against a hard-killed Electron process
or OS crash. A timeout is an explicit supervision failure: blindly killing the
Electron parent on Windows can orphan sidecars. Strong forced-termination
guarantees would require suite-owned Windows Job Objects/process-tree handling,
which this adaptation does not implement.

### Accountable desktop interrogation

Interrogate sends only the active captured page/selection by default. The
unchecked sharing control explicitly adds non-private saved pages, notebook
entries and imports; private artifacts are excluded, and private-tab queries
are blocked before any network request. Context is capped at 32,000 UTF-8
bytes and the question at 4,000 characters. Over-budget input is rejected
visibly rather than silently truncated as a whole.

The Product 20 handshake now carries the returned session cookies and uses the
dedicated handshake-profile token field, not the separately protected
profile-resume field. Status and query HTTP failures,
missing handshake material and invalid answers are explicit; local fallback is
never labeled as successful PsiCat inference. Responses display request
correlation, source URL, sharing scope and returned provenance, without
exposing handshake credentials. No web crawl is requested by this client.
The desktop keeps its sidecar cookie only in main-process memory between
questions, so successive queries resume the same server session; it is not
included in browser state, notebook/sync records, or UI responses, and is
cleared when all windows close.

Queries have a 35-second combined handshake/query deadline and a Cancel query
control. Cancellation stops the local HTTP wait; it does not promise to undo
server work or erase a session already received by Product 20. This adapter
does not write notebook entries, sync records, or promote memory, but existing
Product 20 session/retention behavior still applies. Existing automatic browser
capture/storage is unchanged. The reported source is the captured snapshot,
which may be older than a page changed since capture.

This tranche covers desktop transport and UI, not production identity/sync,
Android/extension parity, a Base44 page-agent port, or model reasoning
certification. See the [integration master plan](../../docs/PSICAT_ECOSYSTEM_INTEGRATION_MASTER_PLAN.md).

## Vite Web Workbench

Product 27 is a separate local Vite development tool with native Product 20 actions. When its loopback service is running, open `http://127.0.0.1:8327/` in a normal browser tab to scaffold, preview, and build workbench projects. The Product 24 Electron browser can use the same address through its address bar; Vite previews open as separate loopback origins. Keep the service local and only preview project code you trust.

## Test standard

- **Playwright is now the default browser test standard for Product 24.**
- Run the proving ground first from:
  `cd /home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/24-psicat-web-browser && npm test`
- The default test script now runs Playwright browser coverage before the targeted Node unit tests.

### Loopback service endpoint restrictions (not an OS sandbox)

`psicatEndpoint` and `syncBackendEndpoint` describe the local research/sync
services, not general browser-tab traffic. Ordinary tabs can browse remote
websites. `desktop/lib/browser-core.js::normalizeState`
is the single chokepoint every path that can set those settings passes
through — the `browser:update-settings` IPC handler, a workspace restore,
and merging an **imported sync packet** all end in a call to
`normalizeState` — and it now unconditionally clamps both endpoints back to
their safe `http://127.0.0.1:*` defaults whenever they are missing or
resolve to anything other than `127.0.0.1`/`localhost`/`::1`. This closes a
real gap: previously an imported sync packet (or a typo'd settings field)
could silently redirect every PsiCat query and sync push/pull to an
attacker-controlled remote endpoint.

Verified by:

- `tests/browser-core.test.js` — unit tests for `isLoopbackEndpoint`,
  `enforceLoopbackEndpoint`, and `normalizeState` rejecting a hostile
  endpoint from both a settings patch and an imported sync packet.
- `tests/e2e/network-sandbox.spec.js` — a real Chromium instance renders
  the production `desktop/ui/app.js`/`app.css` with only the Electron
  preload bridge (`window.psicatBrowser`) stubbed; Playwright's network
  listener asserts **zero requests** leave loopback across a full
  interaction session, including an explicit attempt to redirect both
  endpoints to `https://attacker.example/exfiltrate` via the Settings panel.

The privileged preload belongs only to the local desktop UI. Browser views
have no preload or Node integration, and all browser IPC checks the exact local
UI main frame. The desktop UI cannot navigate to remote content; external-open
and popup URLs are restricted to HTTP(S). The sync scaffold rejects remote
web-page origins while retaining native/no-origin and local-origin clients.
These are application boundaries, not proof of OS-level confinement or a
production-grade sync identity system.

### Portability/lifecycle validation

From this product directory:

```bash
npm run test:unit
python -m unittest discover -s tests -p 'test_*.py' -v
npm run lint
npm test
```

The Playwright UI server uses the same platform-aware Python selector and
`PSICAT_BROWSER_PYTHON` override; it never assumes `python3` on Windows.

Node coverage includes private suite lifecycle message validation/credential
exclusion, Windows interpreter selection, spawn/exit failures,
port collisions, health-body timeouts, startup cancellation, process-specific
escalation, and a real Python sync process with per-user storage and verified
shutdown. An opt-in actual Electron test additionally exercises the production
UI/IPC and sidecar lifecycle, plus actual direct Electron IPC success,
invalid-interpreter startup failure without false ready, and correlated
graceful shutdown with verified Python process exit:

```bash
mkdir -p .test-work
TMPDIR=.test-work PSICAT_BROWSER_ELECTRON_TEST=1 xvfb-run -a node --test tests/desktop-runtime.test.js
```

On Windows set `$env:PSICAT_BROWSER_ELECTRON_TEST = '1'` and run
`node --test tests/desktop-runtime.test.js` without Xvfb. There is no win32
skip: the opt-in test always covers enabled real Product 20, both sidecar
health checks and PID cleanup, missing Navigator, bad interpreter and bootstrap
failure, in addition to local UI/IPC. Install Product 20 requirements in the
test Python first; the test resolves setup-python's `python` on Windows
(or the explicit `PSICAT_BROWSER_PYTHON`) rather than accidentally selecting a
different ambient installation via `py -3`. Local Linux root
testing disables Chromium's sandbox only for that test; production launch does
not add `--no-sandbox`. Linux test success and mocked Windows command selection
do **not** constitute successful native Windows execution.

For a faster Windows **GUI inherited-IPC discriminator**, after installing
Electron run `node tests/run-ipc-probe.js` using the approved Node executable
(or on Linux: `TMPDIR=.test-work xvfb-run -a node tests/run-ipc-probe.js`).
It launches the actual Electron binary directly, loads a hidden sandboxed
`about:blank` window, checks IPC in both directions, requests a correlated
graceful exit, and reports actual exit code/signal and boot records on failure.
It downloads nothing and starts no Python/model services. Its
`ipc-probe-ready` is explicitly **not** Product 24 readiness. This probe plus
the full desktop test separates transport/GUI behavior from source/resource
provisioning without rebuilding the portfolio.

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
