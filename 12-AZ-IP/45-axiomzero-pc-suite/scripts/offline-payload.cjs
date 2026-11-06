// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026  ThomasCory Walker-Pearson
"use strict";

const fs = require("node:fs/promises");
const { constants, createReadStream } = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");

const PART_BYTES = 1024 ** 3;
const MODEL_FILE = "Qwen3-4B-Instruct-2507-Q4_K_M.gguf";
const suite = path.resolve(__dirname, "..");
const digest = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const partName = (version, index) => `AxiomZero-PC-Suite-${version}-model.part${String(index + 1).padStart(3, "0")}`;
const manifestName = (version) => `AxiomZero-PC-Suite-${version}-offline.json`;

async function regularFile(file) {
  const stat = await fs.lstat(file);
  if (!stat.isFile() || stat.isSymbolicLink()) throw new Error(`Not a regular payload file: ${file}`);
  return stat;
}

async function hashFile(file) {
  await regularFile(file);
  const hash = crypto.createHash("sha256");
  for await (const bytes of createReadStream(file, { flags: constants.O_RDONLY | (constants.O_NOFOLLOW || 0) })) hash.update(bytes);
  return hash.digest("hex");
}

function validateRuntime(runtime) {
  const model = runtime.model;
  if (runtime.formatVersion !== 1 || model?.file !== MODEL_FILE ||
      model.repository !== "unsloth/Qwen3-4B-Instruct-2507-GGUF" ||
      !/^[a-f0-9]{40}$/.test(model.revision) || model.license !== "Apache-2.0" ||
      !/^[a-f0-9]{64}$/.test(model.sha256) ||
      !Number.isSafeInteger(model.sizeBytes) || model.sizeBytes < 8 || model.sizeBytes > 3000000000) {
    throw new Error("Unsupported approved model manifest");
  }
}

async function stage(root = suite, partBytes = PART_BYTES) {
  if (!Number.isSafeInteger(partBytes) || partBytes < 1 || partBytes > PART_BYTES) throw new Error("Invalid part size");
  const version = JSON.parse(await fs.readFile(path.join(root, "package.json"), "utf8")).version;
  if (!/^\d+\.\d+\.\d+$/.test(version)) throw new Error("Unsafe payload version");
  const source = path.join(root, "build/instruction");
  const runtimeBytes = await fs.readFile(path.join(source, "manifest.json"));
  const runtime = JSON.parse(runtimeBytes);
  validateRuntime(runtime);
  const modelPath = path.join(source, MODEL_FILE);
  if ((await regularFile(modelPath)).size !== runtime.model.sizeBytes) throw new Error("Model size mismatch");
  const dist = path.join(root, "dist");
  const generated = path.join(root, "build/offline-payload");
  await fs.mkdir(dist, { recursive: true });
  await fs.mkdir(generated, { recursive: true });
  // Delete only this version's own stale output, never unrelated distribution files.
  for (const name of await fs.readdir(dist)) {
    if (name === manifestName(version) || name.startsWith(`AxiomZero-PC-Suite-${version}-model.part`)) {
      await fs.unlink(path.join(dist, name));
    }
  }
  const parts = [];
  const fullHash = crypto.createHash("sha256");
  let handle, partHash, size = 0, total = 0;
  try {
    for await (const chunk of createReadStream(modelPath, { highWaterMark: 1024 * 1024, flags: constants.O_RDONLY | (constants.O_NOFOLLOW || 0) })) {
      fullHash.update(chunk);
      total += chunk.length;
      let offset = 0;
      while (offset < chunk.length) {
        if (!handle) {
          const file = partName(version, parts.length);
          handle = await fs.open(path.join(dist, file), "wx");
          partHash = crypto.createHash("sha256");
          size = 0;
        }
        const bytes = chunk.subarray(offset, offset + Math.min(partBytes - size, chunk.length - offset));
        let written = 0;
        while (written < bytes.length) written += (await handle.write(bytes, written, bytes.length - written)).bytesWritten;
        partHash.update(bytes);
        size += bytes.length;
        offset += bytes.length;
        if (size === partBytes) {
          await handle.close();
          handle = null;
          parts.push({ file: partName(version, parts.length), sizeBytes: size, sha256: partHash.digest("hex") });
        }
      }
    }
    if (handle) {
      await handle.close();
      handle = null;
      parts.push({ file: partName(version, parts.length), sizeBytes: size, sha256: partHash.digest("hex") });
    }
    if (total !== runtime.model.sizeBytes || fullHash.digest("hex") !== runtime.model.sha256) throw new Error("Approved full-model SHA-256 mismatch");
    const manifest = { formatVersion: 1, version, runtimeManifestSha256: digest(runtimeBytes), model: {
      file: MODEL_FILE, sizeBytes: total, sha256: runtime.model.sha256
    }, parts };
    const bytes = Buffer.from(JSON.stringify(manifest, null, 2) + "\n");
    await fs.writeFile(path.join(dist, manifestName(version)), bytes, { flag: "wx" });
    await fs.writeFile(path.join(generated, "payload-manifest.json"), bytes);
    await fs.writeFile(path.join(generated, "runtime-manifest.json"), runtimeBytes);
    await fs.writeFile(path.join(generated, "payload-config.nsh"),
      `!define P45_PAYLOAD_MANIFEST "${manifestName(version)}"\n!define P45_PAYLOAD_SHA256 "${digest(bytes)}"\n`);
    return manifest;
  } finally {
    if (handle) await handle.close();
  }
}

async function verify(root = suite, release = true) {
  const version = JSON.parse(await fs.readFile(path.join(root, "package.json"), "utf8")).version;
  const dist = path.join(root, "dist");
  const expectedBytes = await fs.readFile(path.join(root, "build/offline-payload/payload-manifest.json"));
  const payloadBytes = await fs.readFile(path.join(dist, manifestName(version)));
  if (!payloadBytes.equals(expectedBytes)) throw new Error("Offline manifest differs from installer-bound manifest");
  const manifest = JSON.parse(payloadBytes);
  const fullHash = crypto.createHash("sha256");
  let total = 0;
  for (const [index, part] of manifest.parts.entries()) {
    if (part.file !== partName(version, index) || part.sizeBytes > PART_BYTES) throw new Error("Invalid part contract");
    const file = path.join(dist, part.file);
    if ((await regularFile(file)).size !== part.sizeBytes || await hashFile(file) !== part.sha256) throw new Error("Payload part integrity mismatch");
    for await (const bytes of createReadStream(file)) fullHash.update(bytes);
    total += part.sizeBytes;
  }
  if (total !== manifest.model.sizeBytes || fullHash.digest("hex") !== manifest.model.sha256) throw new Error("Full payload integrity mismatch");
  const names = [manifestName(version), ...manifest.parts.map((part) => part.file)];
  if (release) names.unshift(`AxiomZero-PC-Suite-${version}-x64.exe`);
  const sums = [];
  for (const name of names) {
    const file = path.join(dist, name);
    if ((await regularFile(file)).size >= 2 * 1024 ** 3) throw new Error("Release asset exceeds GitHub/NSIS size ceiling");
    sums.push(`${await hashFile(file)}  ${name}`);
  }
  if (release) await fs.writeFile(path.join(dist, "SHA256SUMS.txt"), sums.join("\n") + "\n");
  return manifest;
}

async function finalize(root = suite) {
  const manifest = await verify(root);
  // Restore the full approved model only AFTER NSIS archive creation for real unpacked diagnostics.
  const source = path.join(root, "build/instruction", MODEL_FILE);
  if (await hashFile(source) !== manifest.model.sha256) throw new Error("Model changed after packaging");
  const target = path.join(root, "dist/win-unpacked/resources/psicat-instruction", MODEL_FILE);
  await fs.copyFile(source, target, constants.COPYFILE_EXCL);
  if (await hashFile(target) !== manifest.model.sha256) throw new Error("Unpacked model restoration failed");
}

if (require.main === module) {
  const commands = { stage, verify, finalize };
  const command = commands[process.argv[2]];
  if (!command) throw new Error("Expected stage, verify or finalize");
  command().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
module.exports = { stage, verify, finalize, hashFile, PART_BYTES, MODEL_FILE, manifestName, partName };
