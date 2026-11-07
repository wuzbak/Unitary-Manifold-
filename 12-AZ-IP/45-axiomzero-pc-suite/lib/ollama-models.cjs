// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026  ThomasCory Walker-Pearson
"use strict";

const http = require("node:http");

const MAX_BYTES = 65536;
const TIMEOUT_MS = 10000;
const MAX_MODELS = 200;

function safeName(name) {
  return typeof name === "string" && name.length <= 80 &&
    /^[A-Za-z0-9][A-Za-z0-9_.:/-]*$/.test(name);
}
function localOnly(value) {
  return !Object.hasOwn(value, "remote_host") && !Object.hasOwn(value, "remote_model");
}
function cancelled() {
  return Object.assign(new Error("Local model inspection was aborted."), { name: "AbortError" });
}

function createOllamaModels({ request = http.request, timeoutMs = TIMEOUT_MS } = {}) {
  if (typeof request !== "function" || !Number.isFinite(timeoutMs) ||
      timeoutMs <= 0 || timeoutMs > TIMEOUT_MS) throw new TypeError("Invalid model inspection transport or timeout.");

  async function query(apiPath, body, signal) {
    if (signal !== undefined && !(signal instanceof AbortSignal)) throw new TypeError("Signal must be an AbortSignal.");
    if (signal?.aborted) throw cancelled();
    const payload = body === null ? null : JSON.stringify(body);
    return new Promise((resolve, reject) => {
      let req;
      let response;
      let settled = false;
      const finish = (error, value) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        signal?.removeEventListener("abort", abort);
        if (error) {
          response?.destroy();
          req?.destroy();
          reject(error);
        } else resolve(value);
      };
      const abort = () => finish(cancelled());
      const timer = setTimeout(() => finish(new Error("Local model inspection timed out. Check Ollama and retry explicitly.")), timeoutMs);
      signal?.addEventListener("abort", abort, { once: true });
      if (signal?.aborted) { abort(); return; }
      try {
        req = request({
          protocol: "http:", hostname: "127.0.0.1", family: 4, port: 11434,
          path: apiPath, method: payload === null ? "GET" : "POST", agent: false,
          headers: payload === null ? {} : {
            "Content-Type": "application/json", "Content-Length": Buffer.byteLength(payload)
          }
        }, (res) => {
          response = res;
          if (settled) { res.destroy(); return; }
          res.on("error", () => finish(new Error("Local model inspection response failed.")));
          res.on("aborted", () => finish(new Error("Local model inspection was interrupted.")));
          if (res.statusCode !== 200) {
            finish(new Error("Ollama returned a non-200 status. Start the local engine and confirm the model is installed; redirects are not followed."));
            return;
          }
          if (Number(res.headers["content-length"]) > MAX_BYTES) {
            finish(new Error("Local model metadata exceeds the byte limit."));
            return;
          }
          const chunks = [];
          let bytes = 0;
          res.on("data", (chunk) => {
            if (settled) return;
            bytes += chunk.length;
            if (bytes > MAX_BYTES) finish(new Error("Local model metadata exceeds the byte limit."));
            else chunks.push(chunk);
          });
          res.on("end", () => {
            if (settled) return;
            let result;
            try { result = JSON.parse(Buffer.concat(chunks).toString("utf8")); }
            catch { finish(new Error("Ollama returned invalid model metadata JSON.")); return; }
            if (!result || typeof result !== "object" || Array.isArray(result)) {
              finish(new Error("Ollama returned unsupported model metadata."));
              return;
            }
            finish(null, result);
          });
          res.on("close", () => {
            if (!res.complete) finish(new Error("Local model inspection was interrupted."));
          });
        });
        req.on("error", () => finish(new Error("Ollama is unavailable at 127.0.0.1:11434. Start it yourself, then retry; no installation or download was attempted.")));
        req.end(payload);
        if (settled) req.destroy();
      } catch {
        finish(new Error("Ollama is unavailable at 127.0.0.1:11434."));
      }
    });
  }

  return Object.freeze({
    async list({ signal } = {}) {
      const result = await query("/api/tags", null, signal);
      if (!Array.isArray(result.models) || result.models.length > MAX_MODELS) {
        throw new Error("Ollama returned an unsupported installed-model list.");
      }
      const models = [];
      for (const model of result.models) {
        if (!model || typeof model !== "object" || Array.isArray(model) ||
            !safeName(model.name) || model.name === "psicat:embedded" ||
            /:cloud$/i.test(model.name) || !localOnly(model) ||
            !Number.isSafeInteger(model.size) || model.size <= 0 ||
            typeof model.digest !== "string" || !/^(?:sha256:)?[a-f0-9]{64}$/.test(model.digest)) continue;
        if (!models.some((item) => item.name === model.name)) {
          models.push({ name: model.name, sizeBytes: model.size, digest: model.digest });
        }
      }
      return { models, omitted: result.models.length - models.length,
        boundary: "UNVERIFIED engine-reported metadata, not artifact provenance or a compatibility certificate. No model was loaded or downloaded." };
    },
    async inspect(model, { signal } = {}) {
      if (!safeName(model) || model === "psicat:embedded" || /:cloud$/i.test(model)) {
        throw new TypeError("Choose an installed local Ollama model, not a cloud model.");
      }
      const result = await query("/api/show", { model, verbose: false }, signal);
      if (!localOnly(result)) throw new Error("Cloud/remote Ollama models are not permitted. Import a local GGUF yourself.");
      if ((Object.hasOwn(result, "capabilities") &&
          (!Array.isArray(result.capabilities) || !result.capabilities.includes("completion"))) ||
          (!Object.hasOwn(result, "capabilities") &&
          (!result.details || typeof result.details !== "object" || Array.isArray(result.details)))) {
        throw new Error("Installed model does not report a completion runtime or recognizable legacy model details. Update/check Ollama and its architecture/quantization support; no fallback or download was attempted.");
      }
      return { status: "UNVERIFIED", model };
    }
  });
}

module.exports = { createOllamaModels, MAX_BYTES, TIMEOUT_MS, MAX_MODELS };
