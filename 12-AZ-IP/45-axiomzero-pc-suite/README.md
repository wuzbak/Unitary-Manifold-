# Product 45 — AxiomZero PC Suite

**Version 0.1.0 · Windows desktop portfolio launcher, local evidence search and governed research harness · readiness not assessed**

Product 45 is an offline-first desktop front door to the registered AxiomZero
portfolio. Its bundled catalog is built from the canonical `12-AZ-IP/README.md`
and includes Products 01–45. It helps an operator search products, tools,
calculators and engines, open local product documentation, and reach a
user-selected work folder. Loopback service links are opened only after an
explicit click.

The app is a launcher and portfolio guide, **not an installer for all 45
products**. It does not silently install Python/Node dependencies, start
services, download models, run arbitrary commands, or grant access to the
whole PC. Connect a local repository checkout to open its product folders and
guides. Individual products retain their own setup, runtime, privacy and
readiness boundaries. For example, PsiCat Navigator is a separate local
service; Product 45 does not impersonate a running model or bypass its
handshake.

## What works offline

- Search the bundled 45-entry catalog and inspect product/version/readiness
  summaries without a network connection or repository checkout.
- Connect or disconnect a checkout using the native folder picker. Product
  actions are limited to registered portfolio folders and README files.
- Open shared `apps`, `calculators`, `engines`, `tools`, `os`, and `lib`
  collections, or select a work folder through the native folder picker.
- Open the local PsiCat Navigator at `127.0.0.1:8020` when Product 20 is
  already running.
- Open the bundled software notice; packaged builds include the AGPL license
  and portfolio license schedule.
- Persist the chosen checkout path in the current Windows user profile.
- Import a user-selected source folder or ZIP into a private, local evidence
  library. Search returns deterministic keyword matches with file/line
  citations and SHA-256 digests; it does not invent an answer or claim to be a
  running PsiCat model. The Webspace seed and PsiCat Mind exports are supported
  as local sources.

The evidence library indexes UTF-8 text and source formats only. It inventories
but does not read PDFs, office documents, images, binaries, or other unsupported
formats. A collection is limited to 10,000 source entries, 256 MiB per ZIP,
512 MiB expanded, 8 MiB per indexed text file, and 64 MiB total indexed text;
at most five collections are retained. The app reads ZIP contents directly and
does not extract, execute, modify, or upload imported files. Oversized files,
excluded dependency/build folders, and unsupported formats are reported in the
collection summary.

The index contains plaintext copies of indexed source text and is stored in the
current Windows user's application data without encryption. Protect the Windows
account and imported data accordingly. “Remove index” deletes only Product 45's
local index; the original folder or ZIP remains untouched. Re-import or refresh
is explicit.

The app makes no automatic network requests. An explicitly approved optional
research step can contact the fixed local Ollama service described below.
“Open local service” hands a
catalogued `localhost`/`127.0.0.1` address to the system browser; the target
service must already be running. The PsiCat shortcut likewise opens the
documented local Product 20 UI; Product 20 handles its own session handshake
and query policy. Other online capabilities belong to their individual products.

## Windows installable build

The Windows workflow builds both a per-user NSIS installer and a portable
executable. From a Windows checkout with Node.js 22, Python 3.12 and internet
access for dependency/bootstrap downloads:

```powershell
cd 12-AZ-IP/45-axiomzero-pc-suite
npm ci
npm test
npm run catalog:check
npm run dist:win
npm run smoke:win
```

Artifacts are written to `dist/`. `npm run smoke:win` silently installs and
uninstalls the per-user NSIS build, launches both installed and portable
applications, and verifies that the window renders all 45 products and the
local evidence controls, creates a research plan and cancels it through the
preload bridge without renderer exceptions. The repository workflow
`.github/workflows/pc-suite-windows.yml` builds and uploads them as a workflow
artifact on pull requests and manual dispatch. Each executable is accompanied
by a SHA-256 checksum. A `pc-suite-v*` tag additionally publishes the installer
and portable executable as a GitHub Release. Builds are currently
**unsigned**; Windows SmartScreen may show a publisher warning. No automatic
update service is included. The configured artifacts target Windows x64;
ARM64 builds and installer upgrades remain unverified. Per-user x64 install,
rendered UI, uninstall and portable launch are exercised by the Windows workflow.

To run from source:

```powershell
npm run start
```

`npm run catalog` regenerates the embedded offline catalog after the master
registry table changes. `npm run catalog:check` fails when the checked-in
catalog is stale.

## Trust and operational boundary

The renderer has no Node.js access and uses a context-isolated, sandboxed
preload bridge. The bridge exposes only fixed catalog, folder-picker, portfolio and research
actions; it accepts product/task IDs and fixed category names rather
than arbitrary filesystem paths or commands. Local service URLs are restricted
to loopback. The app does not open arbitrary external links, run shell
commands, access browser passwords, or elevate privileges.

The selected checkout path and its availability are stored in the user's
application settings. Protect the Windows account and the selected checkout
as usual. Product 45 does not provide repository authentication, encrypted
sync, service health monitoring, or a full backup/restore facility.

## Validation

```powershell
npm test
npm run catalog:check
```

These checks cover catalog integrity, repository-path containment, settings,
ZIP safety, local indexing, evidence citations, index persistence, harness
approvals/state recovery/budgets/cancellation/audit seals, worker execution
and the local reasoning transport. The Windows workflow verifies per-user
installation/UI/uninstall and portable launch. Installer upgrades and a
publisher code-signing certificate remain release work; a successful packaging job is not a claim
that every portfolio product is installed or Windows-compatible.

## Advanced harness control

### Hardware assessment before model selection

Use **Detect this PC** in **PC readiness assessment**. After native consent,
the suite measures CPU, total/available RAM, free space on its application-data
volume, and Electron's graphics-device diagnostics. No shell commands, network
requests, model downloads or training run. Detection has a 15-second deadline;
failures are surfaced. No hostname, account name or device serial is collected.
Results stay in memory until explicitly exported as JSON.

Conservative screening checks x64, at least 8 GiB total RAM, 4 GiB currently
available RAM and 10 GiB free disk. Meeting these thresholds only permits
**model evaluation**, not automatic selection or certification. Graphics-device
identifiers are not reliable measurements of dedicated VRAM or CUDA capability;
these remain explicitly unverified. Training readiness is never inferred.
The exact licensed model and its measured memory/latency/context requirements
must still be approved before any provisioning. No deployment-quality PsiCat
weights have been bundled. Product 43's existing causal character-level
train/resume/sample workflow is experimental, not a production assistant.

### Task execution

The **Research control plane** is an executable, read-only research harness,
not just a prompt wrapper. Its HILS-aligned default-deny policy is independent
of physics claims. Create a goal, inspect the fixed dependency-ordered plan,
and choose **Review & run next step**. A native dialog discloses the action;
approval applies only to that checkpoint and step. Neither a model nor
imported text can approve a tool or add a new capability.

The built-in workflow searches the bundled catalog, searches persisted local
evidence in a cancellable worker, and composes a report containing references
and source excerpts. It does not pretend keyword retrieval inferred an answer.
No match is explicitly reported as an evidence gap. Optional local reasoning
adds one final step using Ollama at `http://127.0.0.1:11434/api/chat`; install
and start Ollama and download a model separately, then enter its exact
installed model name. The suite never installs models, chooses a cloud
fallback, follows redirects, or accepts model tool calls. Before sending the
goal and bounded evidence context, it requires another native approval.
The local provider has its own retention and operational policy. Generated
output is prominently **UNVERIFIED**, not a proof or a verified PsiCat answer.
No live Product 20 session is fabricated; the existing Navigator shortcut
continues to use Product 20's own handshake and policy.

Tasks persist incrementally in `research-harness.json` under Electron's
per-user application data. Each result is committed before acknowledgement.
Pause/cancel aborts active work; already completed results remain available.
A restart marks in-flight execution interrupted and requires new approval.
Failed steps show their error and can be explicitly retried within the
**six-attempt total budget**; there are no hidden retries or unconstrained
loops. Each execution has a **60-second deadline**, evidence search runs
outside the main UI thread, outputs are capped at **24,000 characters**, and
context at **12,000 characters**. Context truncation is disclosed; full
results remain in step checkpoints. The optional local model response is
limited to 64 KiB of JSON and 16,000 output characters.

Up to **50 tasks** and **2,000 audit events** are retained. Export a task and
the entire bounded audit chain to an explicitly chosen JSON file; cancel or
complete a task before removing it. Removal deletes the task and results,
not original sources; audit metadata is retained until the event window rolls
over. The rolling chain retains a hash anchor. Audit hashes also bind task
checkpoints and detect accidental edits, but are **not tamper-proof signatures**:
someone able to rewrite this user's files can recompute them. Invalid stores
fail closed with a startup error rather than silently reset or replay.

The harness has no arbitrary shell, source-write, external-network, finance,
legal-action, privilege-elevation or epistemic-promotion tools. Worker isolation
keeps search responsive but is **not an OS security sandbox**. This deliberately
bounded control plane does not install or orchestrate all 45 product runtimes.
Its task/results/audit exports are plaintext local data, not encrypted memory
or an automatic cross-product profile export.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
