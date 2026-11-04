# Product 45 — AxiomZero PC Suite

**Version 0.1.0 · Windows desktop portfolio launcher and local evidence search · readiness not assessed**

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

The app makes no automatic network requests. “Open local service” hands a
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
local evidence controls without renderer exceptions. The repository workflow
`.github/workflows/pc-suite-windows.yml` builds and uploads them as a workflow
artifact on pull requests and manual dispatch. Each executable is accompanied
by a SHA-256 checksum. A `pc-suite-v*` tag additionally publishes the installer
and portable executable as a GitHub Release. Builds are currently
**unsigned**; Windows SmartScreen may show a publisher warning. No automatic
update service is included. The configured artifacts target Windows x64;
ARM64 builds and an actual Windows install/upgrade/uninstall smoke test remain
unverified.

To run from source:

```powershell
npm run start
```

`npm run catalog` regenerates the embedded offline catalog after the master
registry table changes. `npm run catalog:check` fails when the checked-in
catalog is stale.

## Trust and operational boundary

The renderer has no Node.js access and uses a context-isolated, sandboxed
preload bridge. The bridge exposes only fixed catalog, folder-picker and
portfolio actions; it accepts product IDs and fixed category names rather
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
ZIP safety, local indexing, evidence citations, and index persistence. A
Windows install/upgrade/uninstall smoke test and publisher code-signing
certificate remain release work; a successful packaging job is not a claim
that every portfolio product is installed or Windows-compatible.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
