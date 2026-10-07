// SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
// Copyright (C) 2026  ThomasCory Walker-Pearson

import fs from 'node:fs/promises';
import path from 'node:path';
import net from 'node:net';
import { build, createServer, version as viteVersion } from 'vite';

const PROJECT_NAME = /^[a-z0-9](?:[a-z0-9-]{0,38}[a-z0-9])?$/;
const MAX_PROJECTS = 30;
const MAX_SOURCE_BYTES = 25 * 1024 * 1024;
const IGNORED_DIRS = new Set(['.git', 'node_modules', 'dist']);
const TEMPLATES = Object.freeze({
  'vanilla-js': {
    label: 'Vanilla JavaScript',
    files: {
      'index.html': `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#10151d">
    <title>PsiCat Vite Project</title>
  </head>
  <body>
    <main>
      <p class="eyebrow">PsiCat Vite Web Workbench</p>
      <h1>Your project is ready.</h1>
      <p>Edit <code>src/main.js</code>, then use the Workbench to preview or build.</p>
      <button id="counter" type="button">Count: 0</button>
    </main>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
`,
      'src/main.js': `import './style.css';

let count = 0;
const button = document.querySelector('#counter');
button.addEventListener('click', () => {
  count += 1;
  button.textContent = \`Count: \${count}\`;
});
`,
      'src/style.css': `:root { color-scheme: dark; font-family: system-ui, sans-serif; background: #10151d; color: #e8edf5; }
body { min-height: 100vh; margin: 0; display: grid; place-items: center; }
main { width: min(42rem, calc(100% - 3rem)); }
.eyebrow { color: #a78bfa; font-size: .8rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
h1 { font-size: clamp(2.4rem, 8vw, 5rem); margin: .3rem 0 1rem; }
button { margin-top: 1.5rem; padding: .75rem 1rem; border: 0; border-radius: .5rem; background: #a78bfa; color: #171322; font: inherit; font-weight: 700; cursor: pointer; }
`,
    },
  },
  'vanilla-ts': {
    label: 'Vanilla TypeScript',
    files: {
      'index.html': `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PsiCat Vite TypeScript Project</title>
  </head>
  <body>
    <main>
      <p class="eyebrow">PsiCat Vite Web Workbench</p>
      <h1>TypeScript project ready.</h1>
      <p>Edit <code>src/main.ts</code>, then preview or build it here.</p>
      <output id="result"></output>
    </main>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
`,
      'src/main.ts': `import './style.css';

const result = document.querySelector<HTMLOutputElement>('#result');
if (result) result.value = 'Vite transpiles TypeScript; run a separate type-checker for type validation.';
`,
      'src/style.css': `:root { color-scheme: dark; font-family: system-ui, sans-serif; background: #10151d; color: #e8edf5; }
body { min-height: 100vh; margin: 0; display: grid; place-items: center; }
main { width: min(42rem, calc(100% - 3rem)); }
.eyebrow { color: #a78bfa; font-size: .8rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
h1 { font-size: clamp(2.4rem, 8vw, 5rem); margin: .3rem 0 1rem; }
output { display: block; margin-top: 1.5rem; color: #38bdf8; }
`,
    },
  },
});

function safeProjectName(value) {
  const name = String(value || '').trim().toLowerCase();
  if (!PROJECT_NAME.test(name)) {
    throw new Error('Project names must be 1–40 lowercase letters, numbers, or hyphens; begin and end with a letter or number.');
  }
  return name;
}

async function directorySize(root) {
  let total = 0;
  async function visit(folder) {
    for (const entry of await fs.readdir(folder, { withFileTypes: true })) {
      if (entry.isSymbolicLink()) throw new Error('Symbolic links are not supported in workbench projects.');
      const target = path.join(folder, entry.name);
      if (entry.isDirectory()) {
        if (!IGNORED_DIRS.has(entry.name)) await visit(target);
      } else if (entry.isFile()) {
        total += (await fs.stat(target)).size;
        if (total > MAX_SOURCE_BYTES) throw new Error('Project source exceeds the 25 MiB workbench limit.');
      }
    }
  }
  await visit(root);
  return total;
}

async function findAvailablePort() {
  const socket = net.createServer();
  await new Promise((resolve, reject) => {
    socket.once('error', reject);
    socket.listen(0, '127.0.0.1', resolve);
  });
  const { port } = socket.address();
  await new Promise((resolve, reject) => socket.close((error) => error ? reject(error) : resolve()));
  return port;
}

export class ViteWorkbench {
  constructor({ workspaceRoot = process.env.PSICAT_VITE_WORKBENCH_HOME || path.join(process.env.HOME || process.cwd(), '.local', 'share', 'psicat-vite-workbench') } = {}) {
    this.workspaceRoot = path.resolve(workspaceRoot);
    this.projectsRoot = path.join(this.workspaceRoot, 'projects');
    this.previews = new Map();
    this.lastBuilds = new Map();
  }

  async initialize() {
    await fs.mkdir(this.projectsRoot, { recursive: true, mode: 0o700 });
    return this.status();
  }

  async status() {
    let nodeVersion = process.version;
    return {
      ok: true,
      product: 'PsiCat Vite Web Workbench',
      vite_version: viteVersion,
      node_version: nodeVersion,
      workspace_root: this.workspaceRoot,
      templates: Object.entries(TEMPLATES).map(([id, item]) => ({ id, label: item.label })),
      running_previews: [...this.previews.entries()].map(([project, preview]) => ({
        project,
        url: preview.url,
        started_at: preview.startedAt,
      })),
      policy: {
        bind_host: '127.0.0.1',
        project_limit: MAX_PROJECTS,
        source_limit_bytes: MAX_SOURCE_BYTES,
        arbitrary_commands: false,
        project_vite_configs_loaded: false,
        plugins_loaded: false,
        package_installation: false,
        operating_system_sandbox: false,
      },
    };
  }

  async listProjects() {
    await fs.mkdir(this.projectsRoot, { recursive: true, mode: 0o700 });
    const projects = [];
    for (const entry of await fs.readdir(this.projectsRoot, { withFileTypes: true })) {
      if (!entry.isDirectory() || entry.isSymbolicLink() || !PROJECT_NAME.test(entry.name)) continue;
      const project = await this.inspectProject(entry.name);
      projects.push(project);
    }
    return { ok: true, projects };
  }

  async createProject({ name, template = 'vanilla-js' } = {}) {
    const projectName = safeProjectName(name);
    const templateDefinition = TEMPLATES[template];
    if (!templateDefinition) throw new Error(`Unsupported template. Choose one of: ${Object.keys(TEMPLATES).join(', ')}.`);
    const current = await this.listProjects();
    if (current.projects.length >= MAX_PROJECTS) throw new Error(`The workbench supports at most ${MAX_PROJECTS} projects.`);
    const projectRoot = path.join(this.projectsRoot, projectName);
    await fs.mkdir(this.projectsRoot, { recursive: true, mode: 0o700 });
    try {
      await fs.mkdir(projectRoot, { mode: 0o700 });
    } catch (error) {
      if (error.code === 'EEXIST') throw new Error(`Project "${projectName}" already exists.`);
      throw error;
    }
    try {
      for (const [relativePath, content] of Object.entries(templateDefinition.files)) {
        const target = path.join(projectRoot, relativePath);
        await fs.mkdir(path.dirname(target), { recursive: true, mode: 0o700 });
        await fs.writeFile(target, content, { flag: 'wx', mode: 0o600 });
      }
      const packageData = {
        name: projectName,
        private: true,
        version: '0.0.0',
        type: 'module',
        workbench: { template, vite: viteVersion },
      };
      await fs.writeFile(path.join(projectRoot, 'package.json'), `${JSON.stringify(packageData, null, 2)}\n`, { flag: 'wx', mode: 0o600 });
    } catch (error) {
      await fs.rm(projectRoot, { recursive: true, force: true });
      throw error;
    }
    return { ok: true, project: await this.inspectProject(projectName) };
  }

  async _projectRoot(name) {
    const projectName = safeProjectName(name);
    const projectRoot = path.join(this.projectsRoot, projectName);
    const stat = await fs.lstat(projectRoot).catch(() => null);
    if (!stat?.isDirectory() || stat.isSymbolicLink()) throw new Error(`Project "${projectName}" does not exist in this workbench.`);
    const realRoot = await fs.realpath(projectRoot);
    if (realRoot !== projectRoot) throw new Error('Project path must not resolve through a symbolic link.');
    await directorySize(projectRoot);
    return { projectName, projectRoot };
  }

  async inspectProject(name) {
    const { projectName, projectRoot } = await this._projectRoot(name);
    let packageJson = {};
    try {
      packageJson = JSON.parse(await fs.readFile(path.join(projectRoot, 'package.json'), 'utf8'));
    } catch (error) {
      if (error.code !== 'ENOENT') throw new Error('Project package.json is invalid JSON.');
    }
    const files = [];
    async function visit(folder, prefix = '') {
      for (const entry of await fs.readdir(folder, { withFileTypes: true })) {
        if (entry.isSymbolicLink()) throw new Error('Symbolic links are not supported in workbench projects.');
        if (IGNORED_DIRS.has(entry.name)) continue;
        const relativePath = prefix ? `${prefix}/${entry.name}` : entry.name;
        if (entry.isDirectory()) await visit(path.join(folder, entry.name), relativePath);
        else if (entry.isFile() && files.length < 100) files.push(relativePath);
      }
    }
    await visit(projectRoot);
    return {
      name: projectName,
      template: String(packageJson.workbench?.template || 'custom'),
      files: files.sort(),
      preview: this.previews.get(projectName)?.url || null,
      last_build: this.lastBuilds.get(projectName) || null,
      ignored_project_vite_config: files.some((file) => /^vite\.config\./.test(file)),
    };
  }

  async startPreview(name) {
    const { projectName, projectRoot } = await this._projectRoot(name);
    const existing = this.previews.get(projectName);
    if (existing) return { ok: true, project: projectName, url: existing.url, already_running: true };
    const port = await findAvailablePort();
    const server = await createServer({
      configFile: false,
      root: projectRoot,
      appType: 'spa',
      clearScreen: false,
      envPrefix: 'PSICAT_PROJECT_',
      plugins: [],
      server: {
        host: '127.0.0.1',
        port,
        strictPort: true,
        open: false,
        cors: false,
        hmr: { host: '127.0.0.1' },
        fs: { strict: true, allow: [projectRoot], deny: ['.env', '.env.*', '*.pem', '*.key'] },
      },
    });
    try {
      await server.listen();
      const address = server.httpServer.address();
      if (!address || typeof address === 'string') throw new Error('Vite preview did not bind a TCP port.');
      const preview = {
        server,
        url: `http://127.0.0.1:${address.port}/`,
        startedAt: new Date().toISOString(),
      };
      this.previews.set(projectName, preview);
      return { ok: true, project: projectName, url: preview.url, already_running: false };
    } catch (error) {
      await server.close();
      throw error;
    }
  }

  async stopPreview(name) {
    const projectName = safeProjectName(name);
    const preview = this.previews.get(projectName);
    if (!preview) return { ok: true, project: projectName, stopped: false };
    await preview.server.close();
    this.previews.delete(projectName);
    return { ok: true, project: projectName, stopped: true };
  }

  async buildProject(name) {
    const { projectName, projectRoot } = await this._projectRoot(name);
    const outputDirectory = path.join(projectRoot, 'dist');
    const outputStat = await fs.lstat(outputDirectory).catch(() => null);
    if (outputStat?.isSymbolicLink()) throw new Error('The dist output path must not be a symbolic link.');
    const result = await build({
      configFile: false,
      root: projectRoot,
      appType: 'spa',
      clearScreen: false,
      envPrefix: 'PSICAT_PROJECT_',
      plugins: [],
      base: './',
      build: {
        outDir: outputDirectory,
        emptyOutDir: true,
        sourcemap: false,
        reportCompressedSize: false,
      },
    });
    const outputs = (Array.isArray(result) ? result : [result]).flatMap((item) => item.output || []);
    const files = outputs.map((item) => ({
      file: item.fileName,
      bytes: item.type === 'asset' ? Buffer.byteLength(item.source) : item.code.length,
    }));
    const receipt = {
      built_at: new Date().toISOString(),
      files,
      total_bytes: files.reduce((sum, item) => sum + item.bytes, 0),
    };
    this.lastBuilds.set(projectName, receipt);
    return { ok: true, project: projectName, build: receipt };
  }

  async performAction(payload = {}) {
    const action = String(payload.action || '');
    switch (action) {
      case 'status':
        return this.status();
      case 'list':
        return this.listProjects();
      case 'create':
        return this.createProject(payload);
      case 'inspect':
        return { ok: true, project: await this.inspectProject(payload.name) };
      case 'preview_start':
        return this.startPreview(payload.name);
      case 'preview_stop':
        return this.stopPreview(payload.name);
      case 'build':
        return this.buildProject(payload.name);
      default:
        throw new Error('Unsupported workbench action.');
    }
  }

  async close() {
    await Promise.all([...this.previews.keys()].map((name) => this.stopPreview(name)));
  }
}
