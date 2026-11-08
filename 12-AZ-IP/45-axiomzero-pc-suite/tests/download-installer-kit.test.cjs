// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 ThomasCory Walker-Pearson
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const { execFileSync } = require("node:child_process");
const { stage } = require("../scripts/offline-payload.cjs");
const script = path.resolve(__dirname, "../scripts/download-installer-kit.ps1");
const digest = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const shell = process.env.P45_POWERSHELL || (process.platform === "win32" ? "powershell.exe" : null);

test("download helper is explicit, pinned, bounded, exclusive, and never executes payloads", async () => {
  const source = await fs.readFile(script, "utf8");
  assert.match(source, /\$Tag = 'pc-suite-v0\.1\.0'/);
  assert.match(source, /Read-Host 'Type DOWNLOAD/);
  assert.match(source, /FileMode\]::CreateNew/);
  assert.match(source, /AllowAutoRedirect = \$false/);
  assert.match(source, /\$redirects -ge 5/);
  assert.match(source, /ReadWriteTimeout = 60000/);
  assert.match(source, /\$total -gt \$Limit/);
  assert.match(source, /ReparsePoint/);
  assert.match(source, /Test-KitManifest \$plan/);
  assert.match(source, /function Get-KitSha256[\s\S]*SHA256\]::Create\(\)[\s\S]*ComputeHash\(\$stream\)/);
  assert.match(source, /\(Get-KitSha256 \$Path\) -cne \$Hash/);
  assert.doesNotMatch(source, /Get-FileHash\s+-/);
  assert.doesNotMatch(source, /Invoke-Expression|Start-Process|Start-BitsTransfer|ExecutionPolicy Bypass|Register-ScheduledTask/);
  const workflow = await fs.readFile(path.resolve(__dirname, "../../../.github/workflows/pc-suite-windows.yml"), "utf8");
  assert.match(workflow, /shell: powershell[\s\S]*P45_POWERSHELL = "powershell.exe"/);
  assert.match(workflow, /needs: \[browser-desktop-runtime, instruction-backend, platform-artifacts, recovered-python-products\]/);
  assert.match(workflow, /payload:verify[\s\S]*Copy-Item[\s\S]*Add-Content -LiteralPath dist\/SHA256SUMS.txt/);
  assert.match(workflow, /dist\/\*-download\.ps1/);
});

test("PowerShell helper retrieves only synthetic approved files and fails closed", {
  skip: !shell ? "Windows CI executes native PowerShell 5.1; P45_POWERSHELL enables local validation" : false,
}, async (t) => {
  const root = path.resolve(__dirname, "../build", `download-test-${crypto.randomUUID()}`);
  await fs.mkdir(path.join(root, "build/instruction"), { recursive: true });
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const model = Buffer.from("GGUFsynthetic-test-only!");
  const runtime = { formatVersion: 1, model: { file: "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
    repository: "unsloth/Qwen3-4B-Instruct-2507-GGUF", revision: "a".repeat(40),
    license: "Apache-2.0", sizeBytes: model.length, sha256: digest(model) } };
  await fs.writeFile(path.join(root, "package.json"), '{"version":"0.1.0"}');
  await fs.writeFile(path.join(root, "build/instruction/manifest.json"), JSON.stringify(runtime));
  await fs.writeFile(path.join(root, "build/instruction", runtime.model.file), model);
  const manifest = await stage(root, 8);
  const prefix = "AxiomZero-PC-Suite-0.1.0";
  await fs.writeFile(path.join(root, "dist", `${prefix}-x64.exe`), "SYNTHETIC NOT EXECUTABLE");
  await fs.copyFile(script, path.join(root, "dist", `${prefix}-download.ps1`));
  const names = [`${prefix}-x64.exe`, `${prefix}-offline.json`, ...manifest.parts.map((p) => p.file), `${prefix}-download.ps1`];
  const baseUrl = "https://github.com/wuzbak/Unitary-Manifold-/releases/download/pc-suite-v0.1.0/";
  const assets = await Promise.all(names.map(async (name) => {
    const bytes = await fs.readFile(path.join(root, "dist", name));
    return { name, size: bytes.length, browser_download_url: baseUrl + name, hash: digest(bytes) };
  }));
  const sums = assets.map((asset) => `${asset.hash}  ${asset.name}`).join("\n") + "\n";
  await fs.writeFile(path.join(root, "dist/SHA256SUMS.txt"), sums);
  assets.push({ name: "SHA256SUMS.txt", size: Buffer.byteLength(sums), browser_download_url: baseUrl + "SHA256SUMS.txt" });
  const release = { tag_name: "pc-suite-v0.1.0", draft: false, assets };
  const releasePath = path.join(root, "release.json");
  const harness = path.join(root, "harness.ps1");
  await fs.writeFile(harness, `
$ErrorActionPreference = 'Stop'
$tokens = $null; $errors = $null
$null = [Management.Automation.Language.Parser]::ParseFile($env:KIT_SCRIPT, [ref]$tokens, [ref]$errors)
if ($errors.Count -ne 0) { throw "Script syntax errors: $errors" }
. $env:KIT_SCRIPT -Tag $env:KIT_TAG -DestinationDirectory $env:KIT_DESTINATION
function Receive-KitFile([string]$Url, [string]$Path, [long]$Limit, [long]$ExpectedSize = -1) {
    if ($Url -match '/releases/tags/') { $source = $env:KIT_RELEASE }
    else { $source = Join-Path $env:KIT_DIST ([Uri]$Url).Segments[-1] }
    $bytes = [IO.File]::ReadAllBytes($source)
    if ($bytes.Length -gt $Limit -or ($ExpectedSize -ge 0 -and $bytes.Length -ne $ExpectedSize)) { throw 'Mock bounded size mismatch.' }
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
    if ($env:KIT_MODE -eq 'network-failure' -and $Url -match 'part002$') { [IO.File]::Delete($Path); throw 'Synthetic interrupted download.' }
}
function Read-Host { return $env:KIT_CONSENT }
foreach ($bad in @('http://github.com/file', 'https://evil.example/file', 'https://user@github.com/file', 'https://github.com:444/file', 'https://github.com/file#fragment')) {
    $rejected = $false
    try { Assert-KitUrl $bad -Redirect } catch { $rejected = $true }
    if (-not $rejected) { throw 'Unsafe URL accepted.' }
}
Assert-KitUrl 'https://release-assets.githubusercontent.com/file?signature=synthetic' -Redirect
Invoke-InstallerKitDownload
`);
  let counter = 0;
  // Reproduces CI/user launches from PowerShell 7 whose module path a 5.1 child inherits.
  const inheritedModulePath = path.join(root, "inherited-pwsh7-modules");
  await fs.mkdir(path.join(inheritedModulePath, "Microsoft.PowerShell.Utility"), { recursive: true });
  const run = async ({ mutatedRelease = release, consent = "DOWNLOAD", mode = "", tag = "pc-suite-v0.1.0", existing = false } = {}) => {
    const destination = path.join(root, `kit-${++counter}`);
    await fs.mkdir(destination);
    if (existing) await fs.writeFile(path.join(destination, `${prefix}-x64.exe`), "KEEP");
    await fs.writeFile(releasePath, JSON.stringify(mutatedRelease));
    let output, error;
    try {
      output = execFileSync(shell, ["-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", harness], {
        encoding: "utf8", stdio: "pipe", env: { ...process.env, PSModulePath: inheritedModulePath, KIT_SCRIPT: script, KIT_TAG: tag,
          KIT_DESTINATION: destination, KIT_RELEASE: releasePath, KIT_DIST: path.join(root, "dist"), KIT_CONSENT: consent, KIT_MODE: mode },
      });
    } catch (caught) { error = String(caught.stderr || caught.stdout || caught); }
    const remaining = await fs.readdir(destination);
    assert.equal(remaining.some((name) => name.endsWith(".partial")), false, "partial files cleaned");
    return { output, error, destination, remaining };
  };
  const success = await run();
  assert.equal(success.error, undefined);
  assert.match(success.output, /VERIFIED INSTALLER KIT/);
  assert.deepEqual(success.remaining.sort(), [...names, "SHA256SUMS.txt"].sort());
  for (const name of success.remaining) assert.deepEqual(await fs.readFile(path.join(success.destination, name)), await fs.readFile(path.join(root, "dist", name)));
  for (const options of [
    { consent: "NO" }, { tag: "latest" }, { tag: "pc-suite-v../unsafe" }, { mode: "network-failure" },
    { mutatedRelease: { ...release, tag_name: "pc-suite-v0.2.0" } },
    { mutatedRelease: { ...release, draft: true } },
    { mutatedRelease: { ...release, assets: [...assets, assets[0]] } },
    { mutatedRelease: { ...release, assets: assets.filter((a) => a.name !== manifest.parts[1].file) } },
    { mutatedRelease: { ...release, assets: assets.map((a, i) => i === 0 ? { ...a, browser_download_url: "https://evil.example/file" } : a) } },
    { mutatedRelease: { ...release, assets: assets.map((a, i) => i === 0 ? { ...a, size: 2147483648 } : a) } },
  ]) {
    const failure = await run(options);
    assert.ok(failure.error, JSON.stringify(options));
    assert.deepEqual(failure.remaining, []);
  }
  const overwrite = await run({ existing: true });
  assert.match(overwrite.error, /Refusing to overwrite/);
  assert.equal(await fs.readFile(path.join(overwrite.destination, `${prefix}-x64.exe`), "utf8"), "KEEP");
  await fs.writeFile(path.join(root, "dist", manifest.parts[0].file), Buffer.alloc(8));
  const tampered = await run();
  assert.match(tampered.error, /SHA-256/);
  assert.deepEqual(tampered.remaining, []);
  await fs.writeFile(path.join(root, "dist", manifest.parts[0].file), model.subarray(0, 8));
  for (const bad of [
    `${"a".repeat(64)}  ../unsafe.exe\n`, `${"a".repeat(64)}  ${prefix}-model.part999\n`,
    sums + `${assets[0].hash}  ${assets[0].name}\n`,
  ]) {
    await fs.writeFile(path.join(root, "dist/SHA256SUMS.txt"), bad);
    const changed = { ...release, assets: assets.map((a) => a.name === "SHA256SUMS.txt" ? { ...a, size: Buffer.byteLength(bad) } : a) };
    const failure = await run({ mutatedRelease: changed });
    assert.ok(failure.error);
    assert.deepEqual(failure.remaining, []);
  }
  await fs.writeFile(path.join(root, "dist/SHA256SUMS.txt"), sums);
  const changedManifest = { ...manifest, model: { ...manifest.model, sha256: "0".repeat(64) } };
  const changedBytes = Buffer.from(JSON.stringify(changedManifest));
  await fs.writeFile(path.join(root, "dist", `${prefix}-offline.json`), changedBytes);
  const changedAssets = assets.map((a) => a.name === `${prefix}-offline.json` ? { ...a, size: changedBytes.length, hash: digest(changedBytes) } : a);
  const changedSums = changedAssets.filter((a) => a.name !== "SHA256SUMS.txt").map((a) => `${a.hash}  ${a.name}`).join("\n") + "\n";
  await fs.writeFile(path.join(root, "dist/SHA256SUMS.txt"), changedSums);
  const fullMismatch = await run({ mutatedRelease: { ...release, assets: changedAssets.map((a) => a.name === "SHA256SUMS.txt" ? { ...a, size: Buffer.byteLength(changedSums) } : a) } });
  assert.match(fullMismatch.error, /Full model size\/SHA-256 mismatch/);
  assert.deepEqual(fullMismatch.remaining, []);
});
