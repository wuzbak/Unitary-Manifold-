const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");

async function readDownload(url, limit, signal, fetchResource) {
  const response = await fetchResource(url, { signal, redirect: "error" });
  if (!response.ok || !response.body) throw new Error(`Node download failed: HTTP ${response.status}.`);
  const chunks = [];
  let size = 0;
  for await (const chunk of response.body) {
    size += chunk.length;
    if (size > limit) {
      throw new Error("Node download exceeded its byte budget.");
    }
    chunks.push(Buffer.from(chunk));
  }
  return Buffer.concat(chunks);
}

async function installNodeLts({
  directory, extractionScript, execute, fetchResource = fetch, platform = process.platform,
  architecture = process.arch
}) {
  if (platform !== "win32" || architecture !== "x64") throw new Error("Managed Node bootstrap supports Windows x64 only.");
  const destination = path.join(directory, "node-lts");
  if (fs.existsSync(destination)) throw new Error("Managed Node LTS is already installed; restart the suite to use it.");
  fs.mkdirSync(directory, { recursive: true });
  const pending = fs.mkdtempSync(path.join(directory, "node-download-"));
  try {
    const signal = AbortSignal.timeout(600000);
    const manifest = await readDownload("https://nodejs.org/dist/latest-v24.x/SHASUMS256.txt", 65536, signal, fetchResource);
    const match = manifest.toString("utf8").match(/^([0-9a-f]{64}) {2}(node-v24\.\d+\.\d+-win-x64\.zip)$/m);
    if (!match) throw new Error("The official Node LTS manifest has no valid Windows x64 archive.");
    const filename = match[2];
    const versionDirectory = filename.slice(5, -"-win-x64.zip".length);
    const archive = await readDownload(`https://nodejs.org/dist/${versionDirectory}/${filename}`, 100 * 1024 * 1024, signal, fetchResource);
    if (crypto.createHash("sha256").update(archive).digest("hex") !== match[1]) throw new Error("Node archive checksum failed.");
    const archivePath = path.join(pending, "node.zip");
    fs.writeFileSync(archivePath, archive, { flag: "wx" });
    const extracted = path.join(pending, "extracted");
    await execute("powershell.exe", [
      "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", extractionScript,
      "-Archive", archivePath, "-Destination", extracted
    ], { cwd: pending, timeoutMs: 120000 });
    const runtime = path.join(extracted, filename.slice(0, -4));
    for (const file of ["node.exe", "node_modules/npm/bin/npm-cli.js", "LICENSE"]) {
      if (!fs.existsSync(path.join(runtime, file)) || !fs.statSync(path.join(runtime, file)).isFile()) {
        throw new Error(`The official Node archive is missing ${file}.`);
      }
    }
    const receipt = { version: versionDirectory, sha256: match[1], source: `https://nodejs.org/dist/${versionDirectory}/${filename}` };
    fs.writeFileSync(path.join(runtime, "INSTALL_RECEIPT.json"), `${JSON.stringify(receipt, null, 2)}\n`);
    await execute(path.join(runtime, "node.exe"), ["--version"], { cwd: runtime, timeoutMs: 10000 });
    fs.renameSync(runtime, destination);
    return receipt;
  } finally {
    fs.rmSync(pending, { recursive: true, force: true });
  }
}

module.exports = { installNodeLts };
