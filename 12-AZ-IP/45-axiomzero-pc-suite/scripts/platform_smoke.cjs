const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const yauzl = require("yauzl");
const { createPlatformTargets } = require("../lib/platform-targets.cjs");

async function verifyApk(file) {
  const entries = await new Promise((resolve, reject) => {
    yauzl.open(file, { lazyEntries: true }, (error, zip) => {
      if (error) return reject(error);
      const names = new Set();
      zip.on("error", reject);
      zip.on("entry", (entry) => { names.add(entry.fileName); zip.readEntry(); });
      zip.on("end", () => resolve(names));
      zip.readEntry();
    });
  });
  assert.ok(entries.has("AndroidManifest.xml"), "APK must contain its actual Android manifest");
  assert.ok(entries.has("classes.dex"), "APK must contain compiled application code");
}

function verifyUefi(file) {
  const bytes = fs.readFileSync(file);
  assert.equal(bytes.toString("ascii", 0, 2), "MZ");
  const pe = bytes.readUInt32LE(0x3c);
  assert.equal(bytes.toString("binary", pe, pe + 4), "PE\0\0");
  assert.equal(bytes.readUInt16LE(pe + 4), 0x8664, "UEFI target must be AMD64");
  assert.equal(bytes.readUInt16LE(pe + 24), 0x20b, "UEFI target must be PE32+");
  assert.equal(bytes.readUInt16LE(pe + 24 + 68), 10, "UEFI target must be an EFI application");
}

async function main() {
  if (!process.argv[2]) throw new Error("Provide the installed platform-targets resource directory.");
  const dataRoot = fs.mkdtempSync(path.join(os.tmpdir(), "p45-platform-smoke-"));
  const manager = createPlatformTargets({
    repositoryRoot: path.resolve(__dirname, "../../.."), dataRoot,
    bundledDirectory: path.resolve(process.argv[2])
  });
  try {
    for (const id of ["android-sdam", "android-pentacorder", "uefi-az-kernel"]) {
      const receipt = await manager.importBundled(id);
      assert.equal(receipt.source, "bundled");
      assert.equal(receipt.networkAllowed, false);
      if (id.startsWith("android-")) await verifyApk(receipt.artifactPath);
      else verifyUefi(receipt.artifactPath);
    }
    console.log("Installed platform artifacts passed copied-byte integrity and APK/UEFI structure checks; no device or firmware was modified.");
  } finally {
    await manager.close();
    fs.rmSync(dataRoot, { recursive: true, force: true });
  }
}

main().catch((error) => { console.error(error.message); process.exitCode = 1; });
