import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createWorkbenchHttpServer } from '../server.js';
import { ViteWorkbench } from '../workbench.js';

test('HTTP surface requires the token, blocks foreign origins, and serves the dashboard', async (t) => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'psicat-vite-http-'));
  const token = 'workbench-test-token-0123456789abcdef';
  const workbench = new ViteWorkbench({ workspaceRoot: root });
  await workbench.initialize();
  const server = createWorkbenchHttpServer({ workbench, token, port: 0 });
  server.listen(0, '127.0.0.1');
  await new Promise((resolve) => server.once('listening', resolve));
  const address = server.address();
  const baseUrl = `http://127.0.0.1:${address.port}`;
  const headers = { Authorization: 'Bearer ' + token };
  t.after(async () => {
    await workbench.close();
    await new Promise((resolve) => server.close(resolve));
    await fs.rm(root, { recursive: true, force: true });
  });

  const unauthorized = await fetch(`${baseUrl}/api/status`);
  assert.equal(unauthorized.status, 401);
  const forbiddenOrigin = await fetch(`${baseUrl}/api/status`, {
    headers: { ...headers, Origin: 'https://attacker.example' },
  });
  assert.equal(forbiddenOrigin.status, 403);

  const statusResponse = await fetch(`${baseUrl}/api/status`, { headers });
  assert.equal(statusResponse.status, 200);
  assert.equal((await statusResponse.json()).product, 'PsiCat Vite Web Workbench');
  const dashboard = await fetch(baseUrl);
  assert.equal(dashboard.status, 200);
  assert.match(dashboard.headers.get('content-security-policy'), /frame-ancestors 'none'/);
  const html = await dashboard.text();
  assert.match(html, /PsiCat.*Workbench/);
  const scriptPath = html.match(/src="([^"]+\.js)"/)?.[1];
  assert.ok(scriptPath);
  const dashboardScript = await fetch(new URL(scriptPath, baseUrl));
  assert.equal(dashboardScript.status, 200);

  const created = await fetch(`${baseUrl}/api/action`, {
    method: 'POST',
    headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'create', name: 'api-project' }),
  });
  assert.equal(created.status, 200);
  assert.equal((await created.json()).project.name, 'api-project');
});
