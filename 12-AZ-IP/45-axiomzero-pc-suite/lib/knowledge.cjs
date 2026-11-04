const crypto = require("node:crypto");
const fsSync = require("node:fs");
const fs = require("node:fs/promises");
const path = require("node:path");
const yauzl = require("yauzl");

const MAX_FILES = 10000;
const MAX_DEPTH = 40;
const MAX_FILE_BYTES = 8 * 1024 * 1024;
const MAX_INDEX_BYTES = 64 * 1024 * 1024;
const MAX_ARCHIVE_BYTES = 256 * 1024 * 1024;
const MAX_ARCHIVE_UNCOMPRESSED_BYTES = 512 * 1024 * 1024;
const MAX_ARCHIVE_PATH_LENGTH = 1024;
const MAX_SAVED_INDEX_BYTES = 256 * 1024 * 1024;
const MAX_COLLECTIONS = 5;
const INDEXED_EXTENSIONS = new Set([
  ".bat", ".bib", ".c", ".cjs", ".cmd", ".command", ".conf", ".cpp", ".css",
  ".csv", ".example", ".go", ".h", ".hpp", ".htm", ".html", ".ini",
  ".ipynb", ".java", ".js", ".json", ".jsonc", ".jsonl", ".jsx", ".log",
  ".md", ".mdx", ".mjs", ".php", ".ps1", ".py", ".rb", ".rs", ".rst",
  ".scss", ".sh", ".sql", ".tex", ".toml", ".ts", ".tsx", ".txt", ".xml",
  ".yaml", ".yml"
]);
const EXCLUDED_DIRECTORIES = new Set([
  ".git", ".next", ".venv", "__pycache__", "build", "coverage", "dist",
  "node_modules", "vendor", "venv"
]);
const COLLECTION_ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function isWithin(root, target) {
  const relative = path.relative(root, target);
  return relative !== ".." &&
    !relative.startsWith(`..${path.sep}`) &&
    !path.isAbsolute(relative);
}

function isExpectedReadError(error) {
  return ["EACCES", "ELOOP", "ENOENT", "EPERM"].includes(error.code);
}

function summarizeCollection(collection) {
  const skipped = collection.files.filter((file) => file.status !== "indexed");
  return {
    id: collection.id,
    name: collection.name,
    sourceType: collection.sourceType,
    createdAt: collection.createdAt,
    totalFiles: collection.stats.totalFiles,
    indexedTextFiles: collection.stats.indexedTextFiles,
    unsupportedFiles: collection.stats.unsupportedFiles,
    oversizedFiles: collection.stats.oversizedFiles,
    textLimitFiles: collection.stats.textLimitFiles,
    unreadableFiles: collection.stats.unreadableFiles,
    symlinksSkipped: collection.stats.symlinksSkipped,
    excludedDirectories: collection.stats.excludedDirectories,
    entriesVisited: collection.stats.entriesVisited,
    textBytes: collection.stats.textBytes,
    truncated: collection.stats.truncated,
    skippedFiles: skipped.slice(0, 50).map(({ path: filePath, status, sizeBytes }) => ({
      path: filePath,
      status,
      sizeBytes
    })),
    omittedSkippedFiles: Math.max(0, skipped.length - 50)
  };
}

async function buildCollection(sourceDirectory, id = crypto.randomUUID()) {
  if (!COLLECTION_ID.test(id)) {
    throw new TypeError("Knowledge collection identifier is invalid.");
  }
  const root = await fs.realpath(sourceDirectory);
  const rootStat = await fs.stat(root);
  if (rootStat.isFile() && path.extname(root).toLowerCase() === ".zip") {
    return buildZipCollection(root, id, rootStat.size);
  }
  if (!rootStat.isDirectory()) {
    throw new Error("Select a folder or ZIP containing the webspace or PsiCat files.");
  }

  const stats = {
    totalFiles: 0,
    indexedTextFiles: 0,
    unsupportedFiles: 0,
    oversizedFiles: 0,
    textLimitFiles: 0,
    unreadableFiles: 0,
    symlinksSkipped: 0,
    excludedDirectories: 0,
    entriesVisited: 0,
    textBytes: 0,
    truncated: false
  };
  const files = [];
  const pending = [{ absolute: root, relative: "", depth: 0 }];
  let pendingIndex = 0;

  while (pendingIndex < pending.length && !stats.truncated) {
    const directory = pending[pendingIndex];
    pendingIndex += 1;
    let canonicalDirectory;
    let entries;
    try {
      canonicalDirectory = await fs.realpath(directory.absolute);
      if (!isWithin(root, canonicalDirectory)) {
        stats.symlinksSkipped += 1;
        continue;
      }
      entries = await fs.readdir(canonicalDirectory, { withFileTypes: true });
    } catch (error) {
      if (!isExpectedReadError(error)) throw error;
      stats.unreadableFiles += 1;
      continue;
    }
    entries.sort((left, right) => left.name.localeCompare(right.name));

    for (const entry of entries) {
      if (stats.entriesVisited >= MAX_FILES) {
        stats.truncated = true;
        break;
      }
      stats.entriesVisited += 1;
      const absolute = path.join(canonicalDirectory, entry.name);
      const relative = path.posix.join(directory.relative, entry.name);
      let metadata;
      try {
        metadata = await fs.lstat(absolute);
      } catch (error) {
        if (!isExpectedReadError(error)) throw error;
        stats.unreadableFiles += 1;
        continue;
      }

      if (metadata.isSymbolicLink()) {
        stats.symlinksSkipped += 1;
        continue;
      }
      if (metadata.isDirectory()) {
        if (EXCLUDED_DIRECTORIES.has(entry.name.toLowerCase())) {
          stats.excludedDirectories += 1;
        } else if (directory.depth >= MAX_DEPTH) {
          stats.truncated = true;
        } else {
          pending.push({ absolute, relative, depth: directory.depth + 1 });
        }
        continue;
      }
      if (!metadata.isFile()) continue;
      if (stats.totalFiles >= MAX_FILES) {
        stats.truncated = true;
        break;
      }

      stats.totalFiles += 1;
      const extension = path.extname(entry.name).toLowerCase();
      const record = {
        path: relative,
        extension: extension || "(none)",
        sizeBytes: metadata.size,
        status: "unsupported"
      };
      files.push(record);
      if (!INDEXED_EXTENSIONS.has(extension)) {
        stats.unsupportedFiles += 1;
        continue;
      }
      if (metadata.size > MAX_FILE_BYTES) {
        record.status = "oversized";
        stats.oversizedFiles += 1;
        continue;
      }
      if (stats.textBytes + metadata.size > MAX_INDEX_BYTES) {
        record.status = "text-limit";
        stats.textLimitFiles += 1;
        continue;
      }

      try {
        const canonicalFile = await fs.realpath(absolute);
        if (!isWithin(root, canonicalFile)) {
          record.status = "symlink";
          stats.symlinksSkipped += 1;
          continue;
        }
        const contents = await fs.readFile(canonicalFile);
        indexTextRecord(record, contents, stats);
      } catch (error) {
        if (!isExpectedReadError(error)) throw error;
        record.status = "unreadable";
        stats.unreadableFiles += 1;
      }
    }
  }

  return {
    schema: "axiomzero-pc-knowledge-v1",
    id,
    name: path.basename(root) || root,
    sourceType: "folder",
    root,
    createdAt: new Date().toISOString(),
    stats,
    files
  };
}

function indexTextRecord(record, contents, stats) {
  if (contents.length > MAX_FILE_BYTES) {
    record.status = "oversized";
    stats.oversizedFiles += 1;
    return;
  }
  if (stats.textBytes + contents.length > MAX_INDEX_BYTES) {
    record.status = "text-limit";
    stats.textLimitFiles += 1;
    return;
  }
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(contents);
  } catch (error) {
    if (!(error instanceof TypeError)) throw error;
    record.status = "unsupported";
    stats.unsupportedFiles += 1;
    return;
  }
  record.status = "indexed";
  record.sha256 = crypto.createHash("sha256").update(contents).digest("hex");
  record.lines = text.replace(/^\uFEFF/, "").split(/\r\n|\n|\r/);
  stats.indexedTextFiles += 1;
  stats.textBytes += contents.length;
}

function readZipEntry(zipfile, entry) {
  return new Promise((resolve, reject) => {
    zipfile.openReadStream(entry, (error, stream) => {
      if (error) {
        reject(error);
        return;
      }
      const chunks = [];
      let bytes = 0;
      stream.on("data", (chunk) => {
        bytes += chunk.length;
        if (bytes > MAX_FILE_BYTES) {
          stream.destroy(new Error("ZIP entry exceeded the text indexing limit."));
          return;
        }
        chunks.push(chunk);
      });
      stream.on("error", reject);
      stream.on("end", () => resolve(Buffer.concat(chunks, bytes)));
    });
  });
}

function zipEntryName(name) {
  const normalized = name.replace(/\\/g, "/");
  const segments = normalized.replace(/\/$/, "").split("/");
  if (
    normalized.length > MAX_ARCHIVE_PATH_LENGTH ||
    normalized.includes("\0") ||
    normalized.startsWith("/") ||
    /^[a-z]:/i.test(normalized) ||
    segments.some((segment) => segment === ".." || segment === "." || segment === "")
  ) {
    return null;
  }
  return normalized.replace(/\/$/, "");
}

async function buildZipCollection(zipPath, id, archiveBytes) {
  if (archiveBytes > MAX_ARCHIVE_BYTES) {
    throw new Error(`ZIP file exceeds the ${MAX_ARCHIVE_BYTES / 1024 / 1024} MB import limit.`);
  }
  const stats = {
    totalFiles: 0,
    indexedTextFiles: 0,
    unsupportedFiles: 0,
    oversizedFiles: 0,
    textLimitFiles: 0,
    unreadableFiles: 0,
    symlinksSkipped: 0,
    excludedDirectories: 0,
    entriesVisited: 0,
    textBytes: 0,
    truncated: false
  };
  const files = [];
  const seen = new Set();
  const excludedDirectoryPaths = new Set();
  const archiveHash = await hashFile(zipPath, MAX_ARCHIVE_BYTES);
  const zipfile = await openZip(zipPath);
  if (zipfile.entryCount > MAX_FILES) {
    zipfile.close();
    throw new Error(`ZIP contains more than ${MAX_FILES} entries.`);
  }

  return new Promise((resolve, reject) => {
    let finished = false;
    let totalUncompressedBytes = 0;
    const fail = (error) => {
      if (finished) return;
      finished = true;
      zipfile.close();
      reject(error);
    };
    zipfile.on("error", fail);
    zipfile.on("end", () => {
      if (finished) return;
      finished = true;
      zipfile.close();
      resolve({
        schema: "axiomzero-pc-knowledge-v1",
        id,
        name: path.basename(zipPath),
        sourceType: "zip",
        root: zipPath,
        sourceSha256: archiveHash,
        createdAt: new Date().toISOString(),
        stats,
        files
      });
    });
    zipfile.on("entry", (entry) => {
      Promise.resolve().then(async () => {
        if (stats.truncated) return;
        stats.entriesVisited += 1;
        totalUncompressedBytes += entry.uncompressedSize;
        if (totalUncompressedBytes > MAX_ARCHIVE_UNCOMPRESSED_BYTES) {
          throw new Error(
            `ZIP expands beyond the ${MAX_ARCHIVE_UNCOMPRESSED_BYTES / 1024 / 1024} MB import limit.`
          );
        }
        const name = zipEntryName(entry.fileName);
        if (!name) {
          throw new Error(`ZIP contains an unsafe entry path: ${entry.fileName}`);
        }
        const mode = (entry.externalFileAttributes >>> 16) & 0xFFFF;
        const fileType = mode & 0o170000;
        if (fileType === 0o120000 || (fileType !== 0 && fileType !== 0o100000 && fileType !== 0o040000)) {
          stats.symlinksSkipped += 1;
          return;
        }
        if ((entry.generalPurposeBitFlag & 1) !== 0) {
          throw new Error(`Encrypted ZIP entries are not supported: ${name}`);
        }
        if (entry.fileName.endsWith("/") || fileType === 0o040000) {
          if (EXCLUDED_DIRECTORIES.has(path.posix.basename(name).toLowerCase())) {
            excludedDirectoryPaths.add(name.toLowerCase());
            stats.excludedDirectories = excludedDirectoryPaths.size;
          }
          return;
        }
        const pathParts = name.toLowerCase().split("/");
        const directoryParts = pathParts.slice(0, -1);
        const excludedPartIndex = directoryParts.findIndex((part) => EXCLUDED_DIRECTORIES.has(part));
        if (excludedPartIndex >= 0) {
          excludedDirectoryPaths.add(directoryParts.slice(0, excludedPartIndex + 1).join("/"));
          stats.excludedDirectories = excludedDirectoryPaths.size;
          return;
        }
        const normalizedName = name.toLowerCase();
        if (seen.has(normalizedName)) {
          stats.unreadableFiles += 1;
          return;
        }
        seen.add(normalizedName);
        if (stats.totalFiles >= MAX_FILES) {
          stats.truncated = true;
          return;
        }

        stats.totalFiles += 1;
        const record = {
          path: name,
          extension: path.posix.extname(name).toLowerCase() || "(none)",
          sizeBytes: entry.uncompressedSize,
          status: "unsupported"
        };
        files.push(record);
        if (!INDEXED_EXTENSIONS.has(record.extension)) {
          stats.unsupportedFiles += 1;
          return;
        }
        if (entry.uncompressedSize > MAX_FILE_BYTES) {
          record.status = "oversized";
          stats.oversizedFiles += 1;
          return;
        }
        if (stats.textBytes + entry.uncompressedSize > MAX_INDEX_BYTES) {
          record.status = "text-limit";
          stats.textLimitFiles += 1;
          return;
        }
        const compressionRatio = entry.uncompressedSize / Math.max(1, entry.compressedSize);
        if (compressionRatio > 1000) {
          record.status = "oversized";
          stats.oversizedFiles += 1;
          return;
        }
        const contents = await readZipEntry(zipfile, entry);
        indexTextRecord(record, contents, stats);
      }).then(
        () => {
          if (!finished) zipfile.readEntry();
        },
        fail
      );
    });
    zipfile.readEntry();
  });
}

function openZip(file) {
  return new Promise((resolve, reject) => {
    yauzl.open(
      file,
      {
        lazyEntries: true,
        autoClose: false,
        decodeStrings: true,
        validateEntrySizes: true,
        strictFileNames: true
      },
      (error, zipfile) => {
        if (error) reject(error);
        else resolve(zipfile);
      }
    );
  });
}

function hashFile(file, maxBytes) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash("sha256");
    const stream = fsSync.createReadStream(file);
    let bytes = 0;
    stream.on("error", reject);
    stream.on("data", (chunk) => {
      bytes += chunk.length;
      if (bytes > maxBytes) {
        stream.destroy(new Error(`ZIP file exceeds the ${maxBytes / 1024 / 1024} MB import limit.`));
        return;
      }
      hash.update(chunk);
    });
    stream.on("end", () => resolve(hash.digest("hex")));
  });
}

function searchCollections(collections, query, limit = 8) {
  if (typeof query !== "string" || query.trim().length === 0 || query.length > 400) {
    throw new TypeError("Enter a search question between 1 and 400 characters.");
  }
  const terms = [...new Set(query.toLowerCase().match(/[\p{L}\p{N}_-]{2,}/gu) || [])].slice(0, 16);
  if (terms.length === 0) {
    throw new TypeError("The search needs at least one word or identifier.");
  }

  const matches = [];
  for (const collection of collections) {
    for (const file of collection.files) {
      if (file.status !== "indexed") continue;
      let bestScore = 0;
      let bestLine = -1;
      for (let index = 0; index < file.lines.length; index += 1) {
        const line = file.lines[index].toLowerCase();
        let score = 0;
        for (const term of terms) {
          let occurrences = 0;
          let offset = 0;
          while (occurrences < 4) {
            offset = line.indexOf(term, offset);
            if (offset < 0) break;
            occurrences += 1;
            offset += term.length;
          }
          score += occurrences;
        }
        if (score > bestScore) {
          bestScore = score;
          bestLine = index;
        }
      }
      if (bestLine < 0) continue;

      const start = Math.max(0, bestLine - 1);
      const end = Math.min(file.lines.length - 1, bestLine + 1);
      const excerpt = file.lines
        .slice(start, end + 1)
        .map((line) => line.length > 600 ? `${line.slice(0, 600)}…` : line)
        .join("\n");
      matches.push({
        collectionName: collection.name,
        path: file.path,
        citation: `${file.path}:${start + 1}-${end + 1}`,
        sha256: file.sha256,
        score: bestScore,
        excerpt
      });
    }
  }
  matches.sort((left, right) =>
    right.score - left.score ||
    (left.path < right.path ? -1 : left.path > right.path ? 1 : 0) ||
    (left.collectionName < right.collectionName ? -1 : left.collectionName > right.collectionName ? 1 : 0)
  );
  return {
    query: query.trim(),
    terms,
    totalMatches: matches.length,
    results: matches.slice(0, limit)
  };
}

function collectionFile(directory, id) {
  if (typeof id !== "string" || !COLLECTION_ID.test(id)) {
    throw new TypeError("Knowledge collection identifier is invalid.");
  }
  return path.join(directory, `collection-${id}.json`);
}

function saveCollection(directory, collection) {
  if (!COLLECTION_ID.test(collection.id)) {
    throw new TypeError("Knowledge collection identifier is invalid.");
  }
  fsSync.mkdirSync(directory, { recursive: true });
  const file = collectionFile(directory, collection.id);
  const temporary = `${file}.tmp`;
  fsSync.writeFileSync(temporary, `${JSON.stringify(collection)}\n`, { mode: 0o600 });
  fsSync.renameSync(temporary, file);
}

function validateSavedCollection(collection, id) {
  const statuses = new Set([
    "indexed", "unsupported", "oversized", "text-limit", "unreadable", "symlink"
  ]);
  const counters = [
    "totalFiles", "indexedTextFiles", "unsupportedFiles", "oversizedFiles",
    "textLimitFiles", "unreadableFiles", "symlinksSkipped", "excludedDirectories",
    "entriesVisited", "textBytes"
  ];
  return Boolean(
    collection &&
    collection.schema === "axiomzero-pc-knowledge-v1" &&
    collection.id === id &&
    typeof collection.name === "string" &&
    typeof collection.root === "string" &&
    ["folder", "zip"].includes(collection.sourceType) &&
    typeof collection.createdAt === "string" &&
    collection.stats &&
    counters.every((key) => Number.isSafeInteger(collection.stats[key]) && collection.stats[key] >= 0) &&
    collection.stats.totalFiles <= MAX_FILES &&
    collection.stats.entriesVisited <= MAX_FILES &&
    collection.stats.textBytes <= MAX_INDEX_BYTES &&
    typeof collection.stats.truncated === "boolean" &&
    Array.isArray(collection.files) &&
    collection.files.length <= MAX_FILES &&
    collection.files.every((file) =>
      file &&
      typeof file.path === "string" &&
      file.path.length <= MAX_ARCHIVE_PATH_LENGTH &&
      !file.path.includes("\0") &&
      !path.isAbsolute(file.path) &&
      !file.path.split(/[\\/]/).includes("..") &&
      typeof file.extension === "string" &&
      Number.isSafeInteger(file.sizeBytes) &&
      file.sizeBytes >= 0 &&
      statuses.has(file.status) &&
      (file.status !== "indexed" ||
        (Array.isArray(file.lines) &&
          file.lines.every((line) => typeof line === "string") &&
          /^[0-9a-f]{64}$/i.test(file.sha256)))
    ) &&
    (collection.sourceSha256 === undefined ||
      /^[0-9a-f]{64}$/i.test(collection.sourceSha256))
  );
}

function loadCollection(directory, id) {
  const file = collectionFile(directory, id);
  let collection;
  try {
    if (fsSync.statSync(file).size > MAX_SAVED_INDEX_BYTES) {
      throw new Error(`Local knowledge index ${id} exceeds the saved-index size limit.`);
    }
    collection = JSON.parse(fsSync.readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`Local knowledge index ${id} could not be read: ${error.message}`, { cause: error });
  }
  if (!validateSavedCollection(collection, id)) {
    throw new Error(`Local knowledge index ${id} has an invalid format.`);
  }
  return collection;
}

function removeCollection(directory, id) {
  fsSync.unlinkSync(collectionFile(directory, id));
}

module.exports = {
  MAX_COLLECTIONS,
  buildCollection,
  loadCollection,
  removeCollection,
  saveCollection,
  searchCollections,
  summarizeCollection
};
