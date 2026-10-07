// SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
// Copyright (C) 2026  ThomasCory Walker-Pearson

import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { ViteWorkbench } from './workbench.js';

const PRODUCT_ROOT = path.dirname(fileURLToPath(import.meta.url));
const UI_ROOT = path.join(PRODUCT_ROOT, 'dist');
const HOST = process.env.PSICAT_VITE_WORKBENCH_HOST || '127.0.0.1';
const PORT = Number.parseInt(process.env.PSICAT_VITE_WORKBENCH_PORT || '8327', 10);
const TOKEN = String(process.env.PSICAT_VITE_WORKBENCH_TOKEN || '');
const MAX_BODY_BYTES = 16 * 1024;
const MIME_TYPES = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.ico': 'image/x-icon',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
};

function authorized(request, token) {
  const authorization = String(request.headers.authorization || '');
  const match = authorization.startsWith('Bearer ') ? authorization.slice(7) : '';
  if (!token || !match) return false;
  const provided = Buffer.from(match);
  const expected = Buffer.from(token);
  return provided.length === expected.length && crypto.timingSafeEqual(provided, expected);
}

function sendJson(response, status, payload) {
  const body = Buffer.from(JSON.stringify(payload));
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': body.length,
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
  });
  response.end(body);
}

async function readJson(request) {
  const chunks = [];
  let length = 0;
  for await (const chunk of request) {
    length += chunk.length;
    if (length > MAX_BODY_BYTES) throw new Error('Request body exceeds the 16 KiB limit.');
    chunks.push(chunk);
  }
  const text = Buffer.concat(chunks).toString('utf8');
  const data = text ? JSON.parse(text) : {};
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Request body must be a JSON object.');
  return data;
}

function allowedOrigin(request, port) {
  const origin = String(request.headers.origin || '');
  if (!origin) return true;
  try {
    const parsed = new URL(origin);
    const allowedPorts = new Set([String(port), '5179']);
    return ['127.0.0.1', 'localhost'].includes(parsed.hostname) && allowedPorts.has(parsed.port);
  } catch {
    return false;
  }
}

export function createWorkbenchHttpServer({ workbench = new ViteWorkbench(), token = TOKEN, host = HOST, port = PORT } = {}) {
  const server = http.createServer(async (request, response) => {
    let requestUrl;
    try {
      requestUrl = new URL(request.url || '/', `http://${request.headers.host || `${host}:${port}`}`);
    } catch {
      return sendJson(response, 400, { ok: false, error: 'Invalid request URL.' });
    }
    if (requestUrl.pathname === '/health' && request.method === 'GET') {
      return sendJson(response, 200, { ok: true, service: 'psicat-vite-web-workbench' });
    }
    if (!allowedOrigin(request, port)) return sendJson(response, 403, { ok: false, error: 'Cross-origin requests are not allowed.' });
    if (!requestUrl.pathname.startsWith('/api/')) {
      if (request.method !== 'GET') return sendJson(response, 404, { ok: false, error: 'Not found.' });
      let requestedPath;
      try {
        requestedPath = requestUrl.pathname === '/' ? '/index.html' : decodeURIComponent(requestUrl.pathname);
      } catch {
        return sendJson(response, 400, { ok: false, error: 'Invalid asset path.' });
      }
      const filePath = path.resolve(UI_ROOT, `.${requestedPath}`);
      if (!filePath.startsWith(`${UI_ROOT}${path.sep}`)) return sendJson(response, 404, { ok: false, error: 'Not found.' });
      try {
        const body = await fs.readFile(filePath);
        response.writeHead(200, {
          'Content-Type': MIME_TYPES[path.extname(filePath)] || 'application/octet-stream',
          'Content-Length': body.length,
          'X-Content-Type-Options': 'nosniff',
          'Content-Security-Policy': "default-src 'self'; connect-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'",
        });
        return response.end(body);
      } catch {
        return sendJson(response, 404, { ok: false, error: 'Workbench UI has not been built. Run npm run build.' });
      }
    }
    if (!authorized(request, token)) return sendJson(response, 401, { ok: false, error: 'A valid workbench bearer token is required.' });
    if (requestUrl.pathname === '/api/status' && request.method === 'GET') {
      try {
        return sendJson(response, 200, await workbench.performAction({ action: 'status' }));
      } catch {
        return sendJson(response, 500, { ok: false, error: 'Unable to read workbench status.' });
      }
    }
    if (requestUrl.pathname === '/api/projects' && request.method === 'GET') {
      try {
        return sendJson(response, 200, await workbench.performAction({ action: 'list' }));
      } catch {
        return sendJson(response, 500, { ok: false, error: 'Unable to list workbench projects.' });
      }
    }
    if (requestUrl.pathname === '/api/action' && request.method === 'POST') {
      try {
        return sendJson(response, 200, await workbench.performAction(await readJson(request)));
      } catch (error) {
        return sendJson(response, 400, { ok: false, error: String(error.message || 'Workbench operation failed.') });
      }
    }
    return sendJson(response, 404, { ok: false, error: 'Not found.' });
  });
  return server;
}

async function main() {
  if (!TOKEN || TOKEN.length < 32) {
    throw new Error('Set PSICAT_VITE_WORKBENCH_TOKEN to a random secret of at least 32 characters before starting.');
  }
  if (HOST !== '127.0.0.1' && HOST !== 'localhost') {
    throw new Error('The workbench only supports loopback binding (127.0.0.1 or localhost).');
  }
  const workbench = new ViteWorkbench();
  await workbench.initialize();
  const server = createWorkbenchHttpServer({ workbench, token: TOKEN });
  server.listen(PORT, HOST, () => {
    console.log(`PsiCat Vite Web Workbench listening at http://${HOST}:${PORT}`);
    console.log(`Project workspace: ${workbench.projectsRoot}`);
  });
  const shutdown = async () => {
    await workbench.close();
    server.close(() => process.exit(0));
  };
  process.once('SIGINT', shutdown);
  process.once('SIGTERM', shutdown);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
