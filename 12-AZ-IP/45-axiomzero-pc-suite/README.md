# Product 45 — AxiomZero PC Suite

**Version 0.1.0 · Windows desktop portfolio suite, local evidence, native experimental PsiCat and governed runtime controls · production readiness not assessed**

Product 45 is an offline-first desktop front door to the registered AxiomZero
portfolio. Its bundled catalog is built from the canonical `12-AZ-IP/README.md`
and includes Products 01–46. It helps an operator search products, tools,
calculators and engines, open local product documentation, and reach a
user-selected work folder. Loopback service links are opened only after an
explicit click.

The app includes an actual **standalone native PsiCat character-model
executable and locally trained seed weights**, plus consent-gated provisioning
for registered Python products. It is **not yet an installer for every
portfolio target**: Android applications, UEFI components, other desktop
products, broken legacy launchers and POSIX-dependent services have explicit
limits rather than fake installation success. Individual products retain
their setup, privacy and readiness boundaries. No provisioned dependency
environment or responsive status endpoint constitutes full capability
certification. Product 20 handles its own handshake; its managed launch disables
local command execution.

## Embedded instruction assistant

The selected **Ask PsiCat** candidate uses Unsloth's Q4_K_M conversion of
Qwen3-4B-Instruct-2507, an instruction-only model, and a statically compiled,
revision-pinned CPU llama.cpp server. These are community-converted GGUF
weights, **not direct official Qwen GGUF weights**.
Actual backend acceptance remains a packaging prerequisite, not a claim that
the candidate has already shipped. No separate Python, Ollama or cloud model
service is needed for this path. This is a third-party pretrained language
substrate under the suite's evidence/governance controls, **not** our from-scratch
toroidal model and not proof of physical 5D information flow.

Each question requires native approval before matching catalog/library excerpts
are supplied to the model. Questions and evidence stay local. The renderer cannot
choose an executable, endpoint, API key or arbitrary filesystem path. The owned
server uses a fresh loopback port and API key, bounded CPU/context/output budgets
and explicit cancellation/shutdown. Retrieved text is reference data, not tool
authority; model output never runs tools, commands or file writes.
The client requests JSON-schema constrained decoding for ownership, answers
and optional review. The schema enforces the existing three keys, their
string/array types and the two permitted status labels, `UNVERIFIED` and
`UNSUPPORTED`. It does not choose between those labels or supply nonce,
answer or citation values, and does not prove grounding. Unsupported decoding fails explicitly;
no output repair or unconstrained retry replaces the strict response checks.
The shared candidate/runtime policy requires categorical labels without
explanatory prose and keeps refusal explanations about instruction authority
or unsafe actions separate from capability limits. Contract tests check that
both paths carry the same general rules; they do not establish that the real
candidate follows them. Native acceptance must be rerun after policy changes.
Answers use one generation and a 2,048-token CPU context by default. Hosted
run `42091109622` found no improvement from same-model review: the candidate
still passed only 3/4 cases, with identical incorrect retrieval draft and
revision. That unqualified extra cost is not enabled for normal inference.
Trusted main-process callers may explicitly set `enableModelReview: true`
for the experimental two-generation protocol, with a 4,096-token context.
It reviews the same task and evidence without grader feedback or expected
answers; only the unmodified final generation is validated, and review errors
never fall back to the draft. The returned `modelReview` record discloses
whether review was enabled, generation count and raw outputs. This is not
independent verification or demonstrated quality improvement. Opt-in generations
share the existing five-minute inference deadline and remain cancellable;
original question and evidence admission limits remain unchanged.

Failed-spawn and already-exited child handles are not signalled; cleanup still
waits for their close event within its deadline. Genuine signal errors remain
visible alongside the original operation failure, and incomplete shutdown
retains ownership and blocks another inference until explicit cleanup succeeds.
These lifecycle regressions do not qualify the actual model or Windows installer;
the exact candidate head still requires native Windows acceptance.

**Native checkpoint (2026-11-05):** the cleanup contracts pass on Windows.
The previous Qwen2.5-1.5B candidate failed the unchanged retrieval-injection
criterion despite passing arithmetic, instructions and grounded citations;
the historical Qwen3-1.7B Q8 diagnostic also failed. The larger instruction-only
candidate has not yet passed native acceptance. Packaging remains blocked;
this is not a pass or
an installer/model readiness certificate. The independent AZ IP Master Plan
work remains separate.

Answers remain UNVERIFIED. Citation IDs map to the supplied catalog or original
file/line/hash excerpts; valid IDs do not prove that the answer follows from
them. Missing evidence is not silently replaced by cloud requests. **Export answer
and evidence** saves only after native destination selection; exported reports
contain potentially private source excerpts and are not encrypted.

The research control plane accepts `psicat:embedded` for the same backend with
separate step approvals and a disclosed eighteen-minute CPU step budget,
including startup and a shared fifteen-minute inference budget. Other
steps retain their 60-second deadline. Excerpts are bounded to 1,200 UTF-8 bytes
for embedded research, or 600 bytes each for catalog/imported Ask PsiCat
references; this deliberately small context budget reflects measured baseline
CPU latency. Slow inference can still time out; a failed step requires fresh
approval and is not recorded as completed. Named external Ollama models retain
their separate explicit disclosure.

Windows packaging depends on actual instruction/citation/refusal acceptance.
The workflow verifies the conversion against Unsloth's LFS hash and exact
repository revision under the approved **3,000,000,000-byte model cap**.
Independent hosted acceptance retains its 600-second request deadline;
no answer, citation, refusal or authorization criterion is relaxed.
The ownership challenge and answer use the same system policy and JSON
envelope, allowing the owned engine to reuse prefilling work. The exact fresh
128-bit token, status and citation remain mandatory. The challenge evidence
contains only the token, so copying the entire evidence text does not require
interpreting a key/value prefix. Failed challenges expose bounded diagnostics
for that synthetic token only, not user evidence or the engine's API key.
Ownership, answering and
optional review share one steward-approved bounded fifteen-minute inference
budget; slower CPU performance is disclosed rather than presented as
interactive latency.
The literal-copy ownership question forbids inline citation markers in its
answer field; its citation belongs only in the citations array. Native
qualification requires three consecutive fresh-process governed passes,
stopping at the first failure, before the separate installed-runtime pass.
The steward-approved claim detector distinguishes explicit local negation
from positive execution claims; it does not certify general language safety.
It requires public, ungated Apache-2.0 conversion and official
`Qwen/Qwen3-4B-Instruct-2507` base metadata, and checks any declared base identity.
Provenance records both metadata snapshots; the observed official base revision
does not prove which revision Unsloth converted. This project has not reproduced
the conversion. The candidate is downloaded as supplied, not locally
requantized. The previous Qwen3-1.7B candidate
failed the retrieval case in both Q4 and original-Q8 paired evaluation; those
negative results remain recorded. A failed gate blocks
the installer. Source builds require the validated runtime artifact in
`build/instruction/`, including `manifest.json`, the declared GGUF,
`llama-server.exe`, model card, Apache license, provenance and pinned engine
source/license archive. No model weights or private exports are committed.
The reusable model gate also runs the governed Node client against the actual
candidate engine/weights before publishing that runtime artifact.
Installed smoke exercises the copied model, not an already running server.
Passing these checks does **not** establish expert-level general reasoning or
certify every portfolio target.
The higher file-size cap does not measure RAM use or qualify hardware. Existing
CPU threads, contexts, deadlines, default-off review and acceptance criteria
are unchanged; actual native latency/memory and installed behavior remain open.

## Android, UEFI and WSL deployment

The Windows packaging pipeline builds SDAM and Pentacorder debug APKs and the
locked AZ Kernel UEFI release binary from tracked source. It bundles those
artifacts with their actual SHA-256/size manifest. **Use bundled artifact
(offline)** verifies and copies the selected artifact into managed user data;
no JDK, Gradle or Rust toolchain is required to export it. APK installation
requires ADB, one explicitly selected authorized device and native approval;
it never silently replaces an installed package. Debug APKs are not
production-signed mobile releases.

Optional source builds require installed Android SDK/JDK or Rust/UEFI tooling.
Dependency downloads are off by default. Offline Android builds require a
complete matching Gradle wrapper cache before any wrapper executes, plus
cached Maven dependencies. A separate checkbox and native approval permit a
networked build. UEFI export never flashes firmware, edits boot variables,
writes a system partition or changes removable media.

Navigator's WSL path provisions Python dependencies inside an explicitly
selected registered distribution, then starts the real service with local
command execution disabled. It requires WSL, python3-venv, iproute2 and the
default WSL relay networking mode; mirrored networking fails explicitly.
Provisioning requires internet. Readiness requires the service health,
in-distro listener PID and Windows WSL-relay ownership checks. The manager
owns shutdown; it never installs a distribution or enables an OS feature.
Actual Android-device, firmware and WSL execution are separate validation
obligations, not established by APK/EFI builds or mocked process tests.

## Experimental own model and portfolio installation

The packaged `PsiCatCore` executable contains the repository's own NumPy
toroidal causal Transformer runtime and needs neither a separately installed
Python interpreter nor Ollama. The build trains a small seed on public portfolio
documentation: a small model with a 64-character context and 500 training steps.
Its receipt records source hashes and training metadata. This is real offline
inference, **not a competent general-purpose assistant**; output may be
fragmentary or meaningless. It is explicitly labeled UNVERIFIED. The toroidal
encoding is an experimental software architecture, not verified physical 5D
information flow.

Use **PsiCat native model** to inspect the checkpoint or request bounded
generation. Unknown vocabulary characters block generation explicitly.
**Train on local text** requires a native file selection and approval, permits
1–2,000 steps, and replaces the user checkpoint only after successful training.
Training runs in a separate bounded native process and is cancellable. Corpora
and checkpoints remain local and unencrypted; private ZIP imports are never
automatically used for training. Training from scratch on selected text does
not promise retention of the seed model's behavior.

The **Portfolio runtime manager** displays all 45 reviewed target contracts.
After approval it can bootstrap user-scoped Windows Python 3.12 with winget,
create separate product environments, install reviewed requirements or
pyproject packages, and run `pip check`. These operations require internet
access and execute third-party installation code. Calculator products use
the checked-in scientific dependency profile. Product 26's POSIX execution
is blocked explicitly. Product 36 installs pinned JAX/jaxlib in its own
environment and verifies actual CPU slider values and both gradients before
accepting installation; managed launches force the CPU backend. GPU/TPU
support is not asserted. Startup health uses a live slider calculation, not
the status page; installed Windows execution still needs its workflow check.
Other non-Python target tooling is not managed.

Products 24 and 27 use the managed Node toolchain. **Install private Node LTS** downloads the
maintained Node 24 Windows x64 archive and checksum manifest from fixed
`nodejs.org` HTTPS endpoints, forbids redirects, verifies SHA-256, and extracts
the licensed runtime into suite user data. Native approval is required.
No administrator rights, global PATH edits or system-wide installation are
requested. Download/extraction failures abort installation; the download has
time/byte bounds. This verifies integrity against the official HTTPS manifest,
not a separately verified release-signing key. An existing Node.js LTS installation
(at least 22.12) with npm can also be used.
**Install dependencies** executes npm's JavaScript
CLI directly (no command-shell shim), installs the checked-in lockfile and
builds the actual Vite dashboard. **Start local service** uses a fixed loopback
host/port and fresh random token; protected API operations are never exposed
without authentication. **Open running dashboard** requires separate native
approval to replace the clipboard with that token. Paste it into the dashboard's
token field; the browser retains it in session storage, and clipboard-reading
applications can see it. The suite does not log or persist the token in
receipts/settings or place it in a URL. Stopping discards the session token.
Project storage is under suite user data, not a system/home default.
After dependencies are installed, local project creation, inspection, preview
and build can operate offline; supplied project source must still be reviewed
before execution.

Product 24 provisions pinned Windows Electron 44.10.2, preserving its full
licensed runtime, and a separate Python environment for its sync/Navigator
sidecars. The suite restores the lock without package scripts, then explicitly
runs the locked Electron installer. **Open browser desktop** launches the real
Electron window directly; inherited IPC confirms UI and sidecar readiness.
Ports 8020 and 8787 must be free: stop a separately managed Navigator first.
No existing service or its authority is silently adopted. Browser-owned
Navigator local command execution remains disabled; saved browser settings may explicitly
disable Navigator startup. Android and extension trees are not installed.
**Close browser desktop** requests correlated graceful cleanup and waits for
process exit. An unresponsive desktop may require terminating its specific
owned Windows process tree; this escalation is reported, not OS confinement.
Browser state lives in suite user data. This is not a verified expert model or
an ongoing browser-update mechanism; native Windows behavior needs its workflow check.

Registered loopback launch contracts cover Products 20, 21, 23 and 28–44,
plus Product 27's Node workbench and Product 24's supervised desktop.
Install dependencies first, then approve the corresponding start action.
The manager rejects occupied ports, requires a responsive health route,
retains bounded startup diagnostics and owns the process until **Stop service**
or desktop shutdown. Quit waits for any active bounded installation to finish
and for owned runtimes to exit; new installations/launches are blocked while
quitting. Changed source/dependency locations require reinstallation.
A selected checkout is used when connected; otherwise the installer supplies
a checksum-receipted tracked-source pack that is copied into a content-scoped
user-data worktree before use. Installation resources are never used as mutable
working storage. The source receipt explicitly inventories excluded binaries,
large files, test/build/dependency folders and symlinks; external datasets,
credentials, Android/UEFI artifacts and all runtime-specific data are not
implied to be bundled. Byte-identical Windows case aliases are deduplicated
and recorded explicitly; conflicting alias contents abort source staging.
Each materialization uses a fresh sibling staging directory and verifies both
the copied files and any reused worktree against the receipt. An interrupted
copy cannot block a retry or be mistaken for a complete checkout; abrupt
process termination can leave an unused `.p45-*` staging directory in suite
user data, which is not reused or automatically reclaimed.
Worktree names use the full receipt SHA-256 without redundantly appending HEAD,
reducing Windows path lengths while retaining the complete content identity.
Early browser failures include bounded, PID-scoped bootstrap records when
available; credentials and raw exception stacks are excluded.
The source pack includes Navigator's five explicit `bot/` Python import
dependencies, without bundling unrelated bot data or private exports.

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

The app makes no automatic network requests on startup. Approved dependency
installation contacts package services; started products may contact their
documented integrations. An explicitly approved optional research step can
contact the fixed local Ollama service described below.
“Open local service” hands a
catalogued `localhost`/`127.0.0.1` address to the system browser; the target
service must already be running. The PsiCat shortcut likewise opens the
documented local Product 20 UI; Product 20 handles its own session handshake
and query policy. Other online capabilities belong to their individual products.

## Windows installable build

The Windows workflow requires a native browser readiness/cleanup check before
building the per-user NSIS installer and its separate verified offline payload. This
fail-fast check runs the real Electron desktop on Windows, not a mocked child.
The installed smoke launch quotes and verifies its isolated user-data path,
including spaces; scratch data stays under the checkout's `build/` directory.
An early desktop exit reports its exit code and signal rather than an empty
startup error. From a Windows checkout with Node.js 22, Python 3.12 and internet
access for dependency/bootstrap downloads:

```powershell
cd 12-AZ-IP/45-axiomzero-pc-suite
npm ci
python -m pip install -r requirements-native-build.txt
npm test
npm run catalog:check
npm run dist:win
npm run smoke:win
```

Artifacts are written to `dist/`. `npm run smoke:win` first requires a clean
installation destination and proves that the **actual installer** rejects
missing and tampered companion parts with a nonzero exit, before silently
installing and uninstalling the per-user NSIS build. It launches the installed
application and verifies that the window renders all 46 products and the
local evidence/runtime/native-model controls, creates a research plan and cancels
it through the preload bridge without renderer exceptions. It also runs
standalone installed native inference and training, verifies the bundled source
checksums, installs a real Product 43 environment, and starts/health-checks/stops
that service. This does not certify every product. The repository workflow
also installs private Node LTS, provisions Product 27, rejects unauthenticated
API requests and creates/builds a real local project through the authenticated API.
It rejects generated-project PostCSS configuration execution during preview and
build, checks actual CPU JAX values/gradients, and requires Product 24's window,
sync/Navigator readiness and graceful process exit. A failed or skipped native
check does not certify those capabilities or permit publishing an installer.
`.github/workflows/pc-suite-windows.yml` builds and uploads them as a workflow
artifact on pull requests and manual dispatch. `SHA256SUMS.txt` covers the
installer, companion manifest, and every model part. A `pc-suite-v*` tag
additionally publishes all these files as a GitHub Release. Builds are currently
**unsigned**; Windows SmartScreen may show a publisher warning. No automatic
update service is included. The configured artifacts target Windows x64;
ARM64 builds and installer upgrades remain unverified. Per-user x64 install,
rendered UI, full installed model inference, and uninstall are required by the
Windows workflow; local source/packaging tests alone do not qualify a Windows
installer.

### Verified offline companion payload

The approved **full** Qwen3-4B-Instruct-2507 Q4_K_M GGUF is not reduced or
replaced. Its approximately 2.497 GB file exceeded NSIS's embedded archive mmap
limit. The installer now bundles everything else (including the engine,
runtime manifest, native seed and portfolio), while the model ships as
contiguous **at most 1 GiB** parts. No release asset may reach 2 GiB, respecting
GitHub's per-asset limit as well as NSIS's embedded archive limit.

For version `0.1.0`, place these files together in the **same local folder**:

- `AxiomZero-PC-Suite-0.1.0-x64.exe`
- `AxiomZero-PC-Suite-0.1.0-offline.json`
- `AxiomZero-PC-Suite-0.1.0-model.part001`, `.part002`, and `.part003`
- `SHA256SUMS.txt` (for independent distribution-integrity checking)

Use the installer from that folder, including for silent `/S` installation.
Do not put parts in the installation directory or rename them. Transfer all
assets via an offline medium if desired; **installation requires no network
or model download**. Allow disk space for both the companion parts and the
assembled approximately 2.497 GB model in the installation, plus other bundled
resources. The portable target is deliberately removed: a self-extracting
portable executable would embed the same oversized model again.

Supported electron-builder `customInit` and `customInstall` NSIS hooks invoke
a bundled static PowerShell script as the per-user installer user. It checks
the installer-bound manifest digest, its exact canonical part names and sizes,
every part's SHA-256, and the assembled model's SHA-256 against the bundled
runtime manifest. The first pass happens **before** old-install removal; the
second pass writes to an exclusive new partial file and atomically renames
only after all hashes match. Reparse points, network paths, and overwriting an
existing model are rejected. Failure stops the installer with a nonzero exit;
there is no successful fallback, automatic launch, or external downloader.
If an error occurs after application extraction, that incomplete installation
is not qualified; correct the local payload and rerun the installer.

electron-builder's installed NSIS-web template can discover sibling archives,
but a missing or incorrect archive falls back to a network download. This
package intentionally uses regular NSIS and the fail-closed local hook instead.
`npm run payload:stage` generates the parts and compile-time manifest seal;
`npm run payload:verify` checks the whole release set and writes checksums.
`dist:win` restores the full model in `dist/win-unpacked` **after** installer
archive creation for real unpacked diagnostics. Release smoke instead verifies
and runs the full model installed by the actual local-payload installer.

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
arbitrary shell commands, access browser passwords, or elevate privileges.
Approved runtime installation and launch execute fixed product/package programs
with the user's permissions; these processes are **not OS-sandboxed**.

The selected checkout path and its availability are stored in the user's
application settings. Protect the Windows account and the selected checkout
as usual. Product 45 does not provide repository authentication, encrypted
sync, continuous service health monitoring, or a full backup/restore facility.

## Validation

```powershell
npm test
npm run catalog:check
```

These checks cover catalog integrity, repository-path containment, settings,
ZIP safety, local indexing, evidence citations, index persistence, harness
approvals/state recovery/budgets/cancellation/audit seals, worker execution
and the local reasoning transport, plus source-worktree receipt/retry behavior
and the Windows smoke argument contract. The latter is a source-level check on
non-Windows hosts; it does not replace running the installed smoke on
Windows. The Windows workflow requires fail-closed companion payload tests and
per-user installation/UI/uninstall. Installer upgrades and a
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
must still be evaluated before production use. Only the small experimental
own-model seed described above is bundled; no deployment-quality general
assistant weights are supplied. Product 43's causal character-level workflow
is experimental, not a production assistant.

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
loops. Ordinary execution has a **60-second deadline**; explicitly approved
embedded CPU reasoning has an **eighteen-minute deadline**, including startup
and a shared fifteen-minute inference budget. Evidence search runs
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
bounded control plane does not install or orchestrate all 45 desktop-managed
product runtimes. Product 46 is a native Android app; install it through Android
Studio or Android's user-controlled package installer.
Its task/results/audit exports are plaintext local data, not encrypted memory
or an automatic cross-product profile export.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
