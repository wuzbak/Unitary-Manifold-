import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { ViteWorkbench } from '../workbench.js';

async function temporaryWorkbench(t, options = {}) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'psicat-vite-workbench-'));
  const workbench = new ViteWorkbench({ workspaceRoot: root, ...options });
  await workbench.initialize();
  t.after(async () => {
    await workbench.close();
    await fs.rm(root, { recursive: true, force: true });
  });
  return { root, workbench };
}

test('scaffolds and inspects only curated templates', async (t) => {
  const { workbench } = await temporaryWorkbench(t);
  const created = await workbench.createProject({ name: 'sample-app', template: 'vanilla-js' });
  assert.equal(created.project.name, 'sample-app');
  assert.equal(created.project.template, 'vanilla-js');
  assert.deepEqual(created.project.files, ['index.html', 'package.json', 'src/main.js', 'src/style.css']);
  await assert.rejects(workbench.createProject({ name: '../escape' }), /Project names/);
  await assert.rejects(workbench.createProject({ name: 'bad', template: 'arbitrary-plugin' }), /Unsupported template/);
  await assert.rejects(workbench.createProject({ name: 'sample-app' }), /already exists/);
});

test('starts an isolated loopback preview and stops it cleanly', async (t) => {
  const { workbench } = await temporaryWorkbench(t);
  await workbench.createProject({ name: 'preview-app', template: 'vanilla-ts' });
  const started = await workbench.startPreview('preview-app');
  assert.match(started.url, /^http:\/\/127\.0\.0\.1:\d+\/$/);
  assert.equal((await fetch(started.url)).status, 200);
  assert.equal((await workbench.startPreview('preview-app')).already_running, true);
  assert.equal((await workbench.stopPreview('preview-app')).stopped, true);
  await assert.rejects(fetch(started.url));
  assert.equal((await workbench.stopPreview('preview-app')).stopped, false);
});

test('builds production assets without loading project Vite config or plugins', async (t) => {
  const { root, workbench } = await temporaryWorkbench(t);
  await workbench.createProject({ name: 'build-app' });
  const projectRoot = path.join(root, 'projects', 'build-app');
  const markerPath = path.join(root, 'project-config-executed');
  await fs.writeFile(
    path.join(projectRoot, 'vite.config.mjs'),
    `import { writeFileSync } from 'node:fs'; writeFileSync(${JSON.stringify(markerPath)}, 'executed'); export default {};`,
  );
  const inspection = await workbench.inspectProject('build-app');
  assert.equal(inspection.ignored_project_vite_config, true);
  const result = await workbench.buildProject('build-app');
  assert.ok(result.build.total_bytes > 0);
  assert.ok(result.build.files.some((file) => file.file === 'index.html'));
  assert.equal(await fs.stat(markerPath).catch(() => null), null);
  assert.ok((await fs.stat(path.join(projectRoot, 'dist', 'index.html'))).isFile());
});

test('rejects a symlinked build output before writing outside the workspace', async (t) => {
  const { root, workbench } = await temporaryWorkbench(t);
  await workbench.createProject({ name: 'linked-output' });
  const external = await fs.mkdtemp(path.join(os.tmpdir(), 'psicat-vite-external-'));
  t.after(() => fs.rm(external, { recursive: true, force: true }));
  await fs.writeFile(path.join(external, 'keep.txt'), 'keep');
  await fs.symlink(external, path.join(root, 'projects', 'linked-output', 'dist'));
  await assert.rejects(workbench.buildProject('linked-output'), /Symbolic links/);
  assert.equal(await fs.readFile(path.join(external, 'keep.txt'), 'utf8'), 'keep');
});

test('rejects symlinks added to project sources', async (t) => {
  const { root, workbench } = await temporaryWorkbench(t);
  await workbench.createProject({ name: 'linked-source' });
  const projectRoot = path.join(root, 'projects', 'linked-source');
  await fs.symlink(path.join(projectRoot, 'index.html'), path.join(projectRoot, 'outside-link'));
  await assert.rejects(workbench.inspectProject('linked-source'), /Symbolic links/);
});
