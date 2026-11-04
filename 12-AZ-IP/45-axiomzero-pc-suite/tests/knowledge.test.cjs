const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const zlib = require("node:zlib");
const {
  buildCollection,
  loadCollection,
  removeCollection,
  saveCollection,
  searchCollections,
  summarizeCollection
} = require("../lib/knowledge.cjs");

function crc32(buffer) {
  let crc = 0xFFFFFFFF;
  for (const byte of buffer) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xEDB88320 : 0);
    }
  }
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

function createZip(entries) {
  const localRecords = [];
  const centralRecords = [];
  let localOffset = 0;
  for (const entry of entries) {
    const name = Buffer.from(entry.name);
    const rawContent = Buffer.from(entry.content || "");
    const method = entry.method || 0;
    const content = method === 8 ? zlib.deflateRawSync(rawContent) : rawContent;
    const compressedSize = entry.compressedSize ?? content.length;
    const uncompressedSize = entry.uncompressedSize ?? rawContent.length;
    const checksum = crc32(rawContent);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034B50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(method, 8);
    local.writeUInt32LE(checksum, 14);
    local.writeUInt32LE(compressedSize, 18);
    local.writeUInt32LE(uncompressedSize, 22);
    local.writeUInt16LE(name.length, 26);
    localRecords.push(local, name, content);

    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014B50, 0);
    central.writeUInt16LE(0x031E, 4);
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(method, 10);
    central.writeUInt32LE(checksum, 16);
    central.writeUInt32LE(compressedSize, 20);
    central.writeUInt32LE(uncompressedSize, 24);
    central.writeUInt16LE(name.length, 28);
    central.writeUInt32LE(((entry.mode || 0o100644) << 16) >>> 0, 38);
    central.writeUInt32LE(localOffset, 42);
    centralRecords.push(central, name);
    localOffset += local.length + name.length + content.length;
  }
  const centralDirectory = Buffer.concat(centralRecords);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054B50, 0);
  end.writeUInt16LE(entries.length, 8);
  end.writeUInt16LE(entries.length, 10);
  end.writeUInt32LE(centralDirectory.length, 12);
  end.writeUInt32LE(localOffset, 16);
  return Buffer.concat([...localRecords, centralDirectory, end]);
}

function temporaryDirectory() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "az-suite-knowledge-"));
}

test("ZIP import indexes text locally and returns source-cited evidence", async () => {
  const directory = temporaryDirectory();
  const archivePath = path.join(directory, "workspace.zip");
  const archive = createZip([
    { name: "docs/guide.md", content: "first line\nPsiCat local docs\nlast line" },
    { name: "assets/logo.bin", content: Buffer.from([0, 1, 2]) },
    { name: "docs/too-large.md", content: Buffer.alloc(8 * 1024 * 1024 + 1, 0x78) },
    { name: "node_modules/ignored.js", content: "must not be indexed" },
    { name: "links/shortcut", content: "target", mode: 0o120777 }
  ]);
  fs.writeFileSync(archivePath, archive);

  try {
    const collection = await buildCollection(archivePath);
    assert.equal(collection.sourceType, "zip");
    assert.equal(collection.stats.indexedTextFiles, 1);
    assert.equal(collection.stats.unsupportedFiles, 1);
    assert.equal(collection.stats.symlinksSkipped, 1);
    assert.equal(collection.stats.excludedDirectories, 1);
    assert.equal(collection.stats.totalFiles, 3);
    assert.equal(collection.sourceSha256, crypto.createHash("sha256").update(archive).digest("hex"));

    const result = searchCollections([collection], "PsiCat local");
    assert.equal(result.totalMatches, 1);
    assert.equal(result.results[0].citation, "docs/guide.md:1-3");
    assert.match(result.results[0].excerpt, /PsiCat local docs/);
    assert.equal(result.results[0].sha256, crypto.createHash("sha256").update(
      "first line\nPsiCat local docs\nlast line"
    ).digest("hex"));
    const summary = summarizeCollection(collection);
    assert.equal(summary.sourceType, "zip");
    assert.deepEqual(summary.skippedFiles.map((file) => file.status), ["unsupported", "oversized"]);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("ZIP import rejects traversal paths and corrupt archives", async () => {
  const directory = temporaryDirectory();
  const archivePath = path.join(directory, "unsafe.zip");
  try {
    fs.writeFileSync(archivePath, createZip([
      { name: "../outside.md", content: "not safe" }
    ]));
    await assert.rejects(buildCollection(archivePath), /unsafe entry path|invalid relative path/);
    fs.writeFileSync(archivePath, "not a ZIP file");
    await assert.rejects(buildCollection(archivePath));
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("ZIP import enforces expanded-size and compression-ratio limits", async () => {
  const directory = temporaryDirectory();
  const archivePath = path.join(directory, "bounded.zip");
  try {
    fs.writeFileSync(archivePath, createZip([
      { name: "large.md", method: 8, uncompressedSize: 512 * 1024 * 1024 + 1 }
    ]));
    await assert.rejects(buildCollection(archivePath), /expands beyond/);

    fs.writeFileSync(archivePath, createZip([
      { name: "ratio.md", method: 8, content: "x", uncompressedSize: 1_000_001 }
    ]));
    const collection = await buildCollection(archivePath);
    assert.equal(collection.stats.oversizedFiles, 1);
    assert.equal(collection.files[0].status, "oversized");
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("knowledge collections persist and can be removed", async () => {
  const directory = temporaryDirectory();
  const source = path.join(directory, "source");
  const indexes = path.join(directory, "indexes");
  fs.mkdirSync(source);
  fs.writeFileSync(path.join(source, "notes.md"), "local evidence");
  try {
    const collection = await buildCollection(source);
    saveCollection(indexes, collection);
    assert.equal(loadCollection(indexes, collection.id).name, "source");
    removeCollection(indexes, collection.id);
    assert.throws(() => loadCollection(indexes, collection.id), /could not be read/);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});
