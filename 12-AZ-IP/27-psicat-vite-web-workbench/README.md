# PsiCat's Vite Web Workbench
## Product 27 — standalone frontend project workbench for PsiCat

PsiCat's Vite Web Workbench is a local application for creating and operating small frontend projects with [Vite](https://vite.dev/). PsiCat can discover and call its typed workbench tools; Product 24 can open the dashboard as a local browser page. Vite remains the frontend dev server and production builder—it is not a browser engine, web crawler, model, or operating-system sandbox.

## What it does

- Scaffolds Vanilla JavaScript and TypeScript projects from reviewed templates.
- Inspects bounded project file lists and reports project Vite config files as ignored.
- Starts and stops one Vite dev preview per project, bound to `127.0.0.1`.
- Builds static output and returns a machine-readable file/size receipt.
- Provides a standalone dashboard and HTTP API, protected by a local bearer token.
- Exposes the same actions as native Product 20 PsiCat tools with explicit human approval for file creation, server start/stop, and builds.

Projects are stored outside the repository by default in `~/.local/share/psicat-vite-workbench/projects/`. No project dependency installation is currently provided. Templates use Vite bundled with this product. A Vite build strips TypeScript syntax; it does not type-check it.

## Run the app

Requirements: Node.js `^20.19.0 || >=22.12.0`, npm, and the pinned Vite dependency. Vite 8.3.3 is MIT-licensed.

```bash
cd /home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/27-psicat-vite-web-workbench
npm install
npm run build
export PSICAT_VITE_WORKBENCH_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
npm start
```

Open `http://127.0.0.1:8327/` in a browser and paste the token from the same shell environment. Keep the token in a local secret manager or environment; do not commit it, put it into a `VITE_*` value, or bundle it into a frontend. The listener refuses non-loopback binding. The token is required and must contain at least 32 characters.

## Connect PsiCat

Set the same variables in the environment that launches Product 20:

```bash
export PSICAT_VITE_WORKBENCH_URL=http://127.0.0.1:8327
export PSICAT_VITE_WORKBENCH_TOKEN='<same local token>'
```

Restart Product 20, then discover the native tools with `GET /api/agentToolkit?view=full`. Available tools:

- `getPsiCatViteWorkbenchStatus`
- `listPsiCatViteProjects`
- `inspectPsiCatViteProject`
- `createPsiCatViteProject`
- `startPsiCatVitePreview`
- `stopPsiCatVitePreview`
- `buildPsiCatViteProject`

Write operations require `human_gate_approved: true`; this is a policy acknowledgment, not proof of a separate identity or cryptographic authorization. Product 20 only calls a loopback URL, does not accept the token as a tool argument, and returns no token in status or receipts.

Product 24 can use the Workbench through its normal address bar: open `http://127.0.0.1:8327/`. Preview projects are separate loopback origins and should be treated as trusted local code.

## Operating boundary

- Workbench API and previews bind only to loopback. The UI/API accepts only same-origin requests from loopback hostnames; mutating routes require the token.
- The server loads no project `vite.config.*`, plugins, project package scripts, or package managers. Only static reviewed templates are scaffolded.
- It does not execute arbitrary shell commands or install arbitrary dependencies. Project creation, preview, and build are explicit actions.
- It is **not an OS sandbox**. Vite transforms project source and the preview executes that source in a browser. Use only projects you trust; do not expose this local service to a network.
- Workspace project names are constrained, symbolic links are rejected, source is limited to 25 MiB, and the project count is capped at 30.
- Vite preview should not be treated as a production server; use the static build output in an appropriately reviewed hosting environment.

## Development and tests

```bash
npm test
npm run build
```

`npm run dev` starts Vite's dashboard dev server (port 5179) and expects the API server on `127.0.0.1:8327`.

## Current scope

This is a usable first product, not a full IDE or isolated code-execution service. It does not yet provide arbitrary package management, arbitrary plugin selection, source editing, multi-user auth, network-exposed deployment, or a cloud service. Those capabilities require separate threat modeling and approval rather than widening the runner by default.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
