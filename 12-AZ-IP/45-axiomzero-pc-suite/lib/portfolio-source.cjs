const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { inside } = require("./runtime-manager.cjs");
const { validateCheckout } = require("./repository.cjs");

function isPortfolioSource(name) {
  const prefixes = ["12-AZ-IP/", "src/", "claims/", "recycling/", "5-GOVERNANCE/Unitary Pentad/"];
  const dependencies = ["requirements.txt", "README.md", "FALLIBILITY.md", "bot/__init__.py",
    "bot/assistant_api.py", "bot/rag_index.py", "bot/session_bootstrap.py", "bot/research_resources.py"];
  return prefixes.some((prefix) => name.startsWith(prefix)) || dependencies.includes(name);
}

function verifyFiles(root, files) {
  const seen = new Set();
  for (const file of files) {
    if (typeof file.path !== "string" || seen.has(file.path.toLowerCase()) ||
        !Number.isSafeInteger(file.bytes) || file.bytes < 0 || !/^[0-9a-f]{64}$/.test(file.sha256)) {
      throw new Error("Bundled portfolio file receipt is invalid.");
    }
    seen.add(file.path.toLowerCase());
    const content = fs.readFileSync(inside(root, file.path));
    if (content.length !== file.bytes || crypto.createHash("sha256").update(content).digest("hex") !== file.sha256) {
      throw new Error(`Bundled portfolio checksum failed: ${file.path}`);
    }
  }
}

function verifyMaterializedSource(destination, receipt, bytes) {
  const stat = fs.lstatSync(destination);
  if (!stat.isDirectory() || stat.isSymbolicLink()) throw new Error("Materialized portfolio source is not a directory.");
  if (!fs.readFileSync(path.join(destination, "SOURCE_RECEIPT.json")).equals(bytes)) {
    throw new Error("Materialized portfolio source receipt changed.");
  }
  verifyFiles(destination, receipt.files);
  return validateCheckout(destination);
}

function materializePortfolioSource(source, directory) {
  const bytes = fs.readFileSync(path.join(source, "SOURCE_RECEIPT.json"));
  const receipt = JSON.parse(bytes);
  if (receipt.schema !== "axiomzero-portfolio-source-v1" || !/^[0-9a-f]{40}$/.test(receipt.head) ||
      !Array.isArray(receipt.files) || receipt.files.length < 1 || !Array.isArray(receipt.excluded)) {
    throw new Error("Bundled portfolio source receipt is invalid.");
  }
  const identity = crypto.createHash("sha256").update(bytes).digest("hex");
  const destination = path.join(directory, identity);
  verifyFiles(source, receipt.files);
  if (fs.existsSync(destination)) return verifyMaterializedSource(destination, receipt, bytes);
  fs.mkdirSync(directory, { recursive: true });
  const pending = fs.mkdtempSync(path.join(directory, ".p45-"));
  try {
    for (const file of receipt.files) {
      const target = path.join(pending, file.path);
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.copyFileSync(inside(source, file.path), target, fs.constants.COPYFILE_EXCL);
    }
    fs.writeFileSync(path.join(pending, "SOURCE_RECEIPT.json"), bytes, { flag: "wx" });
    verifyMaterializedSource(pending, receipt, bytes);
    fs.renameSync(pending, destination);
  } catch (error) {
    fs.rmSync(pending, { recursive: true, force: true });
    if (fs.existsSync(destination)) return verifyMaterializedSource(destination, receipt, bytes);
    throw error;
  }
  return destination;
}

module.exports = { materializePortfolioSource, isPortfolioSource };
