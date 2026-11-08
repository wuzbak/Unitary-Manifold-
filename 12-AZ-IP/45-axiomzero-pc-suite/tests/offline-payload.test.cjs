// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 ThomasCory Walker-Pearson
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const { execFileSync } = require("node:child_process");
const { stage, verify, finalize, hashFile, PART_BYTES, MODEL_FILE, manifestName } = require("../scripts/offline-payload.cjs");
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");

async function fixture(t) {
  const root = path.resolve(__dirname, "../build", `payload-test-${crypto.randomUUID()}`);
  await fs.mkdir(path.join(root, "build/instruction"), { recursive: true });
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const model = Buffer.from("GGUFsynthetic-test-only!");
  const runtime = { formatVersion: 1, model: { file: MODEL_FILE, repository: "unsloth/Qwen3-4B-Instruct-2507-GGUF",
    revision: "a".repeat(40), license: "Apache-2.0", sizeBytes: model.length, sha256: hash(model) }, engine: {} };
  await fs.writeFile(path.join(root, "package.json"), '{"version":"0.1.0"}');
  await fs.writeFile(path.join(root, "build/instruction/manifest.json"), JSON.stringify(runtime));
  await fs.writeFile(path.join(root, "build/instruction", MODEL_FILE), model);
  return { root, model, runtime };
}

test("offline staging splits byte-exact bounded parts and binds runtime and payload manifests", async (t) => {
  const { root, model } = await fixture(t);
  const manifest = await stage(root, 8);
  assert.equal(PART_BYTES, 1073741824);
  assert.equal(manifest.parts.length, 3);
  const parts = await Promise.all(manifest.parts.map((part) => fs.readFile(path.join(root, "dist", part.file))));
  assert.deepEqual(Buffer.concat(parts), model);
  assert.equal((await verify(root, false)).model.sha256, hash(model));
  const config = await fs.readFile(path.join(root, "build/offline-payload/payload-config.nsh"), "utf8");
  assert.ok(config.includes(hash(await fs.readFile(path.join(root, "dist", manifestName("0.1.0"))))));
  assert.ok(config.includes(manifestName("0.1.0")));
  await assert.rejects(verify(root), /ENOENT/);
  await fs.writeFile(path.join(root, "dist/AxiomZero-PC-Suite-0.1.0-x64.exe"), "synthetic installer");
  await verify(root);
  const sums = await fs.readFile(path.join(root, "dist/SHA256SUMS.txt"), "utf8");
  assert.equal(sums.trim().split("\n").length, 5);
});

test("staging rejects model tampering, size mismatch and unsafe provenance/version", async (t) => {
  const { root, model, runtime } = await fixture(t);
  await fs.writeFile(path.join(root, "build/instruction", MODEL_FILE), Buffer.alloc(model.length));
  await assert.rejects(stage(root, 8), /SHA-256 mismatch/);
  await fs.writeFile(path.join(root, "build/instruction", MODEL_FILE), "short");
  await assert.rejects(stage(root, 8), /size mismatch/);
  runtime.model.file = "../unsafe.gguf";
  await fs.writeFile(path.join(root, "build/instruction/manifest.json"), JSON.stringify(runtime));
  await assert.rejects(stage(root, 8), /Unsupported/);
  await fs.writeFile(path.join(root, "package.json"), '{"version":"0.1.0\\\"\\n!system evil"}');
  await assert.rejects(stage(root, 8), /Unsafe/);
  await assert.rejects(stage(root, PART_BYTES + 1), /part size/);
});

test("release verification rejects missing, tampered and renamed companion parts or manifest", async (t) => {
  const { root } = await fixture(t);
  const manifest = await stage(root, 8);
  const part = path.join(root, "dist", manifest.parts[0].file);
  const bytes = await fs.readFile(part);
  await fs.unlink(part);
  await assert.rejects(verify(root, false), /ENOENT/);
  await fs.writeFile(part, Buffer.alloc(bytes.length));
  await assert.rejects(verify(root, false), /integrity mismatch/);
  await fs.writeFile(part, bytes);
  await fs.appendFile(path.join(root, "dist", manifestName("0.1.0")), " ");
  await assert.rejects(verify(root, false), /installer-bound/);
});

test("staging handles a final partial part and safely regenerates its own versioned output", async (t) => {
  const { root, model } = await fixture(t);
  const first = await stage(root, 9);
  assert.deepEqual(first.parts.map((part) => part.sizeBytes), [9, 9, 6]);
  await fs.writeFile(path.join(root, "dist/keep-unrelated.txt"), "keep");
  const second = await stage(root, 8);
  assert.deepEqual(second.parts.map((part) => part.sizeBytes), [8, 8, 8]);
  assert.equal((await verify(root, false)).model.sha256, hash(model));
  assert.equal(await fs.readFile(path.join(root, "dist/keep-unrelated.txt"), "utf8"), "keep");
});

test("finalization restores the full unpacked model only after verifying the release set", async (t) => {
  const { root, model } = await fixture(t);
  await stage(root, 8);
  await fs.mkdir(path.join(root, "dist/win-unpacked/resources/psicat-instruction"), { recursive: true });
  await assert.rejects(finalize(root), /ENOENT/);
  await fs.writeFile(path.join(root, "dist/AxiomZero-PC-Suite-0.1.0-x64.exe"), "synthetic installer");
  await finalize(root);
  assert.equal(await hashFile(path.join(root, "dist/win-unpacked/resources/psicat-instruction", MODEL_FILE)), hash(model));
  await assert.rejects(finalize(root), /EEXIST/);
});

test("NSIS uses fail-closed local EXEDIR hooks, excludes only the model, and has no portable/web target", async () => {
  const pkg = require("../package.json");
  assert.deepEqual(pkg.build.win.target, ["nsis"]);
  assert.equal(pkg.build.nsis.perMachine, false);
  assert.equal(pkg.build.nsis.runAfterFinish, false);
  assert.deepEqual(pkg.build.extraResources.find((resource) => resource.from === "build/instruction").filter, ["**/*", "!*.gguf"]);
  assert.match(pkg.scripts["dist:win"], /payload:stage && electron-builder --win nsis --x64 --publish never && node scripts\/offline-payload.cjs finalize/);
  const nsis = await fs.readFile(path.join(__dirname, "../scripts/offline-installer.nsh"), "utf8");
  assert.match(nsis, /!macro customInit[\s\S]*-PayloadDirectory "\$EXEDIR"[\s\S]*-ValidateOnly/);
  assert.match(nsis, /!macro customInstall[\s\S]*-DestinationDirectory "\$INSTDIR\\resources\\psicat-instruction"/);
  assert.equal((nsis.match(/SetErrorLevel 1\s+Quit/g) || []).length, 2);
  assert.doesNotMatch(nsis, /downloadApplicationFiles|APP_PACKAGE_URL/);
  const ps = await fs.readFile(path.join(__dirname, "../scripts/install-offline-payload.ps1"), "utf8");
  assert.match(ps, /FileShare\]::Read/);
  assert.match(ps, /ReparsePoint/);
  assert.match(ps, /FileMode\]::CreateNew/);
  assert.match(ps, /\[IO\.File\]::Move\(\$partial, \$destination\)/);
  assert.doesNotMatch(ps, /Invoke-Expression|Invoke-WebRequest|Start-BitsTransfer|DownloadFile/);
});

test("PowerShell join validates, atomically installs, and rejects tampering without overwrites", {
  skip: process.platform !== "win32" && !process.env.P45_POWERSHELL ? "Windows CI runs the shipped PowerShell script; P45_POWERSHELL enables local script validation" : false
}, async (t) => {
  const { root, model } = await fixture(t);
  const manifest = await stage(root, 8);
  const destination = path.join(root, "installed model with spaces");
  await fs.mkdir(destination);
  const bytes = await fs.readFile(path.join(root, "dist", manifestName("0.1.0")));
  const args = ["-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
    "-File", path.resolve(__dirname, "../scripts/install-offline-payload.ps1"),
    "-PayloadDirectory", path.join(root, "dist"), "-ManifestName", manifestName("0.1.0"),
    "-ManifestSha256", hash(bytes), "-RuntimeManifest", path.join(root, "build/instruction/manifest.json")];
  const run = (extra = []) => execFileSync(process.env.P45_POWERSHELL || "powershell.exe", [...args, ...extra], { encoding: "utf8", stdio: "pipe" });
  assert.match(run(["-ValidateOnly"]), /VERIFIED OFFLINE/);
  assert.deepEqual(await fs.readdir(destination), []);
  const part = path.join(root, "dist", manifest.parts[1].file);
  const original = await fs.readFile(part);
  await fs.unlink(part);
  assert.throws(() => run(["-DestinationDirectory", destination]), /Command failed/);
  await fs.writeFile(part, Buffer.alloc(original.length));
  assert.throws(() => run(["-DestinationDirectory", destination]), /SHA-256 mismatch/);
  assert.deepEqual(await fs.readdir(destination), []);
  await fs.writeFile(part, original);
  const runtimePath = path.join(root, "build/instruction/manifest.json");
  const runtimeBytes = await fs.readFile(runtimePath);
  await fs.appendFile(runtimePath, " ");
  assert.throws(() => run(["-ValidateOnly"]), /manifest SHA-256 mismatch/);
  await fs.writeFile(runtimePath, runtimeBytes);
  const payloadPath = path.join(root, "dist", manifestName("0.1.0"));
  const validateChangedManifest = (payload, error) => {
    const changed = Buffer.from(JSON.stringify(payload));
    return fs.writeFile(payloadPath, changed).then(() => {
      const changedArgs = [...args];
      changedArgs[changedArgs.indexOf("-ManifestSha256") + 1] = hash(changed);
      assert.throws(() => execFileSync(process.env.P45_POWERSHELL || "powershell.exe",
        [...changedArgs, "-DestinationDirectory", destination], { encoding: "utf8", stdio: "pipe" }), error);
    });
  };
  await validateChangedManifest({ ...manifest, parts: [{ ...manifest.parts[0], file: "../unsafe.part001" }, ...manifest.parts.slice(1)] }, /Unsafe offline part metadata/);
  await validateChangedManifest({ ...manifest, parts: [manifest.parts[1], manifest.parts[0], manifest.parts[2]] }, /Unsafe offline part metadata/);
  await validateChangedManifest({ ...manifest, unexpectedField: true }, /Unexpected manifest fields/);
  await validateChangedManifest({ ...manifest, model: { ...manifest.model, sha256: "0".repeat(64) } }, /Model differs from the runtime manifest/);
  const changedRuntime = JSON.parse(runtimeBytes);
  changedRuntime.model.sha256 = "0".repeat(64);
  const changedRuntimeBytes = Buffer.from(JSON.stringify(changedRuntime));
  await fs.writeFile(runtimePath, changedRuntimeBytes);
  await validateChangedManifest({ ...manifest, runtimeManifestSha256: hash(changedRuntimeBytes),
    model: { ...manifest.model, sha256: changedRuntime.model.sha256 } }, /Approved full-model SHA-256 mismatch/);
  assert.deepEqual(await fs.readdir(destination), []);
  await fs.writeFile(runtimePath, runtimeBytes);
  await fs.writeFile(payloadPath, bytes);
  const redirected = path.join(root, "redirected-destination");
  await fs.symlink(destination, redirected, "junction");
  assert.throws(() => run(["-DestinationDirectory", redirected]), /Reparse points are not permitted/);
  assert.match(run(["-DestinationDirectory", destination]), /VERIFIED OFFLINE/);
  assert.deepEqual(await fs.readFile(path.join(destination, MODEL_FILE)), model);
  assert.throws(() => run(["-DestinationDirectory", destination]), /Refusing to overwrite/);
  await fs.appendFile(path.join(root, "dist", manifestName("0.1.0")), " ");
  assert.throws(() => run(["-ValidateOnly"]), /manifest SHA-256 mismatch/);
});
