// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026  ThomasCory Walker-Pearson
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { createOllamaModels, MAX_BYTES, MAX_MODELS, TIMEOUT_MS } = require("../lib/ollama-models.cjs");

const model = { name: "operator-27b:iq3", size: 13500000000, digest: "a".repeat(64) };
const local = { details: { format: "gguf" }, model_info: { "general.architecture": "user-installed" },
  capabilities: ["completion"] };

async function provider(t, handler, timeoutMs = 1000) {
  const server = http.createServer(handler);
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(() => {
    server.closeAllConnections();
    return new Promise((resolve) => server.close(resolve));
  });
  const calls = [];
  const client = createOllamaModels({ timeoutMs, request: (options, callback) => {
    calls.push(options);
    return http.request({ ...options, port: server.address().port }, callback);
  } });
  return { client, calls };
}

test("discovery is explicit, bounded IPv4 loopback only, and preserves engine-reported bytes/digest", async (t) => {
  const { client, calls } = await provider(t, (req, res) => {
    assert.equal(req.method, "GET");
    assert.equal(req.url, "/api/tags");
    res.end(JSON.stringify({ models: [model] }));
  });
  assert.equal(calls.length, 0);
  const result = await client.list();
  assert.deepEqual(result.models, [{ name: model.name, sizeBytes: model.size, digest: model.digest }]);
  assert.match(result.boundary, /not artifact provenance/);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].hostname, "127.0.0.1");
  assert.equal(calls[0].family, 4);
  assert.equal(calls[0].port, 11434);
  assert.equal(calls[0].agent, false);
  assert.equal(calls[0].protocol, "http:");
  assert.equal(TIMEOUT_MS, 10000);
});

test("cloud, malformed, unsafe, reserved and duplicate entries are omitted, not selectable", async (t) => {
  const invalid = [
    { ...model, name: "qwen:cloud" }, { ...model, remote_host: "example.invalid" },
    { ...model, remote_model: "remote" }, { ...model, name: "psicat:embedded" },
    { ...model, name: "<script>alert(1)</script>" }, { ...model, name: "unsafe\n" },
    { ...model, name: "a".repeat(81) }, { ...model, size: 0 },
    { ...model, size: -1 }, { ...model, size: 1.5 }, { ...model, size: Number.MAX_SAFE_INTEGER + 1 },
    { ...model, digest: "not a digest" }, null
  ];
  const { client } = await provider(t, (_req, res) => res.end(JSON.stringify({ models: [model, model, ...invalid] })));
  const result = await client.list();
  assert.equal(result.models.length, 1);
  assert.equal(result.omitted, invalid.length + 1);
});

test("runtime inspection sends only exact model name, rejects remote identity before inference", async (t) => {
  const { client, calls } = await provider(t, (req, res) => {
    assert.equal(req.url, "/api/show");
    assert.equal(req.method, "POST");
    let bytes = "";
    req.on("data", (chunk) => { bytes += chunk; });
    req.on("end", () => {
      assert.deepEqual(JSON.parse(bytes), { model: model.name, verbose: false });
      res.end(JSON.stringify(local));
    });
  });
  assert.deepEqual(await client.inspect(model.name), { status: "UNVERIFIED", model: model.name });
  assert.equal(calls.length, 1);
  for (const name of ["qwen:cloud", "", "-bad", "a b", "a\n", "psicat:embedded", null]) {
    await assert.rejects(client.inspect(name), /local Ollama/);
  }
  assert.equal(calls.length, 1);
});

test("runtime does not claim architecture/IQ3 compatibility from a tag; remote and explicit non-completion metadata fail", async (t) => {
  for (const metadata of [
    { ...local, remote_host: "example.invalid" }, { ...local, remote_model: "remote" },
    {}, { ...local, capabilities: ["embedding"] }, { ...local, capabilities: null },
    { details: [] }
  ]) {
    await t.test(JSON.stringify(metadata), async (t) => {
      const { client, calls } = await provider(t, (_req, res) => res.end(JSON.stringify(metadata)));
      await assert.rejects(client.inspect(model.name), /not permitted|completion runtime/);
      assert.equal(calls.length, 1);
    });
  }
});

test("ordinary completion and legacy Ollama models are not broken by absent optional GGUF metadata", async (t) => {
  for (const metadata of [
    { capabilities: ["completion"] },
    { ...local, details: { format: "safetensors" } },
    { ...local, model_info: null },
    { details: { format: "gguf", family: "llama" } },
    { details: { family: "qwen" }, template: "legacy template" }
  ]) {
    await t.test(JSON.stringify(metadata), async (t) => {
      const { client } = await provider(t, (_req, res) => res.end(JSON.stringify(metadata)));
      assert.equal((await client.inspect("llama3.2:3b")).status, "UNVERIFIED");
    });
  }
});

test("redirects and provider errors never cause fallback/download requests", async (t) => {
  for (const status of [301, 302, 307, 404, 500]) {
    await t.test(String(status), async (t) => {
      const { client, calls } = await provider(t, (_req, res) => {
        res.writeHead(status, { Location: "https://example.invalid/pull" });
        res.end("{}");
      });
      await assert.rejects(client.list(), /non-200/);
      assert.equal(calls.length, 1);
    });
  }
});

test("malformed, oversized and unsupported lists fail boundedly", async (t) => {
  for (const payload of [
    "invalid json", "null", "[]", "{}", '{"models":{}}',
    JSON.stringify({ models: Array.from({ length: MAX_MODELS + 1 }, () => model) }),
    " ".repeat(MAX_BYTES + 1)
  ]) {
    await t.test(`payload ${payload.length}`, async (t) => {
      const { client } = await provider(t, (_req, res) => res.end(payload));
      await assert.rejects(client.list(), /JSON|metadata|list|byte limit/);
    });
  }
  const { client } = await provider(t, (_req, res) => {
    res.setHeader("Content-Length", MAX_BYTES + 1);
    res.write("{}");
  });
  await assert.rejects(client.list(), /byte limit/);
});

test("timeouts, interrupted bodies and aborts do not leave ongoing inspections", async (t) => {
  const { client } = await provider(t, (_req, res) => res.write("{"), 40);
  await assert.rejects(client.list(), /timed out/);
  const controller = new AbortController();
  controller.abort();
  await assert.rejects(client.list({ signal: controller.signal }), { name: "AbortError" });
  const interrupted = await provider(t, (_req, res) => {
    res.writeHead(200, { "Content-Length": 1000 });
    res.write("{}");
    setImmediate(() => res.destroy());
  });
  await assert.rejects(interrupted.client.list(), /interrupted|failed|unavailable/);
  const aborting = new AbortController();
  const open = await provider(t, (_req, res) => {
    res.write("{");
    aborting.abort();
  });
  await assert.rejects(open.client.inspect(model.name, { signal: aborting.signal }), { name: "AbortError" });
});

test("unavailable engine and invalid client arguments fail without arbitrary networking", async () => {
  const client = createOllamaModels({ request() { throw new Error("offline"); } });
  await assert.rejects(client.list(), /unavailable/);
  await assert.rejects(client.list({ signal: {} }), /AbortSignal/);
  for (const timeoutMs of [0, -1, Infinity, 10001]) {
    assert.throws(() => createOllamaModels({ timeoutMs }), /timeout/);
  }
});

test("model chooser keeps bundled/current choice on success, cancellation and discovery failure", async () => {
  const source = fs.readFileSync(path.join(__dirname, "../renderer.js"), "utf8");
  const start = source.indexOf('document.querySelector("#harness-list-models").addEventListener');
  const end = source.indexOf('document.querySelector("#harness-form").addEventListener', start);
  assert.ok(start >= 0 && end > start);
  for (const mode of ["success", "cancel", "failure", "empty"]) {
    const elements = {
      "#harness-list-models": { disabled: false },
      "#harness-model-message": { textContent: "" },
      "#harness-model-options": {
        children: [], replaceChildren(...nodes) { this.children = nodes; },
        append(node) { this.children.push(node); }
      },
      "#harness-model": { value: "psicat:embedded" }
    };
    let click;
    elements["#harness-list-models"].addEventListener = (_event, callback) => { click = callback; };
    vm.runInNewContext(source.slice(start, end), {
      document: { querySelector: (id) => elements[id], createElement: () => ({}) },
      window: { axiomSuite: { listOllamaModels: async () => {
        if (mode === "failure") throw new Error("Start Ollama yourself");
        if (mode === "cancel") return { canceled: true };
        return { models: mode === "empty" ? [] : [{ name: model.name, sizeBytes: model.size }],
          omitted: 0, boundary: "UNVERIFIED" };
      } } }
    });
    await click();
    assert.equal(elements["#harness-model"].value, "psicat:embedded");
    assert.equal(elements["#harness-list-models"].disabled, false);
    const message = elements["#harness-model-message"].textContent;
    if (mode === "success") {
      assert.equal(elements["#harness-model-options"].children[1].value, model.name);
      assert.match(message, /choose a name explicitly/);
    } else if (mode === "cancel") assert.match(message, /No model service was contacted/);
    else if (mode === "failure") assert.match(message, /Start Ollama yourself/);
    else assert.equal(elements["#harness-model-options"].children.length, 1);
  }
});
